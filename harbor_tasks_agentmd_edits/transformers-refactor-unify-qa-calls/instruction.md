# Unify QA check/fix calls under a single runner

## Problem

The `Makefile` currently calls each QA checker script directly — `ruff check`, `ruff format`, individual `python utils/check_*.py` invocations, etc. This leads to:

- Duplicated target lists between `check-repo`, `fix-repo`, `style`, and CI configs (`.circleci/config.yml`)
- No single entry point to run a subset of checks or get unified output
- The CI config (`.circleci/config.yml`) repeats the same long list of `run:` steps instead of delegating to a Makefile target

## Expected Behavior

1. A new **`utils/checkers.py`** module should serve as a single entry point that:
   - Maintains a registry of all available checkers (mapping name → script + args)
   - Supports both check mode and fix mode (`--fix`)
   - Supports `--keep-going` to continue past failures
   - Can run custom checkers (ruff, imports, deps table) that don't follow the standard `python utils/check_*.py` pattern

2. The **`Makefile`** targets (`style`, `typing`, `check-repo`, `fix-repo`) should be refactored to call `python utils/checkers.py` with comma-separated checker names, instead of invoking scripts directly. Two new targets should be added:
   - `check-code-quality` — typing + ruff + import ordering
   - `check-repository-consistency` — all repo consistency checks

3. The **`.circleci/config.yml`** should be simplified to use the new Makefile targets (`make check-code-quality`, `make check-repository-consistency`) instead of listing individual commands.

4. **`tomli`** should be added as a quality dependency in both `setup.py` and `src/transformers/dependency_versions_table.py`.

5. The **`docker/quality.dockerfile`** should install `make` since the CI now depends on Makefile targets.

6. After making the code changes, **update the agent instruction files** (`.ai/AGENTS.md`) to accurately describe the new behavior of the `make` targets. The current description of `make check-repo` is stale and should be updated to match the refactored setup. Remove any claims about CI behavior that are no longer accurate.

## Files to Look At

- `Makefile` — current QA targets that invoke scripts directly
- `utils/` — existing check scripts (the pattern to wrap)
- `.circleci/config.yml` — CI jobs that duplicate Makefile logic
- `setup.py` — dependency extras
- `src/transformers/dependency_versions_table.py` — dependency version tracking
- `docker/quality.dockerfile` — Docker image for CI quality checks
- `.ai/AGENTS.md` — agent instructions describing make targets
