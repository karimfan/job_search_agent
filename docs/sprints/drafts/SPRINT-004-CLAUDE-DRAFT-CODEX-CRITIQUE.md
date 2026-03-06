# Critique: SPRINT-004-CLAUDE-DRAFT.md (Codex)

## Summary

Strong overall structure and aligns with the sprint template, but it conflicts with the stated constraint that SMTP credentials must come from environment variables only and should not be placed in config. It also places email sending inside `runner.py`, which makes the runner impure and diverges from existing flow where `__main__.py` handles output. A few config decisions are inconsistent with the README and sprint intent.

## Strengths

- Clear overview and use cases aligned with the seed intent.
- Keeps email optional and non-fatal, which matches constraints.
- Phased plan is practical and includes documentation updates.
- Defines a concise Definition of Done and risks/mitigations.

## Issues / Conflicts

1. **SMTP credentials in config**
   - The draft proposes `email.smtp_host`, `email.smtp_port`, and `email.from_address` in YAML, plus env vars for username/password.
   - The sprint intent explicitly says SMTP credentials must come from env vars only and README already says SMTP credentials should be env vars. Host/port/from are arguably part of SMTP config; putting them in YAML weakens the security posture and conflicts with the intent. If any SMTP connection data must be in YAML, this needs to be explicitly justified or revised so *all* SMTP settings are env vars.

2. **Runner integration location**
   - It moves the email send into `runner.py` and keeps `__main__.py` unchanged.
   - Current flow is `__main__.py` calling `run()` then `print_jobs()`. Keeping runner pure is cleaner and matches existing design. Introducing side effects in `run()` makes testing and reuse harder. The draft should instead call notifier after `run()` in `__main__.py`.

3. **File naming / module path**
   - Draft uses `email/notifier.py` in architecture but then lists `job_search_agent/notifier.py`. There is no `email/` package currently. The path should be consistent and follow existing module structure.

4. **Env var naming mismatch with README intent**
   - Draft uses generic `SMTP_USERNAME` / `SMTP_PASSWORD`. The repo has no established naming but it should be namespaced (e.g., `JSA_SMTP_*`) to avoid collisions, and consistent across README/config.

5. **Potential scope creep in risks**
   - Mentions SPF/DKIM setup, truncation of large job lists, and `.env` in `.gitignore` (not verified). These are reasonable but add extra surface area not in the intent and might distract from a “keep it simple” sprint.

## Missing or Under-specified

- **Plain-text format details**: It says “one section per job” but does not define exact fields (remote, posted_date). The intent wants a clean plain-text digest; we should specify the exact format to avoid ambiguity.
- **Behavior with storage**: If storage is enabled, `run()` returns only new jobs; if disabled, it returns all. The draft doesn’t highlight this important default behavior.
- **Explicit optionality**: It says skip silently if no jobs found; should confirm whether “no email” on empty results is desired or configurable.

## Recommended Adjustments

- Move all SMTP connection details to env vars, including host/port/from/tls flags.
- Keep `runner.py` unchanged; call email sending in `__main__.py` after `run()` and after `print_jobs()`.
- Use a new module like `job_search_agent/emailer.py` (consistent with existing code style).
- Specify a minimal, deterministic plain-text digest format.
- Clarify that with storage enabled, only new jobs are emailed; otherwise all jobs returned are emailed.

## Open Questions to Resolve

1. Should SMTP host/port/from be required env vars (preferred) or allowed in YAML? (Intent suggests env-only.)
2. Should we send email when there are zero jobs, or skip by default? (Draft assumes skip.)
