# docs(CLAUDE.md): add code review self-check section

Source: [oven-sh/bun#29063](https://github.com/oven-sh/bun/pull/29063)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

Adds a short "Code Review Self-Check" section before "Important Development Notes":

- Justify each non-obvious choice before writing it (research first, don't write-then-justify)
- Don't take a bug report's suggested fix at face value — verify the layer
- Understand *why* neighbors do what they do before deviating

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
