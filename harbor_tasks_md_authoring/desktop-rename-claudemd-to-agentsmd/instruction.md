# Rename CLAUDE.md to AGENTS.md

Source: [Comfy-Org/desktop#1490](https://github.com/Comfy-Org/desktop/pull/1490)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `CLAUDE.md`
- `tests/integration/AGENTS.md`
- `tests/integration/CLAUDE.md`

## What to add / change

## Summary
- move root CLAUDE.md to AGENTS.md
- add redirect stubs in CLAUDE.md paths
- update integration docs to AGENTS.md with redirect

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
