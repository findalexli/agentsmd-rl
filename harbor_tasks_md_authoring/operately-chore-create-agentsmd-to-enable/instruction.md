# chore: Create AGENTS.md to enable Codex

Source: [operately/operately#3356](https://github.com/operately/operately/pull/3356)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `turboui/AGENTS.md`
- `turboui/CLAUDE.md`

## What to add / change

Also moved content from `turboui/CLAUDE.md` to vendor neutral `turboui/AGENTS.md`.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
