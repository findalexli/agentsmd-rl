# docs: add Python code formatting and linting commands to CLAUDE.md

Source: [cocoindex-io/cocoindex#1855](https://github.com/cocoindex-io/cocoindex/pull/1855)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

Fixes #1476

## Problem

CLAUDE.md currently has build and test commands but no formatting/linting instructions. This causes contributors to miss the fact that CI runs ruff format checks, leading to formatting-related CI failures.

## Solution

Add a dedicated **Code Formatting and Linting** section with the following commands:

```bash
uv run ruff format .           # Format Python code
uv run ruff format --check .   # Check formatting without making changes (same as CI)
uv run ruff check .            # Lint Python code
```

Also added a Python formatting row to the Workflow Summary table for quick reference.

## Testing

This is a documentation-only change to CLAUDE.md with no code changes.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
