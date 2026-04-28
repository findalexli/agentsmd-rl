# docs(CLAUDE): reference AGENTS.md and flag overlapping sections

Source: [jentic/jentic-mini#285](https://github.com/jentic/jentic-mini/pull/285)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/CLAUDE.md`

## What to add / change

## Summary
- Add a link from `.claude/CLAUDE.md` to `AGENTS.md` so contributor guidance points at the agent-facing runtime guide.
- Flag the overlapping sections between the two files (Jentic Mini overview, credential-injection flow, capability ID format, `X-Jentic-API-Key` header) so future edits keep them in sync.

Content was already aligned — no factual changes were needed, only the cross-reference and the sync reminder.

## Test plan
- [x] Docs-only change; no backend or UI tests affected.
- [x] Verified `@AGENTS.md` reference resolves (file exists at repo root).

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
