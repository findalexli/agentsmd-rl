# docs: Expand CLAUDE.md with cross-context and cache guidelines

Source: [Mng-dev-ai/agentrove#553](https://github.com/Mng-dev-ai/agentrove/pull/553)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

## Summary
- Add rules for routing cross-context events (SSE, WebSocket, pub/sub) by event identifiers to prevent off-screen misdirection
- Add guidance on capturing entity metadata at session creation for terminal/completion handlers
- Add rule on optimistic cache patching for off-screen entities
- Clarify that terminal-kind gating applies only to UI notifications, not cache invalidations
- Add useEffect rule for keyed pending state derived from input comparison

## Test plan
- [ ] Verify no markdown rendering issues in CLAUDE.md

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
