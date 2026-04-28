# Use `--only-group lint` for linting commands in `CLAUDE.md` to improve performance

Source: [mlflow/mlflow#17753](https://github.com/mlflow/mlflow/pull/17753)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

This PR updates the CLAUDE.md documentation to use `uv run --only-group lint` instead of `uv run` for all linting and code quality related commands. This change improves performance by avoiding unnecessary package builds that can slow down linting operations.

## Changes Made

Updated the following sections in CLAUDE.md:

### Code Quality Section
- `uv run ruff check . --fix` → `uv run --only-group lint ruff check . --fix`
- `uv run ruff format .` → `uv run --only-group lint ruff format .`
- `uv run clint .` → `uv run --only-group lint clint .`
- `uv run bash dev/mlflow-typo.sh .` → `uv run --only-group lint bash dev/mlflow-typo.sh .`

### Committing Changes Section
- `uv run pre-commit run --from-ref origin/master --to-ref HEAD` → `uv run --only-group lint pre-commit run --from-ref origin/master --to-ref HEAD`

### Pre-commit Hooks Section
- `uv run pre-commit install --install-hooks` → `uv run --only-group lint pre-commit install --install-hooks`
- `uv run pre-commit run --all-files` → `uv run --only-group lint pre-commit run --all-files`
- `uv run pre-commit run --files path/to/file.py` → `uv run --only-group lint pre-commit run --files path/to/file.py`
- `uv run pre-commit run ruff --all-files` → `uv run --only-group lint pre-commit run ruff --all-files`
- `uv run bin/install.py` → `uv run --only-group lint bin/install.py`

## Why This Change is Needed

The `uv run` command can be slow because it occasionally triggers package builds for dependencies. By using `--only-grou

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
