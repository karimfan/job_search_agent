# Sprint 002 Merge Notes

## Claude Draft Strengths
- Comprehensive file listing with clear purposes
- Detailed 5-phase implementation plan
- "Second run" use case highlights dedup value proposition
- Explicit `.gitignore` inclusion

## Codex Draft Strengths
- Leaner — SQLite is explicitly optional, matching "smallest runnable slice"
- Fewer dependencies (no beautifulsoup4 since WttJ is JSON)
- Simpler architecture (no abstract base scraper / registry)
- Cleaner phase split (35/50/15 vs 20/20/20/30/10)
- Better naming convention (`config.yaml.example`)

## Valid Critiques Accepted
- **Drop beautifulsoup4**: WttJ returns JSON via Algolia — bs4 is not needed. Trim to httpx + PyYAML only.
- **Skip abstract base scraper / registry**: Premature abstraction for one scraper. A single `wttj.py` module with a `scrape()` function is enough. We can extract a base class when we add a second board.
- **Make SQLite optional**: Include it but don't make dedup part of the DoD. The "must work" path is: config -> scrape -> print. Storage is a bonus.
- **Config file naming**: Use `config.yaml.example` (Codex convention).

## Critiques Rejected (with reasoning)
- **Skip storage entirely**: Disagree. Including a simple SQLite scaffold (even optional) is low cost and prevents rewriting in the next sprint. We just won't make dedup a DoD requirement.

## Interview Refinements Applied
- Package manager: uv (reflected in pyproject.toml)
- Search criteria: keywords + location + remote flag
- No email in this sprint
- Console output only

## Final Decisions
- Include SQLite storage but mark it as optional (not in DoD)
- No abstract base scraper — just a `scrapers/wttj.py` module
- Dependencies: httpx, PyYAML only
- Use `config.yaml.example` naming
- Include `.gitignore`
- uv as package manager
