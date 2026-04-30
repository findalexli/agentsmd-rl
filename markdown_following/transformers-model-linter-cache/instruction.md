# Model Structure Linter: Add Caching and Separate `make typing` Target

## Problem

The model structure linter (`utils/check_modeling_structure.py`) re-analyzes every modeling file under `src/transformers/models/` on every invocation, even when those files have not changed since the last clean run. On large checkouts this makes local iteration noticeably slow — developers fixing a single model have to wait for hundreds of unrelated files to be re-parsed.

Additionally, the `make style` target currently bundles ruff formatting/linting together with the `ty` type checker. There is no standalone target for running type checking and model structure rules on their own. Developers who just want to check types and model structure rules must run the full formatter pipeline.

The Makefile also has several legacy targets (`check-model-rules`, `check-model-rules-pr`, `check-model-rules-all`) that are redundant now that the main script already supports `--changed-only` and `--base-ref` flags.

## What Needs to Change

### 1. Add a content-aware cache to the model linter

Add caching to `utils/check_modeling_structure.py` so that files whose content and enabled rule set have not changed since the last clean run are skipped automatically. The cache is a JSON file located alongside the script. Its schema is a flat dictionary mapping file-path strings to hash-digest strings, for example: `{"src/transformers/models/foo/modeling_foo.py": "a1b2c3...", ...}`. When the cache file is missing, it should be treated as an empty cache (all files are checked).

Implement the following top-level helper functions in the script:

- **`_content_hash(text: str, enabled_rules: set[str]) -> str`** — computes a deterministic hex digest (at least 32 hex characters) from the file text and the set of enabled rule IDs. The result must be sensitive to text changes and to rule-set changes, but **insensitive to the order of rules** (i.e., set semantics — `{"A","B"}` and `{"B","A"}` produce the same hash). Repeated calls with identical inputs must return the same value.

- **`_load_cache() -> dict[str, str]`** — reads and returns the JSON cache dictionary from disk. Returns `{}` when the cache file does not exist or cannot be parsed.

- **`_save_cache(data: dict[str, str]) -> None`** — writes the cache dictionary to the JSON file on disk.

The cache file path must be stored as a **module-level variable** whose value contains both `".json"` and `"cache"` (case-insensitive).

Add a `--no-cache` CLI flag that bypasses the cache and re-checks every file. The `--help` output must mention this cache-related option. The existing `parse_args()` function must continue to support all of its current flags: `--list-rules`, `--no-progress`, `--changed-only`, and `--base-ref`.

### 2. Create a new `make typing` target

Create a Makefile target named `typing` that runs only the type checker (`python utils/check_types.py`) and the model structure linter (`python utils/check_modeling_structure.py`). Move the type-checker invocation out of `make style` so that `make style` handles only ruff formatting and linting.

Ensure `make check-repo` also invokes `check_modeling_structure.py` **without** the Make `-\ ` error-ignore prefix (so that violations are not silently swallowed). Remove the old error-prefixed invocation of `check_modeling_structure.py` from `check-repo`.

### 3. Remove the redundant Makefile targets

Remove these legacy targets from the Makefile: `check-model-rules`, `check-model-rules-pr`, `check-model-rules-all`.

### 4. Update agent config files and documentation

Update the following files to reference `make typing` instead of `make style` for type-checking workflows:

- `.ai/AGENTS.md` — must contain the string `make typing`
- `.ai/skills/add-or-fix-type-checking/SKILL.md` — must contain the string `make typing`
- `docs/source/en/pr_checks.md` — must document `make typing`

### 5. Add the cache file to `.gitignore`

Add an entry to `.gitignore` that excludes the model linter cache file. The entry should match a `.json` file containing `"cache"` in its name, or reference `check_modeling_structure` and `"cache"`.

## Code Style Requirements

- **ruff**: The modified `utils/check_modeling_structure.py` must pass `ruff check` and `ruff format --check`. Use `ruff` for all formatting and linting. No bare `# type: ignore` comments (always specify the error code, e.g. `# type: ignore[attr-defined]`).

## Relevant Files

- `utils/check_modeling_structure.py` — the model structure linter (main changes)
- `Makefile` — target restructuring
- `.ai/AGENTS.md`, `.ai/skills/add-or-fix-type-checking/SKILL.md` — agent config updates
- `docs/source/en/pr_checks.md` — documentation
- `.gitignore` — exclude cache file
