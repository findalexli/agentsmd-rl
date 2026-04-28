# Update claude.md (vibe-kanban)

Source: [BloopAI/vibe-kanban#1484](https://github.com/BloopAI/vibe-kanban/pull/1484)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `CLAUDE.md`
- `CLAUDE.md`

## What to add / change

Update agents.md, change claude.md to be a symlink to agents.md

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
