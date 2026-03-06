# Sprint 001 Intent: Job Search Agent - Project Bootstrap

## Seed

We will create a new tool that will periodically scan job boards looking for roles that fit some criteria. The tool will aggregate all jobs found and send them via an email to a list of addresses. Create a README.md file that describes what we are about to do and include a high level overview + architecture and tech stack. Keep it very simple.

## Context

- Brand new project — empty repository with only sprint management infrastructure
- No existing code, no CLAUDE.md, no prior sprints
- This is Sprint 001: the project bootstrap
- Goal is to create the project README.md documenting the vision, architecture, and tech stack
- No code implementation in this sprint — just the foundational documentation

## Recent Sprint Context

No prior sprints exist. This is the first sprint for the project.

## Relevant Codebase Areas

- Project root `/` — where README.md will live
- No existing source code to integrate with
- Sprint infrastructure exists at `docs/sprints/`

## Constraints

- Keep it very simple (user's explicit instruction)
- README should cover: what the tool does, high-level architecture, tech stack
- This sprint is documentation-only — no code implementation
- Must follow sprint conventions from `docs/sprints/README.md`

## Success Criteria

- A clear, concise README.md exists at the project root
- README covers: purpose, high-level overview, architecture diagram/description, tech stack
- The document is simple and approachable — not over-engineered
- Tech stack choices are sensible for a periodic job scraping + email notification tool

## Interview Answers (from human planner)

1. **Language**: Python
2. **Job boards**: Welcome to the Jungle (global.welcometothejungle.com), BuiltIn (builtin.com), Wellfound (wellfound.com), Underdog.io (underdog.io)
3. **Scheduling**: Cron job — tool runs once per invocation and exits
4. **Email**: SMTP via smtplib
5. **Storage**: TBD (SQLite likely, for deduplication)
6. **Config format**: TBD (YAML likely)

## Remaining Open Questions

1. Storage for job deduplication? (SQLite vs flat file)
2. Configuration format for search criteria and email recipients? (YAML vs TOML vs .env)
