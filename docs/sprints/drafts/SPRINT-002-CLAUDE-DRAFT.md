# Sprint 002: First Runnable Vertical Slice

## Overview

This sprint delivers the thinnest possible vertical slice of the Job Search Agent — a runnable Python package that scrapes one job board, prints matching results to the console, and stores them in SQLite for deduplication. No email sending yet; the goal is to get something the user can actually run and see working end-to-end.

We start with one board (Welcome to the Jungle) because it has a well-structured Algolia-powered search API that returns JSON, making it the easiest to scrape reliably. The project structure, config loading, Job model, and scraper interface are all established in this sprint so that subsequent boards and email delivery can be added incrementally.

## Use Cases

1. **First run**: User creates a config file with search keywords, runs `python3 -m job_search_agent`, and sees matching job listings printed to the console.
2. **Second run**: User runs again; only new jobs (not previously seen) are printed, thanks to SQLite deduplication.
3. **Developer extension**: A developer looks at the scraper interface and config structure and understands exactly how to add a second board.

## Architecture

```
┌──────────────┐    ┌──────────┐    ┌──────────────┐    ┌──────────┐
│  __main__.py │───>│  runner   │───>│ wttj scraper │───>│  SQLite  │
│  (entry)     │    │          │    │              │    │  storage  │
└──────────────┘    └──────────┘    └──────────────┘    └──────────┘
                         │                                    │
                    ┌────┴────┐                          ┌────┴────┐
                    │  config │                          │  dedup  │
                    │  (YAML) │                          │  + log  │
                    └─────────┘                          └─────────┘
```

**Data flow**: Config loaded -> scraper fetches jobs -> storage deduplicates -> new jobs printed to console.

## Implementation Plan

### Phase 1: Project Structure (~20%)

**Files:**
- `pyproject.toml` — Project metadata and dependencies
- `job_search_agent/__init__.py` — Package init
- `job_search_agent/__main__.py` — Entry point (`python3 -m job_search_agent`)
- `config.example.yaml` — Example configuration file
- `.gitignore` — Ignore venv, db, .env, etc.

**Tasks:**
- [ ] Create `pyproject.toml` with project metadata and dependencies (httpx, pyyaml, beautifulsoup4)
- [ ] Create package directory `job_search_agent/`
- [ ] Create `__main__.py` entry point that calls the runner
- [ ] Create `config.example.yaml` with search criteria and board toggles
- [ ] Add `.gitignore` for Python project (venv, __pycache__, *.db, .env)

### Phase 2: Config & Models (~20%)

**Files:**
- `job_search_agent/config.py` — YAML config loader
- `job_search_agent/models.py` — Job dataclass

**Tasks:**
- [ ] Define `Job` dataclass (title, company, location, url, board, posted_date, scraped_at)
- [ ] Define config schema: search keywords, location, remote flag, boards to scrape
- [ ] Implement YAML config loading with sensible defaults

### Phase 3: Storage (~20%)

**Files:**
- `job_search_agent/storage.py` — SQLite storage and deduplication

**Tasks:**
- [ ] Create SQLite schema for jobs table
- [ ] Implement `save_jobs(jobs)` — inserts new jobs, skips duplicates (dedup by URL)
- [ ] Implement `get_new_jobs(jobs)` — returns only jobs not already in the database

### Phase 4: Welcome to the Jungle Scraper (~30%)

**Files:**
- `job_search_agent/scrapers/__init__.py` — Scraper registry
- `job_search_agent/scrapers/base.py` — Abstract base scraper
- `job_search_agent/scrapers/wttj.py` — Welcome to the Jungle scraper

**Tasks:**
- [ ] Define abstract base scraper with `scrape(config) -> list[Job]` interface
- [ ] Implement WTTJ scraper using their search API (Algolia-based, returns JSON)
- [ ] Parse API responses into Job objects
- [ ] Handle pagination if needed

### Phase 5: Runner & Output (~10%)

**Files:**
- `job_search_agent/runner.py` — Orchestrator

**Tasks:**
- [ ] Implement runner: load config -> run scrapers -> dedup via storage -> print new jobs
- [ ] Format console output (title, company, location, URL)
- [ ] Exit with appropriate status code (0 = success, 1 = error)

## Files Summary

| File | Action | Purpose |
|------|--------|---------|
| `pyproject.toml` | Create | Project metadata, dependencies |
| `.gitignore` | Create | Ignore generated files |
| `config.example.yaml` | Create | Example config for users |
| `job_search_agent/__init__.py` | Create | Package init |
| `job_search_agent/__main__.py` | Create | CLI entry point |
| `job_search_agent/config.py` | Create | YAML config loading |
| `job_search_agent/models.py` | Create | Job dataclass |
| `job_search_agent/storage.py` | Create | SQLite storage + dedup |
| `job_search_agent/scrapers/__init__.py` | Create | Scraper registry |
| `job_search_agent/scrapers/base.py` | Create | Abstract base scraper |
| `job_search_agent/scrapers/wttj.py` | Create | Welcome to the Jungle scraper |
| `job_search_agent/runner.py` | Create | Orchestrator |

## Definition of Done

- [ ] `python3 -m job_search_agent` runs successfully with a config file
- [ ] WTTJ scraper returns real Job objects from the API
- [ ] Jobs are stored in SQLite and deduplicated on subsequent runs
- [ ] New jobs are printed to console in a readable format
- [ ] Config file controls search keywords and location
- [ ] Base scraper interface exists for adding more boards later
- [ ] No hardcoded credentials or secrets in source

## Security Considerations

- No API keys or secrets in source code
- Config example file uses placeholder values
- SQLite DB file excluded from git via .gitignore

## Dependencies

- Sprint 001 (completed) — README and architecture

## References

- [Welcome to the Jungle](https://global.welcometothejungle.com/)
- [Welcome to the Jungle API docs](https://developers.welcometothejungle.com/) (if available)
