# Fix Pre-Release Package Installation

## Problem

When installing pre-release (RC) versions of Airflow and providers, the installation commands don't properly prevent unintended package upgrades. The `--pre` flag alone allows pre-release versions but doesn't restrict which versions can be installed.

## Task

Modify `scripts/in_container/install_airflow_and_providers.py` to fix the pre-release installation behavior.

## Details

The file contains two installation functions:
1. `_install_airflow_and_optionally_providers_together()` - installs airflow and providers together
2. `_install_only_airflow_airflow_core_task_sdk_with_constraints()` - installs only airflow core components

Both functions check `installation_spec.pre_release` and add `--pre` to the pip command when true. However, this alone doesn't properly handle pre-release scenarios.

When `pre_release=True`:
- The pip command needs to include both `--pre` AND `--exclude-newer` with a current timestamp
- The console message should be updated to mention both "airflow and providers"

When `pre_release=False`:
- Neither `--pre` nor `--exclude-newer` should be added (this is the current behavior and should remain unchanged)

## Requirements

1. Import `datetime` from the `datetime` module at the top of the file
2. In both functions, when `installation_spec.pre_release` is True:
   - Add `--exclude-newer` flag followed by `datetime.now().isoformat()` to the pip command
   - Update the console print message to mention "airflow and providers" (not just "airflow")
3. The fix should use `.extend()` to add both `--pre` and `--exclude-newer` with the timestamp together

## Verification

After your fix, when running with pre-release enabled:
- The pip install command should include: `--pre --exclude-newer 2024-01-15T10:30:00` (or current timestamp)
- The console output should show: "Allowing pre-release versions of airflow and providers"

Without the fix, only `--pre` is added, which allows unintended package upgrades during RC testing.
