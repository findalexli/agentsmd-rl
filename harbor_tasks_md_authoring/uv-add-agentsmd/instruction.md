# Add `AGENTS.md`

Source: [astral-sh/uv#18902](https://github.com/astral-sh/uv/pull/18902)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `CLAUDE.md`

## What to add / change

## Summary

Like Ruff, we now use `AGENTS.md` and tell Claude to look at that for any Claude users.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
