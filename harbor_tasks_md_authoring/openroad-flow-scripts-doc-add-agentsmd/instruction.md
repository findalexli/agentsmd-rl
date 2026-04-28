# doc: Add `AGENTS.md`

Source: [The-OpenROAD-Project/OpenROAD-flow-scripts#4193](https://github.com/The-OpenROAD-Project/OpenROAD-flow-scripts/pull/4193)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `CLAUDE.md`

## What to add / change

Created `AGENTS.md` for ORFS.
- Improves AI agent discoverability by creating `AGENTS.md` and adding a pointer in `tools/OpenROAD/AGENTS.md`.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
