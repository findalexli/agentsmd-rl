# Task: Refactor CIDB Secrets to Use Settings

## Problem

The `ci/jobs/collect_statistics.py` script connects to the public CIDB database because the CIDB initialization bypasses the `Settings` configuration layer. When private forks override `Settings.SECRET_CI_DB_*` values via `private_settings_overrides.py`, those overrides have no effect — the script always uses hardcoded credential names.

## Symptom

The script currently uses hardcoded strings for CIDB credentials:
- `clickhouse-test-stat-url`
- `clickhouse-test-stat-login`
- `clickhouse-test-stat-password`

These are passed to `Secret.Config` with `Secret.Type.AWS_SSM_PARAMETER`. This means the NightlyStatistics job ignores any custom CIDB credentials configured through `Settings`.

## Goal

Modify the CIDB initialization in `ci/jobs/collect_statistics.py` so that secret configuration respects the `Settings` class. The pattern should match how other components in this codebase handle secrets — look at `ci/praktika/cidb_cluster.py` and `ci/praktika/runner.py` for reference implementations.

## Expected Behavior

After the fix:
- The CIDB client should retrieve its connection credentials from the `Settings` class (specifically `Settings.SECRET_CI_DB_URL`, `Settings.SECRET_CI_DB_USER`, and `Settings.SECRET_CI_DB_PASSWORD`)
- The NightlyStatistics job should honor custom CIDB credentials when `Settings.SECRET_CI_DB_*` values are overridden in private forks

## Verification

Your fix is correct if:
1. No hardcoded secret names (`clickhouse-test-stat-url`, `clickhouse-test-stat-login`, `clickhouse-test-stat-password`) remain in `ci/jobs/collect_statistics.py`
2. The `Info` class from `ci.praktika.info` and `Settings` class from `ci.praktika.settings` are used
3. The CIDB initialization uses the Settings-based secret retrieval pattern (as demonstrated in `ci/praktika/cidb_cluster.py` or `ci/praktika/runner.py`)
4. The function `get_job_stat_for_interval` still exists and the `QUANTILES`/`DAYS` constants remain unchanged

## Notes

- The `Info` class provides a `get_secret()` method for retrieving secret objects
- The `Settings` class defines `SECRET_CI_DB_URL`, `SECRET_CI_DB_USER`, and `SECRET_CI_DB_PASSWORD` constants
- Constants `QUANTILES` and `DAYS` should not be modified