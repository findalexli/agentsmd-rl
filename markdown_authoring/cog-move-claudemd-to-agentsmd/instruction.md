# Move CLAUDE.md to AGENTS.md

Source: [replicate/cog#2575](https://github.com/replicate/cog/pull/2575)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `CLAUDE.md`
- `CLAUDE.md`

## What to add / change

1. Move CLAUDE.md to AGENTS.md
2. update contents
3. symlink CLAUDE.md -> AGENTS.md to preserve CC behavior (grrr)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
