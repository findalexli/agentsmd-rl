# feat(agents): codify peer-escalation discipline as §10 item 7 (#10385)

Source: [neomjs/neo#10386](https://github.com/neomjs/neo/pull/10386)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

Authored by Claude Opus 4.7 (Claude Code). Session aaf22f06-cc5c-4dff-aa2f-7d5efb3a6343.

## Summary

Codifies cross-family peer escalation as `AGENTS.md §10 item 7` — the missing tier between solo-loop and user-escalation in the Testing & Validation Protocol. Cultural framing front-and-center: *"Stuck is data, not failure. Asking is discipline."*

**Resolves #10385.**

## Why this exists now

Empirical anchor from this session: @neo-gemini-3-1-pro encountered a Playwright/ES-module load-order paradox while working on #10358; burned substantial turn budget on solo debugging before @tobiu externally triggered cross-family escalation. The peer (@neo-opus-4-7) provided substrate-knowledge of Neo's class system + 4 diagnostic hypotheses + bisection strategy in a single A2A response. **The substrate worked when invoked; what was missing was the discipline-layer reflex to invoke it proactively.**

@tobiu's framing this session made the cultural intent explicit: *"as a team, no one is alone, and imho we should totally leverage this more... it is a sign of strength and wisdom, not failure."* The original §10.5 / §10.6 rules were authored when Claude operated solo — before the swarm. They route directly *agent → human* and skip the *agent → cross-family-peer → human* path the swarm now enables.

## Changes (1 file, +3 / -2)

`AGENTS.md` — three coordinated edits in §10 (Testing and Validation Protocol):

### Item 5 (Productive Failure Loop) — augmented with peer-tier prefix

> *"...as

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
