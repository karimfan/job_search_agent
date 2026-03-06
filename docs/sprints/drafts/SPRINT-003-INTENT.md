# Sprint 003 Intent: Multi-Board Expansion

## Seed

"let's continue to flesh out this tool. We need to add more than just wttj. Pls add all the job boards I suggested and a few more that you can recommend"

## Context

- Sprint 001 bootstrapped the project with README and architecture docs
- Sprint 002 delivered the first runnable vertical slice: WttJ scraper via Algolia API, YAML config, console output, optional SQLite storage
- The user originally named 4 target boards: Welcome to the Jungle, BuiltIn, Wellfound, Underdog.io
- The tool currently supports only WttJ; the user wants to expand to multiple boards
- The scraper architecture is already modular: each board is a module in `scrapers/` with a `scrape(config) -> list[Job]` function, registered in `runner.py`'s `SCRAPERS` dict

## Recent Sprint Context

- **Sprint 001**: Created README.md with architecture diagram, tech stack, target boards
- **Sprint 002**: Built full vertical slice — WttJ Algolia scraper, config loader, runner, storage, CLI entry point. Bug fix for multi-keyword support (separate queries per keyword + dedup).

## Research Findings

Four parallel research agents investigated each board:

1. **BuiltIn** (builtin.com): Server-rendered HTML behind Cloudflare. No JSON API. Search via URL params (`/jobs?search=keyword&page=N`). Needs HTML parsing (BeautifulSoup). Medium difficulty — Cloudflare may intermittently block, but SSR HTML is parseable.

2. **Wellfound** (wellfound.com): Next.js app with `__NEXT_DATA__` JSON, GraphQL endpoint. Requires authentication for full access, heavy Cloudflare protection. **HARD** — fragile to maintain, likely to break.

3. **Underdog.io**: **NOT VIABLE** — this is a curated talent marketplace where candidates apply and companies reach out. No public job listings to scrape.

4. **Additional recommended boards** (all with free public JSON APIs):
   - **Himalayas.app** — `GET https://himalayas.app/jobs/api` (free, no auth, limit/offset pagination)
   - **Remotive.com** — `GET https://remotive.com/api/remote-jobs` (free, 2 req/min rate limit)
   - **The Muse** — `GET https://www.themuse.com/api/public/jobs` (free, 500 req/hr without key)

## Relevant Codebase Areas

- `job_search_agent/scrapers/wttj.py` — Reference implementation for scraper pattern
- `job_search_agent/runner.py` — `SCRAPERS` dict registry, orchestration loop
- `job_search_agent/config.py` — Config/SearchConfig dataclasses
- `job_search_agent/models.py` — Job dataclass (title, company, location, url, source, remote, posted_date)
- `config.yaml.example` — Board list config
- `README.md` — Target boards list (needs updating)

## Constraints

- Must follow existing scraper pattern: `scrape(config: Config) -> list[Job]`
- Must handle per-keyword querying with dedup (same pattern as WttJ fix)
- Must register each new scraper in `runner.py`'s `SCRAPERS` dict
- Dependencies added to `pyproject.toml`
- Underdog.io should be dropped and replaced with viable alternatives
- README.md target boards list should be updated

## Success Criteria

- At least 3 new scrapers working alongside WttJ
- User can enable any combination of boards in `config.yaml`
- Each scraper returns normalized `Job` objects
- Deduplication works across all boards (by URL)
- README updated with new board list

## Open Questions

1. Should we include BuiltIn despite Cloudflare risk, or defer it?
2. Should we attempt Wellfound despite its difficulty, or replace it entirely?
3. Should we add all 3 recommended boards (Himalayas, Remotive, The Muse) or pick a subset?
4. Do we need rate limiting/retry logic, or keep it simple for now?
