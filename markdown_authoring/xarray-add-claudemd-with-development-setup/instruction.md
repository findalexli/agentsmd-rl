# Add CLAUDE.md with development setup instructions

Source: [pydata/xarray#10692](https://github.com/pydata/xarray/pull/10692)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

## Summary
- Add CLAUDE.md file with essential development commands for xarray
- Includes setup with `uv sync`, test commands, and linting instructions

## Test plan
- [ ] `uv sync` runs successfully
- [ ] `uv run pytest xarray -n auto` executes tests
- [ ] `pre-commit run --all-files` runs linting checks
- [ ] `uv run dmypy run` performs type checking

🤖 Generated with [Claude Code](https://claude.ai/code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
