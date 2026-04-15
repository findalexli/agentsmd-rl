# Task: Refactor CIDB Secrets to Use Settings

## Problem

The `ci/jobs/collect_statistics.py` script hardcodes public CIDB credential names:
- `clickhouse-test-stat-url`
- `clickhouse-test-stat-login`
- `clickhouse-test-stat-password`

These are passed to `Secret.Config` with `Secret.Type.AWS_SSM_PARAMETER`. This causes the NightlyStatistics job to always connect to the public CIDB database, even in private forks that override `Settings.SECRET_CI_DB_*` values via `private_settings_overrides.py`.

## Goal

Refactor the CIDB initialization in `ci/jobs/collect_statistics.py` to use the `Settings` class for secret configuration, matching the pattern used in `ci/praktika/runner.py` and `ci/praktika/cidb_cluster.py`.

## Requirements

1. **Remove** the hardcoded secret name strings (`clickhouse-test-stat-url`, `clickhouse-test-stat-login`, `clickhouse-test-stat-password`) that currently hardcode the public CIDB credentials
2. **Import** `Info` from `ci.praktika.info` and `Settings` from `ci.praktika.settings`
3. **Retrieve** secrets using the Settings constants `Settings.SECRET_CI_DB_URL`, `Settings.SECRET_CI_DB_USER`, and `Settings.SECRET_CI_DB_PASSWORD`
4. **Initialize** the `CIDB` object with the retrieved credentials

## Key Files

- `ci/jobs/collect_statistics.py` - The file to modify (CIDB initialization section)
- `ci/praktika/cidb_cluster.py` - Reference for the Settings-based secret retrieval pattern
- `ci/praktika/runner.py` - Additional reference for the pattern

## Notes

- The fix should maintain the same overall structure - only the CIDB initialization section needs to change
- The `Info().get_secret()` method retrieves secret objects
- The `Settings` class provides `SECRET_CI_DB_URL`, `SECRET_CI_DB_USER`, `SECRET_CI_DB_PASSWORD` constants
- Constants `QUANTILES` and `DAYS` should not be modified