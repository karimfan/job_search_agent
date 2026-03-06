# Sprint 001: Project Bootstrap — README & Architecture

## Overview

This sprint establishes the foundational documentation for the Job Search Agent project. The tool will periodically scan job boards for roles matching user-defined criteria, deduplicate results, and send aggregated email digests to a configured list of recipients.

The deliverable for this sprint is a clear, concise README.md at the project root that communicates the project's purpose, high-level architecture, and chosen tech stack. No code is written in this sprint — the goal is to align on direction before implementation begins.

## Use Cases

1. **Project onboarding**: A new contributor reads the README and immediately understands what the tool does, how it's structured, and what technologies are used.
2. **Architecture alignment**: The team agrees on the tech stack and high-level design before writing code, preventing rework.
3. **Scope definition**: The README establishes clear boundaries for what the tool does and doesn't do.

## Architecture

The README will describe the following high-level architecture:

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐     ┌──────────────┐
│  Scheduler   │────▶│  Job Board   │────▶│  Storage /   │────▶│    Email     │
│  (cron)      │     │  Scrapers    │     │  Dedup       │     │  Notifier    │
└─────────────┘     └──────────────┘     └─────────────┘     └──────────────┘
                          │                     │
                    ┌─────────────────┐   ┌─────┴─────┐
                    │ Welcome to the  │   │  SQLite   │
                    │ Jungle          │   │  Database │
                    │ BuiltIn         │   └───────────┘
                    │ Wellfound       │
                    │ Underdog.io     │
                    └─────────────────┘
```

**Components:**
- **Scheduler**: Triggers scraping runs on a configured interval
- **Scrapers**: Modular scrapers per job board, each returning a common Job model
- **Storage**: SQLite database for job persistence and deduplication
- **Email Notifier**: Composes and sends digest emails with new jobs found

**Confirmed Tech Stack (for README):**
- **Language**: Python 3.11+
- **Scheduling**: cron (external) — tool runs once per invocation, exits
- **Scraping**: httpx + BeautifulSoup4 (or Playwright for JS-heavy sites)
- **Storage**: SQLite via sqlite3 stdlib
- **Email**: smtplib (stdlib) with SMTP relay
- **Config**: YAML file for search criteria, email recipients, schedule
- **Target boards**: Welcome to the Jungle, BuiltIn, Wellfound, Underdog.io

## Implementation Plan

### Phase 1: Write README.md (~90%)

**Files:**
- `README.md` — Project README at repository root

**Tasks:**
- [ ] Write project title and one-line description
- [ ] Write "Overview" section (what the tool does, in 2-3 sentences)
- [ ] Write "Architecture" section with ASCII diagram and component descriptions
- [ ] Write "Tech Stack" section listing chosen technologies with brief rationale
- [ ] Write "Getting Started" placeholder section (for future sprints)
- [ ] Write "Configuration" placeholder section (for future sprints)

### Phase 2: Sprint Housekeeping (~10%)

**Files:**
- `docs/sprints/SPRINT-001.md` — This sprint document

**Tasks:**
- [ ] Sync sprint ledger
- [ ] Mark sprint as completed once README is approved

## Files Summary

| File | Action | Purpose |
|------|--------|---------|
| `README.md` | Create | Project overview, architecture, tech stack |

## Definition of Done

- [ ] `README.md` exists at project root
- [ ] README contains: Overview, Architecture, Tech Stack sections
- [ ] Architecture section includes a clear component diagram
- [ ] Tech stack choices are documented with brief rationale
- [ ] Document is concise and simple (user's explicit requirement)
- [ ] Sprint ledger is synced

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Over-engineering the README | Medium | Low | User explicitly said "keep it very simple" — respect that |
| Wrong tech stack choices | Low | Medium | Interview user for preferences before finalizing |
| Scope creep into implementation | Low | Medium | Sprint is docs-only; implementation is a separate sprint |

## Security Considerations

- No code in this sprint, so minimal security concerns
- README should note that credentials (SMTP, API keys) will be stored in environment variables, not config files

## Dependencies

- None — this is the first sprint

## Open Questions

1. Should the README include a roadmap / future sprint hints?
