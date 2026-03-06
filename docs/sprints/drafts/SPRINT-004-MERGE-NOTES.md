# Sprint 004 Merge Notes

## Claude Draft Strengths
- Comprehensive phased plan with clear file-by-file breakdown
- Good risks & mitigations table
- Included documentation phase

## Codex Draft Strengths
- Keeps runner.py pure — email call in __main__.py (correct separation of concerns)
- All SMTP settings as env vars with `JSA_` namespace prefix (avoids collisions)
- Proposed `emailer.py` module name (simpler than `notifier.py`, avoids confusion with `email` stdlib)
- Cleaner EmailConfig — only `enabled`, `recipients`, `subject_prefix` in YAML (everything SMTP is env vars)
- `build_digest()` as separate function from `send_digest()` — better testability

## Valid Critiques Accepted
1. **SMTP host/port/from in config file** — Codex is right that these should be env vars, not YAML. The user confirmed "env vars only" in the interview. Moving all SMTP settings to env vars.
2. **Runner integration location** — Email should be called from `__main__.py`, not `runner.py`. Keeps runner pure and testable.
3. **File naming** — Use `emailer.py` consistently (not `notifier.py` or `email/notifier.py`). Avoids shadowing stdlib `email` module.
4. **Env var namespace** — Use `JSA_SMTP_*` prefix to avoid collisions with other tools.
5. **Plain-text vs HTML** — User said HTML in interview. Override Codex's plain-text proposal. Use HTML with plain-text fallback (multipart/alternative).

## Critiques Rejected (with reasoning)
- **"Scope creep in risks"** — SPF/DKIM mention is a reasonable documentation note, not scope creep. Keep it in README as a tip.
- **"All SMTP in env vars only"** — We'll keep `recipients` and `subject_prefix` in YAML since these aren't secrets. Only SMTP connection details go to env vars.

## Interview Refinements Applied
- **HTML format** (user chose HTML over plain text)
- **All jobs from run** (no storage dependency for email)
- **Env vars only** for SMTP credentials
- **Gmail defaults** — document Gmail-specific setup (smtp.gmail.com:587, app password)

## Final Decisions
- Module: `job_search_agent/emailer.py`
- EmailConfig in YAML: `enabled`, `recipients`, `subject_prefix` only
- All SMTP settings via env vars: `JSA_SMTP_HOST`, `JSA_SMTP_PORT`, `JSA_SMTP_USERNAME`, `JSA_SMTP_PASSWORD`, `JSA_SMTP_FROM`
- Email call in `__main__.py` after `print_jobs()`
- HTML email body with plain-text fallback (multipart/alternative)
- Gmail defaults documented in README and config.yaml.example
- Skip email if 0 jobs found
- Non-fatal on all email errors
