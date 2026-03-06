# Sprint 002: First Runnable Vertical Slice

## Overview

This sprint delivers the smallest runnable version of the Job Search Agent. The goal is a single command that fetches job listings from Welcome to the Jungle, normalizes them into Job objects, and prints results to the console. No email, no multi-board aggregation — just a working end-to-end path the user can run and see real output from.

We start with Welcome to the Jungle because it has an Algolia-powered search API that returns JSON, making it the most reliable board to scrape first. The project structure, config loading, and scraper module are established here so that subsequent boards, storage, and email can be added incrementally.

## Use Cases

1. **Run and see results**: User creates a config, runs `python3 -m job_search_agent`, and sees matching job listings printed to the console.
2. **Validate scraping approach**: Confirm WttJ API integration works and the Job model shape is right.
3. **Foundation for next sprints**: Project layout supports adding more scrapers, SQLite dedup, and email incrementally.

## Architecture

```
config.yaml ──> runner ──> scrapers/wttj ──> Job list ──> console output
                                │
                                v
                           (optional)
                            sqlite
```

**Components:**
- **Config** (`config.py`): Loads YAML with keywords, location, and remote flag.
- **Runner** (`runner.py`): Orchestrates config loading, scraping, and output.
- **WttJ Scraper** (`scrapers/wttj.py`): Queries the WttJ search API, returns Job objects.
- **Storage** (`storage.py`): Optional SQLite scaffold for persisting jobs. Not required for the happy path.

## Implementation Plan

### Phase 1: Project Structure + Config (~35%)

**Files:**
- `pyproject.toml` — uv project setup, dependencies (httpx, PyYAML)
- `job_search_agent/__init__.py` — Package marker
- `job_search_agent/models.py` — Job dataclass
- `job_search_agent/config.py` — YAML config loader
- `config.yaml.example` — Example configuration
- `.gitignore` — Python ignores (venv, __pycache__, *.db, .env)

**Tasks:**
- [ ] Create `pyproject.toml` with Python 3.11+ and dependencies (httpx, PyYAML)
- [ ] Create `job_search_agent/` package with `__init__.py`
- [ ] Define `Job` dataclass (title, company, location, url, source, posted_date)
- [ ] Implement YAML config loader with fields: keywords, location, remote flag
- [ ] Create `config.yaml.example` documenting all config fields
- [ ] Create `.gitignore`

### Phase 2: WttJ Scraper + Runner (~50%)

**Files:**
- `job_search_agent/scrapers/__init__.py` — Scrapers package marker
- `job_search_agent/scrapers/wttj.py` — Welcome to the Jungle scraper
- `job_search_agent/runner.py` — Orchestrator
- `job_search_agent/__main__.py` — CLI entry point

**Tasks:**
- [ ] Implement WttJ scraper: query their search API with keywords/location/remote filters
- [ ] Parse JSON responses into Job objects
- [ ] Handle pagination if the API supports it
- [ ] Implement runner: load config -> call scraper -> print results
- [ ] Format console output (title, company, location, URL per job)
- [ ] Create `__main__.py` entry point

### Phase 3: Optional SQLite Scaffold (~15%)

**Files:**
- `job_search_agent/storage.py` — SQLite setup + insert

**Tasks:**
- [ ] Create SQLite schema for jobs table
- [ ] Implement insert function (save scraped jobs)
- [ ] Wire into runner as optional step (controlled by config flag)

## Files Summary

| File | Action | Purpose |
|------|--------|---------|
| `pyproject.toml` | Create | Project metadata, uv setup, dependencies |
| `.gitignore` | Create | Ignore venv, __pycache__, *.db, .env |
| `config.yaml.example` | Create | Example config for users |
| `job_search_agent/__init__.py` | Create | Package init |
| `job_search_agent/__main__.py` | Create | CLI entry point |
| `job_search_agent/models.py` | Create | Job dataclass |
| `job_search_agent/config.py` | Create | YAML config loading |
| `job_search_agent/runner.py` | Create | Orchestrator |
| `job_search_agent/scrapers/__init__.py` | Create | Scrapers package |
| `job_search_agent/scrapers/wttj.py` | Create | Welcome to the Jungle scraper |
| `job_search_agent/storage.py` | Create | Optional SQLite scaffold |

## Definition of Done

- [ ] `python3 -m job_search_agent` runs successfully with a config file
- [ ] WttJ scraper fetches real jobs using keyword/location/remote filters
- [ ] Jobs are normalized into `Job` dataclass instances
- [ ] Results are printed to the console in a readable format
- [ ] `config.yaml.example` documents all config fields
- [ ] Project installs cleanly with `uv sync`

## Security Considerations

- No credentials or secrets committed to the repo
- `config.yaml.example` uses placeholder values only
- `.gitignore` excludes `.env` and database files

## Dependencies

- Sprint 001 (completed) — README and architecture

## References

- [Welcome to the Jungle](https://global.welcometothejungle.com/)
