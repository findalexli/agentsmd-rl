# Add clint custom linter command to CLAUDE.md Code Quality section

Source: [mlflow/mlflow#17740](https://github.com/mlflow/mlflow/pull/17740)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

This PR adds the `uv run clint .` command to the Code Quality section in CLAUDE.md to ensure developers are aware of MLflow's custom linter for code quality checks.

## Changes Made

- Added `uv run clint .` command to the Code Quality section in CLAUDE.md
- Positioned the command logically after Ruff linting commands and before typos checking
- Included descriptive comment "# Custom MLflow linting with Clint" and inline comment "# Run MLflow custom linter"
- Maintained consistent formatting with existing commands

## Context

The MLflow repository includes a custom linter called "clint" (located in `dev/clint/`) that enforces MLflow-specific rules that aren't covered by standard linters like Ruff. The clint tool is already integrated into the repository's pre-commit hooks and CI pipeline, but wasn't documented in the developer guidance file.

## Why This Change is Needed

Developers working on MLflow should be aware of all available code quality tools to ensure their contributions meet the project's standards. By documenting the clint command alongside other linting tools like Ruff and the typos checker, developers can proactively run all quality checks locally before committing their changes.

The command follows the same pattern as other tools in the section, using `uv run` for consistent dependency management and execution.

<!-- START COPILOT CODING AGENT SUFFIX -->



<!-- START COPILOT CODING AGENT TIPS -->
---

💡 You can make Copilot smarter by setting up custom instr

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
