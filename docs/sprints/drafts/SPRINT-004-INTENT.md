# Sprint 004 Intent: Email Digest Notifications

## Seed

"we now need to add support to sending an email to a list of participants everytime the tool runs"

## Context

- The project already planned for email from Sprint 001 — README mentions SMTP, architecture diagram includes an email component, but it was never implemented
- Currently the tool scrapes 5 boards, deduplicates, and prints results to console
- The runner returns a `list[Job]` which `__main__.py` passes to `print_jobs()`
- Config currently has search, boards, storage settings — no email section exists
- README says "SMTP credentials should be set via environment variables"

## Recent Sprint Context

- **Sprint 001**: Bootstrap — README with architecture mentioning email notifier component
- **Sprint 002**: First vertical slice — WttJ scraper, console output, config loader, optional SQLite
- **Sprint 003**: Multi-board expansion — added Himalayas, Remotive, The Muse, BuiltIn scrapers

## Relevant Codebase Areas

- `job_search_agent/__main__.py` — Entry point, calls `run()` then `print_jobs()`
- `job_search_agent/runner.py` — `run()` returns jobs, `print_jobs()` formats console output
- `job_search_agent/config.py` — `Config` and `SearchConfig` dataclasses, `load_config()`
- `job_search_agent/models.py` — `Job` dataclass
- `config.yaml.example` — Config template
- `README.md` — Already mentions SMTP and email

## Constraints

- SMTP credentials must come from environment variables, never config files
- Must use Python stdlib `smtplib` and `email` — no extra dependencies
- Email should be optional (tool still works without email config)
- Must integrate cleanly with existing runner flow
- Keep it simple — no HTML templates, just a clean plain-text digest

## Success Criteria

- User configures SMTP settings + recipient list
- After each run, an email digest of found jobs is sent to all recipients
- Email is optional — tool still prints to console without email config
- SMTP credentials are securely loaded from environment variables

## Open Questions

1. Should the email be HTML or plain text?
2. Should email only send new/unseen jobs (requires storage) or all jobs from the run?
3. Should there be a "dry run" mode that skips email?
4. Where should SMTP credentials come from — env vars only, or also support config file?
