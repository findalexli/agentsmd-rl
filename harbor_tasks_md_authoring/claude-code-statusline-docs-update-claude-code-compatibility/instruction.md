# docs: update Claude Code compatibility to v2.1.19

Source: [rz1989s/claude-code-statusline#232](https://github.com/rz1989s/claude-code-statusline/pull/232)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

Sync main branch with latest compatibility update.

- Updates Claude Code version compatibility range to v2.1.6–v2.1.19

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
