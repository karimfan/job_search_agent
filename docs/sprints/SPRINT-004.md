# Sprint 004: Email Digest Notifications

## Overview

This sprint adds email digest notifications to the Job Search Agent, completing the final major component from the original architecture. After each run, the tool composes an HTML email with all found jobs and sends it via SMTP to a configured list of recipients.

Email is optional. If the email section is not configured (or `enabled: false`), the tool behaves exactly as before — console output only. SMTP connection details and credentials are loaded exclusively from environment variables for security. Only non-secret settings (recipients, subject prefix) live in `config.yaml`.

The user chose HTML format for the email, Gmail as the SMTP provider, and environment variables only for credentials. The email sends all jobs returned by the run (not just new/unseen).

## Use Cases

1. **Daily email digest**: User schedules the tool via cron. Each morning, recipients receive an HTML email listing job matches.
2. **Team distribution**: Multiple recipients get the same digest — useful for a hiring team tracking roles.
3. **Console-only mode**: User omits the email config section and continues using the tool for console output only.

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
        +-> SMTP creds from JSA_SMTP_* env vars
```

**New component:**
- **Emailer** (`emailer.py`): Takes a list of Jobs, composes an HTML email with plain-text fallback, sends via SMTP to all configured recipients.

**Config additions (YAML):**
- `email.enabled` — toggle email on/off
- `email.recipients` — list of recipient email addresses
- `email.subject_prefix` — optional subject line prefix (default: `[Job Search Agent]`)

**Environment variables (SMTP connection):**
- `JSA_SMTP_HOST` — SMTP server hostname (e.g., `smtp.gmail.com`)
- `JSA_SMTP_PORT` — SMTP port (e.g., `587`)
- `JSA_SMTP_USERNAME` — SMTP login username
- `JSA_SMTP_PASSWORD` — SMTP login password
- `JSA_SMTP_FROM` — sender email address

## Implementation Plan

### Phase 1: Config Extension (~20%)

**Files:**
- `job_search_agent/config.py` — Add `EmailConfig` dataclass
- `config.yaml.example` — Add email section

**Tasks:**
- [ ] Add `EmailConfig` dataclass: `enabled: bool`, `recipients: list[str]`, `subject_prefix: str`
- [ ] Add `email: EmailConfig` field to `Config` dataclass
- [ ] Update `load_config()` to parse email section from YAML
- [ ] Update `config.yaml.example` with email section and env var documentation

### Phase 2: Emailer Module (~50%)

**Files:**
- `job_search_agent/emailer.py` — Email composition and SMTP sending

**Tasks:**
- [ ] Create `emailer.py` with `send_digest(jobs: list[Job], config: Config) -> bool`
- [ ] Implement `_build_html(jobs)` — HTML email body with job cards (title, company, location, remote, posted date, clickable URL)
- [ ] Implement `_build_text(jobs)` — plain-text fallback
- [ ] Compose multipart/alternative email (`EmailMessage` with HTML + text)
- [ ] Subject line: `{subject_prefix} {count} jobs found — {date}`
- [ ] Load SMTP settings from `JSA_SMTP_*` environment variables
- [ ] Connect via `smtplib.SMTP` with STARTTLS (port 587 for Gmail)
- [ ] Send to all recipients
- [ ] Return early (no email) if: email not enabled, no recipients, or 0 jobs
- [ ] Graceful error handling: print warning on any SMTP failure, return False, never crash

### Phase 3: Integration (~15%)

**Files:**
- `job_search_agent/__main__.py` — Call emailer after print_jobs()

**Tasks:**
- [ ] Import emailer in `__main__.py`
- [ ] Call `emailer.send_digest(jobs, config)` after `print_jobs(jobs)`
- [ ] Print confirmation on success, warning on failure
- [ ] `runner.py` remains unchanged (no side effects)

### Phase 4: Documentation (~15%)

**Files:**
- `README.md` — Add email configuration section

**Tasks:**
- [ ] Add "Email Notifications" section to README
- [ ] Document all `JSA_SMTP_*` environment variables
- [ ] Show Gmail-specific setup (smtp.gmail.com:587, app password requirement)
- [ ] Show example `config.yaml` email section
- [ ] Note that email is optional

## Files Summary

| File | Action | Purpose |
|------|--------|---------|
| `job_search_agent/emailer.py` | Create | HTML email composition and SMTP sending |
| `job_search_agent/config.py` | Modify | Add EmailConfig, parse email section |
| `job_search_agent/__main__.py` | Modify | Call emailer after print_jobs |
| `config.yaml.example` | Modify | Add email config section |
| `README.md` | Modify | Document email setup and env vars |

## Definition of Done

- [ ] `emailer.py` composes and sends an HTML email digest with plain-text fallback
- [ ] SMTP settings loaded exclusively from `JSA_SMTP_*` environment variables
- [ ] Non-secret email config (`enabled`, `recipients`, `subject_prefix`) in YAML
- [ ] Email sent to all configured recipients
- [ ] Empty digests (0 jobs) are not sent
- [ ] Email is optional — tool works identically without email config
- [ ] Graceful error handling on SMTP failure (warning printed, no crash)
- [ ] `config.yaml.example` includes email section with comments
- [ ] README documents email configuration and Gmail setup
- [ ] `runner.py` unchanged — email called from `__main__.py`
- [ ] `uv sync` still works (no new dependencies — stdlib only)

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| SMTP auth fails | Medium | No email sent | Clear error message; document Gmail app password requirement |
| Email marked as spam | Medium | Recipients miss digest | Document SPF/DKIM in README; recommend reputable SMTP provider |
| Missing env vars | Medium | SMTP login fails | Check for required env vars early; print specific missing var name |
| Gmail blocks "less secure" apps | Low | Auth rejected | Document that Gmail requires an App Password, not account password |

## Security Considerations

- SMTP credentials (host, port, username, password, from) NEVER in config files — only environment variables
- `.gitignore` already excludes `.env`
- `config.yaml.example` uses placeholder values only
- Always use STARTTLS for SMTP connections (never plain text)
- No logging of SMTP passwords

## Dependencies

- Sprint 003 (completed) — Multi-board scrapers, runner, config
- No new pip dependencies (uses Python stdlib `smtplib` and `email`)

## References

- [Python smtplib docs](https://docs.python.org/3/library/smtplib.html)
- [Python email.message docs](https://docs.python.org/3/library/email.message.html)
- [Gmail App Passwords](https://support.google.com/accounts/answer/185833)
