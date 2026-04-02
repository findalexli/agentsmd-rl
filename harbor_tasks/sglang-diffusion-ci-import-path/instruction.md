# Broken imports in diffusion CI publish scripts

## Summary

Two CI utility scripts in `scripts/ci/utils/diffusion/` crash immediately on import with an `ImportError` when run as standalone scripts. Both scripts need to reuse helper functions from `scripts/ci/utils/publish_traces.py` (one directory up), but the import mechanism is broken.

## Bug Details

### 1. `publish_comparison_results.py`

This script publishes diffusion comparison results to a CI data repository. It attempts to import helpers like `create_blobs`, `create_commit`, `get_branch_sha`, etc. from `publish_traces.py` using a relative package import (`from ..module import ...`). However, the script is invoked directly (e.g., `python3 scripts/ci/utils/diffusion/publish_comparison_results.py ...`), not as a package — so `__package__` is `None` and relative imports fail.

Additionally, the `sys.path.insert` fallback points to the wrong directory — it adds the script's own directory (`diffusion/`) instead of the parent directory where `publish_traces.py` actually lives.

### 2. `publish_diffusion_gt.py`

Same problem: uses a relative package import from `..publish_traces` and has the same incorrect `sys.path` manipulation that adds the wrong parent directory.

## Expected Behavior

Both scripts should be importable and runnable both as standalone scripts (`python3 scripts/ci/utils/diffusion/publish_comparison_results.py`) and when imported as part of a package. The import of helpers from `publish_traces.py` should succeed in both modes.

## Files

- `scripts/ci/utils/diffusion/publish_comparison_results.py`
- `scripts/ci/utils/diffusion/publish_diffusion_gt.py`
- `scripts/ci/utils/publish_traces.py` (the module they need to import from)
