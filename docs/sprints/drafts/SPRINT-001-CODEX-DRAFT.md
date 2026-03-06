# Sprint 001: Project Bootstrap — README

## Overview

This sprint creates the first project documentation for the Job Search Agent. The tool will periodically scan selected job boards for roles that match user-defined criteria, deduplicate results, and email a digest to a configured list of recipients.

The only deliverable is a simple, clear `README.md` at the project root that explains the project purpose, high-level architecture, and the intended tech stack. No implementation work is included in this sprint.

## Use Cases

1. **Quick onboarding**: A new contributor can understand what the tool does in a few minutes.
2. **Alignment on direction**: The README anchors the team on architecture and stack choices before code starts.
3. **Scope clarity**: The README sets expectations that this sprint is documentation-only.

## Architecture

The README will include a lightweight diagram and a short component description. Example diagram:

```
[cron]
  |
  v
[runner] -> [scrapers] -> [dedup/storage] -> [email notifier]
              |               |
              v               v
     WttJ / BuiltIn /  SQLite (likely)
     Wellfound / Underdog
```

**Components:**
- **Scheduler (cron)**: Triggers the tool periodically; each run exits when done.
- **Runner**: Orchestrates config loading, scraping, dedup, and email sending.
- **Scrapers**: One per job board, normalized into a shared Job model.
- **Storage/Dedup**: Likely SQLite for persistence and avoiding repeats.
- **Email Notifier**: Sends a digest of newly found roles via SMTP.

## Implementation Plan

### Phase 1: Draft README.md (~90%)

**Files:**
- `README.md` — Project documentation at repo root

**Tasks:**
- [ ] Title + one-line summary
- [ ] Overview section (2-3 sentences)
- [ ] Architecture section with ASCII diagram + component bullets
- [ ] Tech Stack section with brief justifications
- [ ] Configuration section (short, placeholders for details)
- [ ] Running/Scheduling section (cron invocation note)

### Phase 2: Sprint Admin (~10%)

**Files:**
- `docs/sprints/SPRINT-001.md` — Sprint document

**Tasks:**
- [ ] Sync sprint ledger after creating sprint doc
- [ ] Mark sprint complete after README review

## API Endpoints

None (documentation-only sprint)

## Files Summary

| File | Action | Purpose |
|------|--------|---------|
| `README.md` | Create | Project purpose, architecture, and tech stack |

## Definition of Done

- [ ] `README.md` exists at project root
- [ ] README contains: Overview, Architecture, Tech Stack
- [ ] README mentions target job boards
- [ ] README notes cron scheduling (run once per invocation)
- [ ] README keeps language simple and concise
- [ ] No code implementation added in this sprint

## Security Considerations

- Note in README that credentials (SMTP, API keys) should not be committed
- Mention environment variables or secrets store as future approach

## Dependencies

- None (first sprint)

## References

- Job boards: Welcome to the Jungle, BuiltIn, Wellfound, Underdog.io
