# Sprint 003: Multi-Board Expansion

## Overview

This sprint expands the Job Search Agent from a single-board tool (WttJ only) to a multi-board aggregator with 5 supported boards. Based on research into each board's technical feasibility, we prioritize boards with free public JSON APIs and include one HTML-scraped board (BuiltIn) that the user specifically requested.

**Board decisions:**
- **Keep**: Welcome to the Jungle (already implemented)
- **Add (JSON APIs)**: Himalayas.app, Remotive.com, The Muse
- **Add (HTML scraping)**: BuiltIn — included per user request, with graceful degradation if Cloudflare blocks
- **Drop**: Underdog.io (not a job board — curated talent marketplace, no public listings)
- **Defer**: Wellfound (heavy Cloudflare + auth requirements — future sprint candidate)

All scrapers follow the established pattern: `scrape(config: Config) -> list[Job]`, with per-keyword querying and URL-based deduplication. Error handling is simple — each board fails gracefully with a warning, never blocking the overall run.

## Use Cases

1. **Broader coverage**: User enables multiple boards and gets aggregated results from all of them in a single run.
2. **Selective scraping**: User enables/disables individual boards in `config.yaml` to control which sources are queried.
3. **Cross-board dedup**: Jobs appearing on multiple boards are deduplicated by URL.

## Architecture

```
config.yaml
   |
   v
runner -> [scrapers/wttj, scrapers/himalayas, scrapers/remotive, scrapers/themuse, scrapers/builtin]
   |
   v
dedup/storage (by URL) -> console output
```

All scrapers implement: `scrape(config: Config) -> list[Job]`

## Implementation Plan

### Phase 1: JSON API Scrapers (~50%)

Three boards with free, public JSON APIs. Lowest-risk additions.

**Files:**
- `job_search_agent/scrapers/himalayas.py` — Himalayas.app scraper
- `job_search_agent/scrapers/remotive.py` — Remotive.com scraper
- `job_search_agent/scrapers/themuse.py` — The Muse scraper

**Tasks:**
- [ ] Implement Himalayas scraper (`GET https://himalayas.app/jobs/api` with keyword + limit/offset pagination)
- [ ] Implement Remotive scraper (`GET https://remotive.com/api/remote-jobs` with search param)
- [ ] Implement The Muse scraper (`GET https://www.themuse.com/api/public/jobs` with page + category params)
- [ ] Each scraper: per-keyword querying, URL dedup, normalize to Job model
- [ ] Simple error handling: try-except with warning on failure, return empty list

**API Details:**

| Board | Endpoint | Auth | Rate Limit | Key Params |
|-------|----------|------|------------|------------|
| Himalayas | `GET /jobs/api` | None | None known | `limit`, `offset`, `q` |
| Remotive | `GET /api/remote-jobs` | None | 2 req/min | `search`, `limit` |
| The Muse | `GET /api/public/jobs` | None | 500 req/hr | `page`, `category`, `location` |

### Phase 2: BuiltIn HTML Scraper (~25%)

BuiltIn has no public API — requires HTML parsing. Behind Cloudflare but serves server-rendered HTML. Included per user request with graceful degradation.

**Files:**
- `job_search_agent/scrapers/builtin.py` — BuiltIn scraper

**Tasks:**
- [ ] Implement BuiltIn scraper: fetch `https://builtin.com/jobs?search=keyword&page=N`
- [ ] Parse job listings from HTML using BeautifulSoup
- [ ] Extract: title, company, location, URL, remote status
- [ ] Handle pagination (increment page until no results)
- [ ] Add `beautifulsoup4` to `pyproject.toml` dependencies
- [ ] Realistic User-Agent header; fail gracefully on Cloudflare blocks

### Phase 3: Registration & Config (~20%)

**Files:**
- `job_search_agent/runner.py` — Register new scrapers
- `config.yaml.example` — Update board list
- `README.md` — Update target boards section

**Tasks:**
- [ ] Register all 4 new scrapers in `runner.py`'s `SCRAPERS` dict
- [ ] Update `config.yaml.example` with all 5 available boards and comments
- [ ] Update README.md: replace Underdog.io/Wellfound with new boards, note Wellfound deferred

### Phase 4: Validation (~5%)

**Tasks:**
- [ ] Run tool with all boards enabled, verify output
- [ ] Verify cross-board dedup works
- [ ] Confirm graceful failure when a board is unreachable

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `https://himalayas.app/jobs/api` | GET | Public job listings (JSON, paginated) |
| `https://remotive.com/api/remote-jobs` | GET | Public remote jobs (JSON) |
| `https://www.themuse.com/api/public/jobs` | GET | Public jobs (JSON, paginated) |
| `https://builtin.com/jobs` | GET | Job listings (HTML, server-rendered) |

## Files Summary

| File | Action | Purpose |
|------|--------|---------|
| `job_search_agent/scrapers/himalayas.py` | Create | Himalayas.app JSON API scraper |
| `job_search_agent/scrapers/remotive.py` | Create | Remotive.com JSON API scraper |
| `job_search_agent/scrapers/themuse.py` | Create | The Muse JSON API scraper |
| `job_search_agent/scrapers/builtin.py` | Create | BuiltIn HTML scraper |
| `job_search_agent/runner.py` | Modify | Register 4 new scrapers |
| `pyproject.toml` | Modify | Add beautifulsoup4 dependency |
| `config.yaml.example` | Modify | List all 5 available boards |
| `README.md` | Modify | Update target boards section |

## Definition of Done

- [ ] Himalayas scraper fetches real jobs and returns Job objects
- [ ] Remotive scraper fetches real jobs and returns Job objects
- [ ] The Muse scraper fetches real jobs and returns Job objects
- [ ] BuiltIn scraper fetches real jobs (or degrades gracefully if Cloudflare blocks)
- [ ] All scrapers use per-keyword querying with URL-based deduplication
- [ ] All scrapers registered in runner.py SCRAPERS dict
- [ ] `python3 -m job_search_agent` works with multiple boards enabled
- [ ] Cross-board URL dedup functions correctly
- [ ] `config.yaml.example` updated with all 5 boards
- [ ] README.md updated (Underdog.io removed, new boards added, Wellfound noted as deferred)
- [ ] `uv sync` installs cleanly with new dependencies

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| BuiltIn Cloudflare blocks | Medium | Scraper returns 0 results | Realistic User-Agent; graceful failure; user can disable board |
| Remotive rate limit (2 req/min) | Low | Slow with many keywords | Keep keyword count reasonable; warn in config comments |
| API response format changes | Low | Individual scraper breaks | Each scraper isolated; one breaking doesn't affect others |
| API endpoints deprecated | Low | Scraper stops working | Easy to detect (HTTP errors); can be disabled individually |

## Security Considerations

- No API keys or secrets stored in code (all APIs are public/free)
- User-Agent header for BuiltIn is realistic but not deceptive
- No credentials committed to repo
- Respect rate limits for public APIs

## Dependencies

- Sprint 002 (completed) — WttJ scraper, project structure, config, runner
- External: `beautifulsoup4` (new dependency for BuiltIn HTML parsing)

## References

- [Himalayas.app API](https://himalayas.app/jobs/api)
- [Remotive API](https://remotive.com/api/remote-jobs)
- [The Muse API](https://www.themuse.com/api/public/jobs)
- [BuiltIn Jobs](https://builtin.com/jobs)
