# Update directory of AGENTS.md

Source: [base/docs#1160](https://github.com/base/docs/pull/1160)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `docs/AGENTS.md`

## What to add / change

**What changed? Why?**

AGENTS.md should live under `docs/` to be discoverable under docs.base.org/AGENTS.md

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
