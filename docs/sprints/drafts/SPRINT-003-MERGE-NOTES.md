# Sprint 003 Merge Notes

## Claude Draft Strengths
- Comprehensive API details table with endpoints, auth, rate limits, and params
- Clear board decision rationale (keep/add/drop/defer)
- Detailed risks & mitigations table
- BuiltIn included as a full phase (user confirmed they want it in the interview)

## Codex Draft Strengths
- BuiltIn correctly flagged as stretch/optional scope — pragmatic risk management
- Cleaner architecture diagram
- More concise overall — less noise
- Good point about consolidating dependency changes

## Valid Critiques Accepted
- **File naming inconsistency**: Claude draft uses both `themuse.py` and `the_muse.py`. Standardize on `themuse.py` (shorter, matches `wttj.py` style).
- **beautifulsoup4 listed twice**: Consolidate into a single dependency change step.
- **Per-keyword dedup in DoD**: Add explicit DoD item for per-keyword querying + cross-board dedup.
- **Testing should be generic**: Remove user-specific config reference from testing tasks.

## Critiques Rejected (with reasoning)
- **"Make BuiltIn a stretch goal"**: The user explicitly confirmed in the interview that BuiltIn should be included in this sprint. However, we'll note it should fail gracefully and not block the sprint if Cloudflare is too aggressive. We'll frame it as "included but with graceful degradation."

## Interview Refinements Applied
- Drop Underdog.io, replace with all 3 recommended boards (Himalayas, Remotive, The Muse)
- Defer Wellfound to future sprint
- Include BuiltIn (per user's explicit confirmation)
- Keep error handling simple: try-except with warning on failure, no retries

## Final Decisions
- 4 new scrapers: himalayas.py, remotive.py, themuse.py, builtin.py
- File naming: `himalayas.py`, `remotive.py`, `themuse.py`, `builtin.py` (all lowercase, no underscores)
- BuiltIn is included but with graceful failure — if Cloudflare blocks, it prints a warning and returns empty list
- beautifulsoup4 added once in Phase 2 (BuiltIn phase)
- Simple error handling throughout: try-except per board in runner, warning on failure
- Per-keyword querying + dedup is explicit in DoD
