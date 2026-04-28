# minor: adding agents.md

Source: [wkaisertexas/ScreenTimeLapse#69](https://github.com/wkaisertexas/ScreenTimeLapse/pull/69)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `CLAUDE.md`

## What to add / change

Used codex to create a `Agents.md` to explain this repository and symbolically linked a Claude.md to it

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
