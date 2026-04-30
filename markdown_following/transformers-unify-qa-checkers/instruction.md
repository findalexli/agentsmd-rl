# Unify QA check calls through a single runner

## Problem

The Makefile runs dozens of individual QA check scripts with inline commands (ruff, custom Python scripts, etc.). The CI configuration (.circleci/config.yml) duplicates these same check invocations. This makes it hard to keep CI and local checks in sync — adding or changing a check requires editing multiple places.

The `make style`, `make typing`, `make check-repo`, and `make fix-repo` targets all have their own inline shell commands. There is no single source of truth for which checks run and with what arguments.

## Expected Behavior

Create a unified `utils/checkers.py` module that serves as the single entry point for running all QA checks. Each Makefile target (`style`, `typing`, `check-repo`, `fix-repo`, and two new CI-specific targets `check-code-quality` and `check-repository-consistency`) should delegate to this module instead of running individual commands.

The `checkers.py` module must:
- Export a module-level dictionary named `CHECKERS` that maps checker names to their metadata. The dict must contain exactly these 21 keys: `add_dates`, `auto_mappings`, `config_attributes`, `config_docstrings`, `copies`, `deps_table`, `doc_toc`, `docstrings`, `doctest_list`, `dummies`, `imports`, `init_isort`, `inits`, `modeling_structure`, `modular_conversion`, `pipeline_typing`, `repo`, `ruff_check`, `ruff_format`, `types`, `update_metadata`.
- Accept a `--list` flag that lists all available checker names.
- Accept a `--fix` flag to run in auto-fix mode.
- Accept a `--keep-going` flag to continue running all checkers even if some fail.
- Exit with a non-zero code and print a message containing "nknown" when given an unknown checker name.

The CI config should call the new Make targets instead of running individual scripts.

The project's `.ai/AGENTS.md` should be updated to reflect the simplified command structure — specifically, the `check-repo` description should be clarified and the outdated claim about CI behavior should be removed.

A `tomli` dependency needs to be added to support the new module.

## Files to Look At

- `Makefile` — currently has inline commands for each target; needs to be refactored to use `utils/checkers.py`
- `utils/checkers.py` — does not exist yet; needs to be created as the unified runner. Must define a `CHECKERS` dict (see Expected Behavior for required keys), and must accept `--list`, `--fix`, and `--keep-going` flags
- `.ai/AGENTS.md` — documents the QA commands; needs updating to match the new structure
- `setup.py` — needs `tomli` added to quality extras
- `src/transformers/dependency_versions_table.py` — needs `tomli` entry
- `.circleci/config.yml` — should call the new make targets instead of individual scripts
