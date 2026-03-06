# Sprint 004: Email Digest Notifications

## Overview

This sprint adds the long-planned email digest capability to the Job Search Agent. After each run, the tool will optionally send a plain-text summary of found jobs to a configured list of recipients. Email delivery uses Python’s standard library (`smtplib` + `email`), with SMTP credentials loaded exclusively from environment variables for safety.

The existing flow already returns a `list[Job]` from `runner.run()` and prints it to console. We will integrate email at the end of that flow in `__main__.py`, so the tool still works without email configuration and still prints the same console output.

## Use Cases

1. **Daily digest**: User runs the tool on a cron schedule and receives an email with the new jobs found that run.
2. **Optional delivery**: User wants console output only; email is disabled or missing credentials, and the tool still runs normally.
3. **Multiple recipients**: User sends results to a small list (self + partner/mentor).

## Architecture

```
config.yaml
   |
   v
runner -> [scrapers] -> dedup/storage -> jobs list
   |                                  
   +-> print_jobs() (console)
   |
   +-> emailer.send_digest(jobs, config)
        |
        +-> SMTP creds from env vars
```

## Implementation Plan

### Phase 1: Email Config + Environment Variables (~35%)

**Files:**
- `job_search_agent/config.py` — add `EmailConfig` dataclass and parsing
- `config.yaml.example` — add email section
- `README.md` — document env vars and email section

**Tasks:**
- [ ] Add `EmailConfig` to `config.py`:
  - `enabled: bool`
  - `recipients: list[str]`
  - `subject_prefix: str` (optional)
- [ ] Parse `email` section in `load_config()` with safe defaults
- [ ] Add `email:` section to `config.yaml.example` with comments
- [ ] Update README with env var names + example usage

**Proposed SMTP environment variables:**
- `JSA_SMTP_HOST`
- `JSA_SMTP_PORT`
- `JSA_SMTP_USERNAME`
- `JSA_SMTP_PASSWORD`
- `JSA_SMTP_USE_TLS` ("true"/"false")
- `JSA_SMTP_FROM` (sender email address)

### Phase 2: Email Composition + Sending (~45%)

**Files:**
- `job_search_agent/emailer.py` — new module

**Tasks:**
- [ ] Implement `build_digest(jobs, config) -> str` that returns plain-text body
- [ ] Implement `send_digest(jobs, config) -> bool`:
  - Early return `False` if `email.enabled` is false or recipients empty
  - Read SMTP env vars; if required values missing, print warning and return `False`
  - Compose `EmailMessage` with subject/body/from/to
  - Connect via `smtplib.SMTP` (or `SMTP_SSL` if TLS disabled + SSL desired)
  - Support STARTTLS when `JSA_SMTP_USE_TLS=true`
  - Send to all recipients
- [ ] Include simple formatting:
  - Header with count + timestamp
  - One block per job (title, company, location, remote, posted date, URL)
  - Footer with total count

### Phase 3: Runner Integration (~15%)

**Files:**
- `job_search_agent/__main__.py` — call emailer after `run()`
- `job_search_agent/runner.py` — no changes, keep pure

**Tasks:**
- [ ] Import and call `emailer.send_digest(jobs, config)` in `__main__.py`
- [ ] Ensure console output still occurs regardless of email status
- [ ] Add warning log for email failures (non-fatal)

### Phase 4: Validation (~5%)

**Tasks:**
- [ ] Run with `email.enabled: false` to verify no change in behavior
- [ ] Run with dummy SMTP env vars to ensure failures are graceful
- [ ] Run with a real SMTP server (if available) to confirm delivery

## Files Summary

| File | Action | Purpose |
|------|--------|---------|
| `job_search_agent/config.py` | Modify | Add `EmailConfig` and parse `email` section |
| `job_search_agent/emailer.py` | Create | Build and send plain-text digest |
| `job_search_agent/__main__.py` | Modify | Trigger email sending after run |
| `config.yaml.example` | Modify | Add email section and comments |
| `README.md` | Modify | Document email config + SMTP env vars |

## Definition of Done

- [ ] `EmailConfig` exists and `load_config()` reads `email:` from YAML
- [ ] SMTP credentials are loaded only from environment variables
- [ ] Email sending is optional and non-fatal on failure
- [ ] Digest is plain-text and includes all job fields
- [ ] `python3 -m job_search_agent` prints jobs and sends email when enabled
- [ ] `config.yaml.example` and README updated with email instructions

## Security Considerations

- SMTP credentials never appear in YAML or code; only environment variables
- No logging of SMTP passwords or full credentials
- Plain-text email only; no external templating

## Dependencies

- Sprint 002/003 (completed) — runner + scrapers + Job model
- No new third-party dependencies (stdlib only)

## Open Questions

1. Should we support sending only **new** jobs (requires storage enabled) or always send all jobs returned by the run? Default proposal: send whatever `run()` returns (new-only when storage is enabled, all jobs otherwise).
2. Should we support SSL (`SMTP_SSL`) in addition to STARTTLS? (Proposed: allow both via env var.)
3. Should there be a `send_if_empty` option to notify even when no jobs are found? (Default: no email if zero jobs.)
