# Fix Pre-Release Package Installation

## Problem

When installing pre-release (RC) versions of Airflow and providers, the installation commands don't properly prevent unintended package upgrades. The `--pre` flag alone allows pre-release versions but doesn't restrict which versions can be installed.

## Task

Modify `scripts/in_container/install_airflow_and_providers.py` to fix the pre-release installation behavior.

## Details

The file contains two installation functions that handle pre-release scenarios:
1. One function installs airflow and providers together
2. Another function installs only airflow core components

Both functions check `installation_spec.pre_release` and add `--pre` to the pip command when true. However, this alone doesn't properly handle pre-release scenarios because pip can still upgrade other packages to newer versions.

## Requirements

When `pre_release=True`:
- The pip command needs to include both `--pre` AND `--exclude-newer` with a current timestamp in ISO format (e.g., `2024-01-15T10:30:00`)
- The console message should be updated to mention both "airflow and providers"

When `pre_release=False`:
- Neither `--pre` nor `--exclude-newer` should be added (this is the current behavior and should remain unchanged)

## Expected Behavior After Fix

When running with pre-release enabled:
- The pip install command should include: `--pre --exclude-newer` followed by the current timestamp
- The console output should show: "Allowing pre-release versions of airflow and providers"

Without the fix, only `--pre` is added, which allows unintended package upgrades during RC testing.

## Verification

After your fix:
- Installing with `pre_release=True` should include `--pre` and `--exclude-newer` with a current ISO timestamp
- Installing with `pre_release=False` should NOT add these flags
- The console message should mention both "airflow and providers"

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `ruff format and ruff check`
