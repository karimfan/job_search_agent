# Sprint 001: Project Bootstrap — README & Architecture

## Overview

This sprint creates the foundational documentation for the Job Search Agent project. The tool will periodically scan selected job boards for roles matching user-defined criteria, deduplicate results, and send an aggregated email digest to configured recipients.

The only deliverable is a clear, concise `README.md` at the project root covering purpose, architecture, and tech stack. No code is written in this sprint.

## Use Cases

1. **Quick onboarding**: A new contributor reads the README and immediately understands what the tool does and how it's built.
2. **Architecture alignment**: The team agrees on tech stack and design before writing code.
3. **Scope definition**: The README establishes clear boundaries for what the tool does and doesn't do.

## Architecture

The README will describe the following high-level architecture:

```
┌──────┐    ┌──────────┐    ┌─────────────┐    ┌────────────────┐
│ cron │───>│  runner   │───>│  scrapers   │───>│ dedup/storage  │───>│ email notifier │
└──────┘    └──────────┘    └─────────────┘    └────────────────┘
                                  │                    │
                            WttJ / BuiltIn /      SQLite
                            Wellfound / Underdog
```

**Components:**
- **Scheduler (cron)**: Triggers the tool periodically; each run exits when done.
- **Runner**: Orchestrates config loading, scraping, dedup, and email sending.
- **Scrapers**: One module per job board, each returning a common Job model.
- **Storage/Dedup**: SQLite for persistence and deduplication.
- **Email Notifier**: Composes and sends a digest of new jobs via SMTP.

## Implementation Plan

### Phase 1: Write README.md (~90%)

**Files:**
- `README.md` — Project documentation at repo root

**Tasks:**
- [ ] Title and one-line project summary
- [ ] Overview section (2-3 sentences on what the tool does)
- [ ] Architecture section with diagram and component descriptions
- [ ] Tech Stack section with confirmed choices
- [ ] Configuration section (brief placeholder)
- [ ] Running / Scheduling section (cron invocation note)

### Phase 2: Sprint Admin (~10%)

**Tasks:**
- [ ] Sync sprint ledger
- [ ] Mark sprint complete after README review

## Files Summary

| File | Action | Purpose |
|------|--------|---------|
| `README.md` | Create | Project overview, architecture, tech stack |

## Definition of Done

- [ ] `README.md` exists at project root
- [ ] README contains: Overview, Architecture, Tech Stack sections
- [ ] README mentions all four target job boards
- [ ] README notes cron-based scheduling (run once per invocation)
- [ ] Document is simple and concise
- [ ] Sprint ledger synced

## Security Considerations

- README should note that credentials (SMTP passwords, API keys) belong in environment variables, not in config files or source control

## Dependencies

- None (first sprint)

## References

- [Welcome to the Jungle](https://global.welcometothejungle.com/)
- [BuiltIn](https://builtin.com/)
- [Wellfound](https://wellfound.com/)
- [Underdog.io](https://underdog.io/)
