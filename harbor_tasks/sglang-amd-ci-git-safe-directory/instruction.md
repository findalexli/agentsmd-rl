# AMD CI containers fail at "Install dependencies" due to git ownership error

## Problem

All AMD CI workflows (nightly and PR tests for both ROCm 7.0 and 7.2) are failing during the "Install dependencies" step. The failure started around March 25, 2026 and affects the majority of CI jobs.

The root cause is a git "dubious ownership" error inside the CI container. The AMD CI containers run as `root` (via `--user root`), but the repository checkout mounted into the container at `/sglang-checkout` is owned by the GitHub Actions runner user (non-root). Git >= 2.35.2 rejects operations on repositories owned by a different user unless the directory is explicitly marked as safe.

Previously this wasn't a problem because `setuptools-scm` handled the error gracefully. However, the newer `vcs_versioning` package (which `setuptools-scm>=8.0` now resolves to) treats this git error as fatal during version introspection, causing `pip install` to fail.

## Affected files

The AMD CI container startup scripts need to be fixed:

- `scripts/ci/amd/amd_ci_start_container.sh` — used by `nightly-test-amd.yml`, `pr-test-amd.yml`, and their ROCm 7.2 variants
- `scripts/ci/amd/amd_ci_start_container_disagg.sh` — used by disaggregated testing workflows

Both scripts launch Docker containers but do not configure the git safe.directory setting after the container starts.

## Expected behavior

After the container is launched, the checkout directory should be marked as a safe directory for git, so that package version resolution via `setuptools-scm` / `vcs_versioning` succeeds inside the container.
