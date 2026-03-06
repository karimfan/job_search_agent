# Sprint 002 Intent: First Runnable Vertical Slice

## Seed

Read the README.md and propose a first iteration and deliverable to try out this new tool. Deliver iteratively and incrementally.

## Context

- Sprint 001 (completed) created the project README with architecture, tech stack, and target board list
- No code exists yet — this is the first implementation sprint
- User explicitly wants iterative, incremental delivery — the smallest thing they can run and try
- Architecture from README: cron -> runner -> scrapers -> storage -> email
- Tech stack: Python 3.11+, SQLite, SMTP (smtplib), YAML config, cron

## Recent Sprint Context

- **Sprint 001** (completed): Documentation-only sprint. Created README.md with project overview, architecture diagram, tech stack, and target job boards (Welcome to the Jungle, BuiltIn, Wellfound, Underdog.io).

## Relevant Codebase Areas

- No source code exists yet — everything needs to be created
- `README.md` — defines the architecture and tech stack to follow
- Target boards: Welcome to the Jungle, BuiltIn, Wellfound, Underdog.io

## Constraints

- Must follow architecture from README (runner, scrapers, storage, email)
- Python 3.11+, SQLite, SMTP, YAML config
- Iterative delivery — smallest runnable slice, not the full system
- Must be something the user can actually execute and see results from
- Keep it simple — this is a v0.1

## Success Criteria

- User can run a single command and see job listings scraped from at least one board
- Project structure is established (package layout, config, etc.)
- The scraper returns structured Job objects
- Results are visible (printed to console at minimum, optionally stored in SQLite)
- Foundation is in place to add more boards and email in subsequent sprints

## Interview Answers

1. **Starting board**: Welcome to the Jungle (Algolia-powered search API, returns JSON — easiest to scrape reliably)
2. **Email**: Console only for this sprint — no SMTP. Add email in a follow-up sprint.
3. **Package manager**: uv
4. **Search criteria**: Keywords + location + remote flag

## Remaining Open Questions

None — scope is clear.
