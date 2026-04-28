# 🐝 Symlink CLAUDE.md to AGENTS.md

Source: [owid/etl#5059](https://github.com/owid/etl/pull/5059)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `CLAUDE.md`

## What to add / change

Symlink `CLAUDE.md -> AGENTS.md` to have the same source of instructions for both claude and codex.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
