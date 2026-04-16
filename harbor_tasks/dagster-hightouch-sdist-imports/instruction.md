# Fix dagster-hightouch sdist packaging issue

## Problem

The dagster-hightouch package fails to import correctly when installed from a source distribution (sdist). The `check-manifest` CI check fails, and `import dagster_hightouch` raises import errors when the package is installed from a tarball rather than from a development checkout.

## Background

Python packages distributed as sdist/tarballs have a different directory structure than the source checkout. Relative imports (like `from .resources`) rely on the package being laid out identically to the source tree, which breaks in sdist because the extracted tarball has a different structure.

When a package is built as an sdist and then installed, the module resolution path changes. Code that works in a dev checkout (where `dagster_hightouch/` is directly importable) will fail in sdist because the package layout after extraction doesn't preserve the relative directory structure that makes `..resources` resolution work.

## Symptoms

The following symptoms indicate the package has this issue:

1. **Import fails from sdist**: Running `import dagster_hightouch` raises `ModuleNotFoundError` or `ImportError` when the package is installed from a built tarball rather than from the source tree.

2. **`check-manifest` CI fails**: The CI pipeline's `check-manifest` step rejects the package due to packaging metadata issues.

3. **Relative import patterns present**: The package uses import patterns like `from .resources`, `from .ops`, `from .component`, `from . import utils`, `from .types` — these are relative imports that break in sdist context.

4. **Incorrect library registration import**: The code imports `DagsterLibraryRegistry` from `dagster._core.libraries`, which is not the correct import path for library registration in this version of the codebase.

## Requirements

After fixing, the package must satisfy the following:

1. **Package imports from sdist**: `import dagster_hightouch` must succeed when the package is installed from a built sdist tarball.

2. **Absolute imports used**: The package code uses absolute imports with the `dagster_hightouch.` package prefix (e.g., `from dagster_hightouch.resources import ...` instead of `from .resources import ...`). All relative import patterns must be converted to their absolute form.

3. **Correct library registration**: The code imports `DagsterLibraryRegistry` from the correct module path for library registration (`dagster_shared.libraries`, not `dagster._core.libraries`).

4. **No packaging conflicts**: The package root must not contain a `pyproject.toml` file that conflicts with the repository's packaging configuration.

5. **All exports accessible**: After `import dagster_hightouch`, all items listed in `dagster_hightouch.__all__` must be accessible as module attributes.

6. **Linting passes**: The code must pass `ruff==0.11.5` linting and formatting checks.

7. **Repository tests pass**: The tests in `dagster_hightouch_tests/` must pass (excluding tests that use newer Dagster API versions not available in the base commit).