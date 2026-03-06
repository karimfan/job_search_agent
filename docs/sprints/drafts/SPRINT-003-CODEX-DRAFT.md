# Sprint 003: Multi-Board Expansion

## Overview

This sprint expands Job Search Agent from a single-board scraper (Welcome to the Jungle) to a multi-board aggregator. We will add at least three additional boards with reliable public APIs, normalize them into the shared `Job` model, and ensure the user can enable any subset via config. The emphasis is pragmatic: pick boards that are technically straightforward and stable to scrape today.

We will explicitly drop Underdog.io (not a public listings board) and defer Wellfound due to heavy auth/Cloudflare complexity. BuiltIn remains a stretch goal because it is HTML + Cloudflare and may intermittently block. The core success path uses the three recommended public APIs.

## Use Cases

1. **Broader coverage**: A user turns on multiple boards and gets more results without changing code.
2. **Selective scraping**: A user enables only specific boards via `config.yaml`.
3. **Cross-board dedup**: The tool avoids duplicate postings when the same role appears on multiple boards.

## Architecture

```
config.yaml
   |
   v
runner -> [scrapers/wttj, scrapers/himalayas, scrapers/remotive, scrapers/the_muse]
   |
   v
dedup/storage (by URL) -> console output
```

**Components:**
- **Scrapers**: One module per board, each implementing `scrape(config) -> list[Job]`.
- **Runner**: Registry of boards and orchestration loop (unchanged pattern).
- **Storage**: Optional SQLite dedup (existing behavior).

## Implementation Plan

### Phase 1: New API Scrapers (~60%)

**Files:**
- `job_search_agent/scrapers/himalayas.py` - Himalayas API scraper
- `job_search_agent/scrapers/remotive.py` - Remotive API scraper
- `job_search_agent/scrapers/the_muse.py` - The Muse API scraper
- `job_search_agent/scrapers/__init__.py` - Export convenience (if used)
- `job_search_agent/runner.py` - Register new boards

**Tasks:**
- [ ] Implement Himalayas scraper using `/jobs/api` with keyword + pagination support
- [ ] Implement Remotive scraper using `/api/remote-jobs` and keyword filtering
- [ ] Implement The Muse scraper using `/api/public/jobs` with keyword + location filters
- [ ] Normalize each result into `Job` (title, company, location, url, source, remote, posted_date)
- [ ] Register new scrapers in `SCRAPERS` dict
- [ ] Ensure per-keyword querying and dedup logic mirrors WttJ approach

### Phase 2: Config + Docs Updates (~25%)

**Files:**
- `config.yaml.example` - Expand board list and notes
- `README.md` - Update target boards list

**Tasks:**
- [ ] Add new board keys to `config.yaml.example` with short comments
- [ ] Update README target board list to match the new supported set
- [ ] Note that Underdog.io is not supported and Wellfound is deferred

### Phase 3: Optional BuiltIn Spike (~15%, Stretch)

**Files:**
- `job_search_agent/scrapers/builtin.py` - HTML scraper (optional)

**Tasks:**
- [ ] If time permits, implement a minimal BuiltIn scraper via HTML parsing
- [ ] Guard against Cloudflare failures; fail gracefully
- [ ] Only include in registry if reliable enough for local testing

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `https://himalayas.app/jobs/api` | GET | Public job listings (JSON, paginated) |
| `https://remotive.com/api/remote-jobs` | GET | Public remote jobs (JSON, rate-limited) |
| `https://www.themuse.com/api/public/jobs` | GET | Public jobs (JSON, paginated) |

## Files Summary

| File | Action | Purpose |
|------|--------|---------|
| `job_search_agent/scrapers/himalayas.py` | Create | Himalayas API scraper |
| `job_search_agent/scrapers/remotive.py` | Create | Remotive API scraper |
| `job_search_agent/scrapers/the_muse.py` | Create | The Muse API scraper |
| `job_search_agent/runner.py` | Modify | Register new scrapers |
| `config.yaml.example` | Modify | New board options |
| `README.md` | Modify | Updated supported boards |
| `job_search_agent/scrapers/builtin.py` | Create | Optional BuiltIn HTML scraper |

## Definition of Done

- [ ] At least three new boards return jobs via their public JSON APIs
- [ ] User can enable any subset via `config.yaml` `boards` list
- [ ] All scrapers return normalized `Job` objects
- [ ] Deduplication works across boards by URL
- [ ] README updated with new supported boards list

## Security Considerations

- No API keys required for chosen boards; avoid storing secrets
- Respect rate limits for public APIs (especially Remotive)

## Dependencies

- Sprint 002 (runner + WttJ scraper + config system)

## References

- Himalayas public jobs API
- Remotive public jobs API
- The Muse public jobs API
