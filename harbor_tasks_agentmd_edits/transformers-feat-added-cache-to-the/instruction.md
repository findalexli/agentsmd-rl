# Add a file-level cache to the model structure linter and reorganize Makefile targets

## Problem

The model structure linter (`utils/check_modeling_structure.py`) re-analyzes every file on each run, even when files haven't changed. This is slow for iterative development. Additionally, the `make style` target bundles formatting, linting, and type checking all together — type checking and model structure linting should be a separate step so developers can run them independently.

## What needs to change

1. **Add caching to `utils/check_modeling_structure.py`**: Implement a file-level cache so that unchanged files (with the same content and same set of enabled rules) are skipped on subsequent runs. The cache should be stored as a JSON file adjacent to the script. Include a `--no-cache` CLI flag to bypass caching when needed.

2. **Reorganize the Makefile**: Extract type checking (`check_types.py`) and model structure linting (`check_modeling_structure.py`) out of the `style` target into a new `typing` target. The `check-repo` target should also run the model structure linter as a hard failure (not with the `-` soft-fail prefix). Clean up the old `check-model-rules*` targets that are no longer needed.

3. **Update `.gitignore`**: The new cache file should be git-ignored.

4. After making the code changes, update the relevant agent instruction files and documentation to reflect the new `make typing` command. The project's `.ai/AGENTS.md`, relevant skill files, and contributor documentation should accurately describe the updated command structure.

## Files to Look At

- `utils/check_modeling_structure.py` — the model structure linter script
- `Makefile` — build targets for style, type checking, and repo checks
- `.gitignore` — should exclude the new cache file
- `.ai/AGENTS.md` — agent command documentation
- `.ai/skills/add-or-fix-type-checking/SKILL.md` — type checking skill workflow
- `docs/source/en/pr_checks.md` — contributor documentation for PR checks
