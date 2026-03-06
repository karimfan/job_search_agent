# Sprint 004: Email Digest Notifications

## Overview

This sprint adds email notification support to the Job Search Agent. After each run, the tool composes a digest of all found jobs and sends it via SMTP to a configured list of recipients. This completes the final major component from the original architecture — the tool can now scrape, deduplicate, and email results automatically.

Email is optional. If no email section is configured, the tool behaves exactly as before (console output only). SMTP credentials (username/password) are loaded from environment variables for security — they are never stored in config files.

## Use Cases

1. **Daily email digest**: User schedules the tool via cron. Each morning, recipients receive an email listing new job matches.
2. **Team distribution**: Multiple recipients get the same digest — useful for a hiring team tracking roles.
3. **Console-only mode**: User omits the email config section and continues using the tool as before.

## Architecture

```
config.yaml ──> runner ──> scrapers ──> Job list ──> console output
                                            |
                                            v
                                     email/notifier.py
                                            |
                                            v
                                     SMTP ──> recipients
```

**New component:**
- **Notifier** (`email/notifier.py`): Takes a list of Jobs, composes a plain-text email, sends via SMTP to all configured recipients.

**Config additions:**
- `email.enabled` — toggle email on/off
- `email.smtp_host` / `email.smtp_port` — SMTP server
- `email.from_address` — sender address
- `email.recipients` — list of recipient email addresses
- `email.subject_prefix` — optional subject line prefix
- Environment variables: `SMTP_USERNAME`, `SMTP_PASSWORD`

## Implementation Plan

### Phase 1: Email Notifier Module (~50%)

**Files:**
- `job_search_agent/notifier.py` — Email composition and sending

**Tasks:**
- [ ] Create `notifier.py` with `send_digest(jobs: list[Job], config: Config) -> None`
- [ ] Compose plain-text email body: subject line with job count + date, one section per job (title, company, location, URL)
- [ ] Use `smtplib.SMTP_SSL` or `smtplib.SMTP` with STARTTLS based on port (465 = SSL, else STARTTLS)
- [ ] Load SMTP username/password from `SMTP_USERNAME` and `SMTP_PASSWORD` environment variables
- [ ] Send to all recipients in `config.email.recipients`
- [ ] Skip silently if no jobs found (don't send empty digests)
- [ ] Graceful error handling: print warning on SMTP failure, don't crash the tool

### Phase 2: Config Extension (~25%)

**Files:**
- `job_search_agent/config.py` — Add `EmailConfig` dataclass and load from YAML
- `config.yaml.example` — Add email section

**Tasks:**
- [ ] Add `EmailConfig` dataclass: `enabled`, `smtp_host`, `smtp_port`, `from_address`, `recipients`, `subject_prefix`
- [ ] Add `email: EmailConfig` field to `Config` dataclass
- [ ] Update `load_config()` to parse email section from YAML
- [ ] Update `config.yaml.example` with email section and comments explaining env vars

### Phase 3: Runner Integration (~15%)

**Files:**
- `job_search_agent/runner.py` — Call notifier after scraping
- `job_search_agent/__main__.py` — No changes needed (runner handles it)

**Tasks:**
- [ ] Import notifier in runner
- [ ] After `run()` returns jobs, call `send_digest()` if `config.email.enabled`
- [ ] Print confirmation message after successful send

### Phase 4: Documentation (~10%)

**Files:**
- `README.md` — Add email configuration section

**Tasks:**
- [ ] Add "Email Notifications" section to README
- [ ] Document required environment variables (`SMTP_USERNAME`, `SMTP_PASSWORD`)
- [ ] Show example `config.yaml` email section
- [ ] Note that email is optional

## Files Summary

| File | Action | Purpose |
|------|--------|---------|
| `job_search_agent/notifier.py` | Create | Email composition and SMTP sending |
| `job_search_agent/config.py` | Modify | Add EmailConfig, parse email section |
| `job_search_agent/runner.py` | Modify | Call notifier after scraping |
| `config.yaml.example` | Modify | Add email config section |
| `README.md` | Modify | Document email setup |

## Definition of Done

- [ ] `notifier.py` composes and sends a plain-text email digest
- [ ] SMTP credentials loaded from environment variables (`SMTP_USERNAME`, `SMTP_PASSWORD`)
- [ ] Email sent to all configured recipients
- [ ] Empty digests (0 jobs) are not sent
- [ ] Email is optional — tool works without email config
- [ ] `config.yaml.example` includes email section with comments
- [ ] README documents email configuration
- [ ] Graceful error handling on SMTP failure (warning, no crash)
- [ ] `uv sync` still works (no new dependencies)

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| SMTP auth fails | Medium | No email sent | Clear error message with troubleshooting hints |
| Email marked as spam | Medium | Recipients miss digest | Document SPF/DKIM setup; use reputable SMTP provider |
| Large job lists = huge email | Low | Unreadable email | Truncate to reasonable limit (e.g. 200 jobs) |
| Missing env vars | Medium | SMTP login fails | Check for env vars early; clear error if missing |

## Security Considerations

- SMTP password NEVER stored in config files — only environment variables
- `.gitignore` already excludes `.env`
- `config.yaml.example` uses placeholder values only
- Use TLS/SSL for SMTP connections (never plain text)

## Dependencies

- Sprint 003 (completed) — Multi-board scrapers, runner, config
- No new pip dependencies (uses Python stdlib `smtplib` and `email`)

## References

- [Python smtplib docs](https://docs.python.org/3/library/smtplib.html)
- [Python email.message docs](https://docs.python.org/3/library/email.message.html)
