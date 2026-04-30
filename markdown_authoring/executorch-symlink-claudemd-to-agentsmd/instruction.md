# Symlink claude.md to agents.md

Source: [pytorch/executorch#19046](https://github.com/pytorch/executorch/pull/19046)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

Summary: Symlink agents and claude.md to work with other coding tools

Reviewed By: Gasoonjia

Differential Revision: D102001090

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
