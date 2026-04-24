# Add a mypy-primer project setup script for ty ecosystem reproduction

## Problem

When investigating ty ecosystem CI regressions, developers must manually clone mypy-primer projects, figure out the right revision, create a virtualenv, and install dependencies — often getting it wrong on the first try (missing deps, wrong commit, etc.). There's no streamlined way to reproduce ecosystem check results locally.

## What's Needed

Create a Python script at `scripts/setup_primer_project.py` that automates this workflow:
1. Look up a project by name from the mypy-primer project registry
2. Clone the project to a specified directory (respecting pinned revisions)
3. Create a `.venv` and install the project's dependencies

The script must:
- Expose a `main()` function with at least 3 substantive statements (argument parsing, project lookup, and orchestration logic)
- Expose a `find_project()` function at the module level that takes a project name string and returns the corresponding project object from the mypy_primer registry
- Accept a `--help` flag that displays usage information including a 'project' argument description
- Exit with a non-zero status and print "not found" to stderr when given an unknown project name
- Be runnable via `uv run scripts/setup_primer_project.py <project-name> <directory>`

The script should use the `mypy-primer` package to access the project registry (specifically `get_projects()` from `mypy_primer.projects`).

Don't forget to:
- Add `mypy-primer` as a dependency in `scripts/pyproject.toml` with a git source pointing to `hauntsaninja/mypy_primer` (configure under `[tool.uv.sources]` with `git = "https://github.com/hauntsaninja/mypy_primer"`)
- Update the project's agent instructions (`CLAUDE.md`) to document this new workflow so that AI assistants know to use this script when asked to reproduce ty ecosystem changes. The CLAUDE.md update must:
  - Include an "ecosystem" section
  - Reference the literal string `setup_primer_project`
  - Show the exact command `uv run scripts/setup_primer_project.py`

## Files to Look At

- `scripts/` — existing scripts directory with its own `pyproject.toml`
- `CLAUDE.md` — project-level agent instructions (see existing sections for style)

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `typos (spell-check)`
