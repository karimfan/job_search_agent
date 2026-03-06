# Sprint 002: First Runnable Vertical Slice

## Overview

This sprint delivers the smallest runnable version of Job Search Agent. The goal is a single command that fetches job listings from one board (Welcome to the Jungle) using a real API, normalizes results into a Job model, and prints them to the console. We will lay down the project structure, config loading, and a simple runner that can be extended in future sprints.

This is a deliberate v0.1: no email sending yet, no multi-board aggregation, and no complex scheduling. The focus is runnable, visible output and a clean foundation.

## Use Cases

1. **Run once and see results**: A user can execute one command and see recent jobs for their criteria.
2. **Validate scraping approach**: We confirm the WttJ JSON API integration and model shape.
3. **Foundation for expansion**: The project layout supports adding more boards and storage/email later.

## Architecture

```
[config.yaml] -> [runner] -> [scrapers.wttj] -> [Job list] -> [console output]
                                    |
                                    v
                                (optional)
                                 [sqlite]
```

**Components:**
- **Config**: YAML file with keywords, location, and remote flag.
- **Runner**: Loads config, calls the WttJ scraper, and formats output.
- **Scraper (WttJ)**: Queries the WttJ JSON API and returns Job objects.
- **Storage (optional)**: SQLite placeholder for saving jobs for future dedup.

## Implementation Plan

### Phase 1: Project Structure + Config (~35%)

**Files:**
- `job_search_agent/__init__.py` - package marker
- `job_search_agent/config.py` - config model + YAML loader
- `job_search_agent/models.py` - Job dataclass
- `config.yaml.example` - sample config
- `pyproject.toml` - uv/packaging setup

**Tasks:**
- [ ] Create package layout for `job_search_agent`
- [ ] Define a minimal `Job` dataclass (id, title, company, location, url, source)
- [ ] Implement YAML config loader with keywords, location, remote flag
- [ ] Provide a minimal `config.yaml.example`
- [ ] Add `pyproject.toml` with Python 3.11+ and dependencies (PyYAML, httpx)

### Phase 2: WttJ Scraper + Runner (~50%)

**Files:**
- `job_search_agent/scrapers/wttj.py` - WttJ API client
- `job_search_agent/runner.py` - orchestrator
- `job_search_agent/__main__.py` - CLI entrypoint

**Tasks:**
- [ ] Implement WttJ scraper against the JSON API
- [ ] Normalize results into `Job` objects
- [ ] Implement runner to load config and call scraper
- [ ] Print results to console in a readable format
- [ ] Add `python3 -m job_search_agent` entrypoint

### Phase 3: Optional SQLite Scaffold (~15%)

**Files:**
- `job_search_agent/storage.py` - SQLite setup + insert

**Tasks:**
- [ ] Add minimal SQLite schema for jobs
- [ ] Insert scraped jobs (no dedup logic yet)
- [ ] Make storage optional via config flag

## API Endpoints

None (CLI only)

## Files Summary

| File | Action | Purpose |
|------|--------|---------|
| `job_search_agent/__init__.py` | Create | Package initialization |
| `job_search_agent/__main__.py` | Create | CLI entrypoint |
| `job_search_agent/config.py` | Create | YAML config parsing |
| `job_search_agent/models.py` | Create | Job dataclass |
| `job_search_agent/runner.py` | Create | Orchestrates scraping run |
| `job_search_agent/scrapers/wttj.py` | Create | WttJ API integration |
| `job_search_agent/storage.py` | Create | Optional SQLite scaffold |
| `config.yaml.example` | Create | Example configuration |
| `pyproject.toml` | Create | uv + deps setup |

## Definition of Done

- [ ] `python3 -m job_search_agent` runs successfully
- [ ] WttJ jobs are fetched with keyword/location/remote filters
- [ ] Jobs are normalized to `Job` objects
- [ ] Results are printed to the console
- [ ] `config.yaml.example` documents expected config fields
- [ ] Basic project structure exists for adding new scrapers

## Security Considerations

- Do not store credentials in the repo; only config that is safe to commit
- No email credentials or tokens in this sprint

## Dependencies

- Sprint 001 (README/architecture)

## References

- Welcome to the Jungle job board (JSON/Algolia-powered search API)
- README architecture and tech stack
