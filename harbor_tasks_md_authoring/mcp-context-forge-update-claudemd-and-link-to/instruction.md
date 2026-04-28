# Update CLAUDE.md and link to existing documentation

Source: [IBM/mcp-context-forge#1347](https://github.com/IBM/mcp-context-forge/pull/1347)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

## Summary

- Reorganize CLAUDE.md with clearer structure and documentation quick links
- Enable flake8 and black in pre-commit hooks for consistent code quality
- Standardize use of uv environment manager across Makefile and CI
- Configure Neovim linters (flake8, pylint) for editor integration
- Fix pytest warnings configuration in test runs

## Changes

### Documentation Improvements
- Restructure CLAUDE.md with focused essential commands section
- Move detailed performance configuration to dedicated docs
- Add comprehensive documentation quick links section organized by category
- Clarify uv usage for virtual environment management

### Code Quality Tooling
- Enable flake8 pre-commit hook for style enforcement
- Enable black pre-commit hook for consistent formatting
- Remove obsolete fix-encoding-pragma hook
- Configure Neovim ALE linters: mypy, ruff, flake8, pylint

### Build System Updates
- Add `make uv` target to ensure uv is installed (brew or curl fallback)
- Update `make pylint` to use `uv run` with proper error handling
- Adjust `make test` to show warnings (remove --disable-warnings)
- Standardize pylint flags: `--fail-on E --fail-under 10`

### CI/CD Alignment
- Install uv in GitHub Actions lint workflow
- Update pylint job to use `uv run` instead of pip install
- Ensure CI matches local development environment

## Test Plan

- [x] Run `make venv install-dev` - virtual environment setup works
- [x] Run `make flake8` - linting passes
- [x] Run `make pylint` - pyli

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
