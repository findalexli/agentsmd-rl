# RC Version Installation Fails Due to Cooldown Period

## Problem

When using Breeze to test Apache Airflow release candidate (RC) versions, the installation fails with:

```
× No solution found when resolving dependencies:
  ╰─▶ Because there is no version of apache-airflow==3.2.0rc2 and you require apache-airflow==3.2.0rc2
```

This happens even though the RC package exists on PyPI. The issue is that the package resolver's cooldown period (4 days) is longer than the typical RC testing window (72 hours), causing newly published RC packages to be invisible to the resolver.

## Context

- The file `scripts/in_container/install_airflow_and_providers.py` handles installation of Airflow and providers in the Breeze development environment
- When `pre_release=True`, the script currently adds `--pre` flag to allow pre-release versions
- The `uv` package manager supports an `--exclude-newer` flag that limits resolution to packages published before a given timestamp

## Expected Behavior

When installing pre-release versions (when `pre_release=True`):

1. The install commands should pass the current timestamp to `--exclude-newer` alongside the `--pre` flag. The `--exclude-newer` flag should accept an ISO 8601 formatted timestamp (e.g., `2024-04-06T16:08:05.123456`).

2. The console message displayed when enabling pre-release installation should contain the exact phrase **"airflow and providers"** (updating the current message that only mentions "airflow").

3. Non-pre-release installations (when `pre_release=False`) must NOT be affected by these changes - they should continue to work exactly as before without any timestamp or `--exclude-newer` logic.

## Files to Modify

- `scripts/in_container/install_airflow_and_providers.py`

## Implementation Notes

The `--exclude-newer` flag from `uv` allows the resolver to use packages published before a specific point in time. You will need to generate a current UTC timestamp in ISO format and pass it to this flag for the installation commands that run when pre-release versions are enabled.

Both installation code paths in the script (the one that installs Airflow with providers, and the one that installs only Airflow core with task SDK) should exhibit this behavior when `pre_release=True`.

## Observable Requirements

The solution must satisfy the following observable properties:

- The `--exclude-newer` flag must be present in the source at least twice (once for each installation function path)
- The source must contain a datetime import: either `from datetime import datetime` or `import datetime`
- When pre-release installation is enabled, the console output must contain the exact phrase **"airflow and providers"**

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `ruff format and ruff check`
