# Unify QA check/fix calls through a single orchestrator

## Problem

The repository's QA pipeline is fragmented: the `Makefile` directly invokes `ruff`, individual `utils/check_*.py` scripts, and various `python -m` commands. The CI configuration (`.circleci/config.yml`) duplicates the same list of individual script calls. This makes it hard to add, remove, or reorder checks — every change requires updates in multiple places.

## Goal

Create a unified Python module (`utils/checkers.py`) that wraps and orchestrates all QA check/fix scripts. Each checker should be registered by name (e.g., `ruff_check`, `copies`, `types`, `deps_table`) so the Makefile and CI can invoke groups of checks with a single command.

The module should support:
- Running named checkers: `python utils/checkers.py copies,doc_toc`
- A `--fix` flag for fixable checkers
- A `--keep-going` flag to continue past failures
- A `--list` flag to show available checkers
- Running all checkers: `python utils/checkers.py all`

## Changes needed

1. **`utils/checkers.py`** (new): The unified check runner. It should know about all existing check scripts (`check_copies.py`, `check_modular_conversion.py`, `check_doc_toc.py`, `check_docstrings.py`, `check_dummies.py`, `check_repo.py`, `check_inits.py`, `check_pipeline_typing.py`, `check_config_docstrings.py`, `check_config_attributes.py`, `check_doctest_list.py`, `check_types.py`, `check_modeling_structure.py`, `custom_init_isort.py`, `sort_auto_mappings.py`, `update_metadata.py`, `add_dates.py`), plus custom runners for `ruff check/format`, `deps_table` (via `setup.py deps_table_update`), and public `imports` (via `from transformers import *`).

2. **`Makefile`**: Rewrite `style`, `typing`, `check-repo`, and `fix-repo` targets to delegate to `utils/checkers.py`. Add two new targets: `check-code-quality` (typing + ruff + init ordering) and `check-repository-consistency` (all repo consistency checks). The `checkers.py` module needs `tomli` for reading the TOML config, so add it as a dependency.

3. **`.circleci/config.yml`**: Replace the inline lists of individual script calls with `make check-code-quality` and `make check-repository-consistency`.

4. **`docker/quality.dockerfile`**: Ensure `make` is installed.

5. **`setup.py`** and **`src/transformers/dependency_versions_table.py`**: Add `tomli` to the dependency list and quality extras.

6. **`.ai/AGENTS.md`**: Update the "Useful commands" section to accurately describe what `make check-repo` does now. Remove any statement that implies CI runs `make check-repo` directly, since CI now uses the more specific `check-code-quality` and `check-repository-consistency` targets.

## Files to look at

- `Makefile` — current scattered QA targets
- `.circleci/config.yml` — current CI check scripts
- `utils/` — existing `check_*.py` scripts to wrap
- `.ai/AGENTS.md` — agent instructions describing make commands
