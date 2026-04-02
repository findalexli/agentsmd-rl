# Model Structure Linter: Add Caching and Separate `make typing` Target

## Problem

The model structure linter (`utils/check_modeling_structure.py`) re-analyzes every modeling file under `src/transformers/models/` on every invocation, even when those files have not changed since the last clean run. On large checkouts this makes local iteration noticeably slow — developers fixing a single model have to wait for hundreds of unrelated files to be re-parsed.

Additionally, the `make style` target currently bundles ruff formatting/linting together with the `ty` type checker. There is no standalone target for running type checking and model structure rules on their own. Developers who just want to check types and model structure rules must run the full formatter pipeline.

The Makefile also has several legacy targets (`check-model-rules`, `check-model-rules-pr`, `check-model-rules-all`) that are redundant now that the main script already supports `--changed-only` and `--base-ref` flags.

## What Needs to Change

1. **Add a content-aware cache to the model linter** so that files whose content (and enabled rule set) have not changed since the last clean run are skipped automatically. The cache should be stored as a JSON file next to the script and should be invalidatable via a CLI flag.

2. **Create a new `make typing` target** that runs only the type checker and model structure rules. Move type checking out of `make style` into this new target. Ensure `make check-repo` also runs the model linter (without the error-ignore prefix so violations are not silently swallowed).

3. **Remove the redundant Makefile targets** (`check-model-rules`, `check-model-rules-pr`, `check-model-rules-all`).

4. **Update agent config files and documentation** to reference `make typing` instead of `make style` for type-checking workflows:
   - `.ai/AGENTS.md`
   - `.ai/skills/add-or-fix-type-checking/SKILL.md`
   - `docs/source/en/pr_checks.md`

5. **Add the cache file pattern to `.gitignore`** so the local cache is never committed.

## Relevant Files

- `utils/check_modeling_structure.py` — the model structure linter (main changes)
- `Makefile` — target restructuring
- `.ai/AGENTS.md`, `.ai/skills/add-or-fix-type-checking/SKILL.md` — agent config updates
- `docs/source/en/pr_checks.md` — documentation
- `.gitignore` — exclude cache file
