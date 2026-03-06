# Sprint 003: Multi-Board Expansion

## Overview

This sprint expands the Job Search Agent from a single-board tool (WttJ only) to a multi-board aggregator. Based on research into the originally proposed boards and additional recommendations, we add scrapers for boards with reliable, free JSON APIs and defer or replace boards that are fragile or non-viable.

**Board decisions:**
- **Keep**: Welcome to the Jungle (already implemented)
- **Add (easy — public JSON APIs)**: Himalayas.app, Remotive.com, The Muse
- **Add (medium — HTML scraping)**: BuiltIn
- **Drop**: Underdog.io (not a job board — curated talent marketplace with no public listings)
- **Defer**: Wellfound (heavy Cloudflare + auth requirements make it fragile and high-maintenance)

This gives us 5 working boards, with Wellfound as a future sprint candidate if needed. The three new JSON-API boards are low-risk and high-value, while BuiltIn covers one of the user's original requests despite requiring HTML parsing.

## Use Cases

1. **Broad job search**: User configures multiple boards and gets aggregated results from all of them in a single run.
2. **Board selection**: User enables/disables individual boards in `config.yaml` to control which sources are queried.
3. **Cross-board dedup**: Jobs that appear on multiple boards are deduplicated by URL, preventing duplicate listings.

## Architecture

```
config.yaml ──> runner ──> ┬── scrapers/wttj.py       (Algolia JSON API)
                           ├── scrapers/himalayas.py   (REST JSON API)
                           ├── scrapers/remotive.py    (REST JSON API)
                           ├── scrapers/themuse.py     (REST JSON API)
                           └── scrapers/builtin.py     (HTML scraping)
                                      │
                                      v
                               Job list ──> console / sqlite
```

All scrapers follow the same interface: `scrape(config: Config) -> list[Job]`

## Implementation Plan

### Phase 1: JSON API Scrapers (~50%)

These three boards have free, public JSON APIs with no authentication required. They are the lowest-risk additions.

**Files:**
- `job_search_agent/scrapers/himalayas.py` — Himalayas.app scraper
- `job_search_agent/scrapers/remotive.py` — Remotive.com scraper
- `job_search_agent/scrapers/themuse.py` — The Muse scraper

**Tasks:**
- [ ] Implement Himalayas scraper (`GET https://himalayas.app/jobs/api` with limit/offset pagination, keyword filtering)
- [ ] Implement Remotive scraper (`GET https://remotive.com/api/remote-jobs` with search param, respect 2 req/min rate limit)
- [ ] Implement The Muse scraper (`GET https://www.themuse.com/api/public/jobs` with page param, category/location filters)
- [ ] Each scraper: per-keyword querying, URL dedup, normalize to Job model

**API Details:**

| Board | Endpoint | Auth | Rate Limit | Params |
|-------|----------|------|------------|--------|
| Himalayas | `GET /jobs/api` | None | None known | `limit`, `offset`, `q` (keyword) |
| Remotive | `GET /api/remote-jobs` | None | 2 req/min | `search` (keyword), `limit` |
| The Muse | `GET /api/public/jobs` | None (optional key) | 500 req/hr | `page`, `category`, `location`, `company` |

### Phase 2: BuiltIn HTML Scraper (~30%)

BuiltIn requires HTML parsing since it has no public API. It's behind Cloudflare but serves server-rendered HTML that's parseable.

**Files:**
- `job_search_agent/scrapers/builtin.py` — BuiltIn scraper

**Tasks:**
- [ ] Implement BuiltIn scraper: fetch `https://builtin.com/jobs?search=keyword&page=N`
- [ ] Parse job listings from HTML using BeautifulSoup
- [ ] Extract: title, company, location, URL, remote status
- [ ] Handle pagination (increment page until no results)
- [ ] Add `beautifulsoup4` to `pyproject.toml` dependencies
- [ ] Add realistic User-Agent header to avoid Cloudflare blocks

### Phase 3: Registration & Config (~15%)

**Files:**
- `job_search_agent/runner.py` — Register new scrapers
- `config.yaml.example` — Update board list
- `README.md` — Update target boards section

**Tasks:**
- [ ] Register all new scrapers in `runner.py`'s `SCRAPERS` dict
- [ ] Update `config.yaml.example` with all available boards
- [ ] Update README.md target boards list (replace Underdog.io and Wellfound with new boards)
- [ ] Add `beautifulsoup4` dependency to `pyproject.toml`

### Phase 4: Testing & Validation (~5%)

**Tasks:**
- [ ] Run tool with all boards enabled, verify output
- [ ] Verify cross-board dedup works (same job from different boards)
- [ ] Test with user's current config (talent acquisition keywords, US, remote fulltime)

## Files Summary

| File | Action | Purpose |
|------|--------|---------|
| `job_search_agent/scrapers/himalayas.py` | Create | Himalayas.app JSON API scraper |
| `job_search_agent/scrapers/remotive.py` | Create | Remotive.com JSON API scraper |
| `job_search_agent/scrapers/themuse.py` | Create | The Muse JSON API scraper |
| `job_search_agent/scrapers/builtin.py` | Create | BuiltIn HTML scraper |
| `job_search_agent/runner.py` | Modify | Register 4 new scrapers |
| `pyproject.toml` | Modify | Add beautifulsoup4 dependency |
| `config.yaml.example` | Modify | List all available boards |
| `README.md` | Modify | Update target boards section |

## Definition of Done

- [ ] Himalayas scraper fetches real jobs and returns Job objects
- [ ] Remotive scraper fetches real jobs and returns Job objects
- [ ] The Muse scraper fetches real jobs and returns Job objects
- [ ] BuiltIn scraper fetches real jobs and returns Job objects
- [ ] All scrapers registered in runner.py
- [ ] `python3 -m job_search_agent` works with multiple boards enabled
- [ ] Cross-board URL dedup functions correctly
- [ ] `config.yaml.example` updated with all boards
- [ ] README.md updated (Underdog.io removed, new boards added)
- [ ] `uv sync` installs cleanly with new dependencies

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| BuiltIn Cloudflare blocks | Medium | Scraper returns 0 results | Realistic User-Agent header; graceful error handling; user can disable board |
| Remotive rate limit (2 req/min) | Low | Slow with many keywords | Small delay between requests; warn in config comments |
| API response format changes | Low | Scraper breaks | Each scraper is isolated; one breaking doesn't affect others |
| Wellfound users miss it | Low | Fewer results | Can be added in future sprint if demand exists |

## Security Considerations

- No API keys or secrets stored in code (all APIs are public/free)
- User-Agent header for BuiltIn should be realistic but not deceptive
- No credentials committed to repo

## Dependencies

- Sprint 002 (completed) — WttJ scraper, project structure, config, runner
- External: beautifulsoup4 (new pip dependency for BuiltIn HTML parsing)

## References

- [Himalayas.app API](https://himalayas.app/jobs/api)
- [Remotive API](https://remotive.com/api/remote-jobs)
- [The Muse API](https://www.themuse.com/api/public/jobs)
- [BuiltIn Jobs](https://builtin.com/jobs)
