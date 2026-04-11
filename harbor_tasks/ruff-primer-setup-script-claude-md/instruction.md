# Add a mypy-primer project setup script for ty ecosystem reproduction

## Problem

When investigating ty ecosystem CI regressions, developers must manually clone mypy-primer projects, figure out the right revision, create a virtualenv, and install dependencies — often getting it wrong on the first try (missing deps, wrong commit, etc.). There's no streamlined way to reproduce ecosystem check results locally.

## What's Needed

Create a Python script at `scripts/setup_primer_project.py` that automates this workflow:
1. Look up a project by name from the mypy-primer project registry
2. Clone the project to a specified directory (respecting pinned revisions)
3. Create a `.venv` and install the project's dependencies

The script should use the `mypy-primer` package to access the project registry (specifically `get_projects()` from `mypy_primer.projects`). It should be runnable via `uv run scripts/setup_primer_project.py <project-name> <directory>`.

Don't forget to:
- Add `mypy-primer` as a dependency in `scripts/pyproject.toml` with a git source pointing to `hauntsaninja/mypy_primer`
- Update the project's agent instructions (`CLAUDE.md`) to document this new workflow so that AI assistants know to use this script when asked to reproduce ty ecosystem changes

## Files to Look At

- `scripts/` — existing scripts directory with its own `pyproject.toml`
- `CLAUDE.md` — project-level agent instructions (see existing sections for style)
