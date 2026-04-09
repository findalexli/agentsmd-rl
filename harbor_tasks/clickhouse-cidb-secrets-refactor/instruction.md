# Task: Refactor CIDB Secrets to Use Settings

## Problem

The `ci/jobs/collect_statistics.py` script hardcodes public CIDB secret names (`clickhouse-test-stat-url`, `clickhouse-test-stat-login`, `clickhouse-test-stat-password`) using `Secret.Config` calls with `Secret.Type.AWS_SSM_PARAMETER`. 

This causes the NightlyStatistics job to always connect to the public CIDB database, even in private forks that override `Settings.SECRET_CI_DB_*` values via `private_settings_overrides.py`.

## Goal

Refactor the CIDB initialization in `ci/jobs/collect_statistics.py` to use the `Settings` class for secret configuration, matching the pattern used in `ci/praktika/runner.py` and `ci/praktika/cidb_cluster.py`.

## Requirements

1. **Remove** the hardcoded `Secret.Config` calls for CIDB credentials
2. **Import** `Info` from `ci.praktika.info` and `Settings` from `ci.praktika.settings`
3. **Use** `Info().get_secret(Settings.SECRET_CI_DB_URL)`, `Settings.SECRET_CI_DB_USER`, and `Settings.SECRET_CI_DB_PASSWORD` to retrieve secrets
4. **Initialize** the `CIDB` object with the retrieved credentials

## Key Files

- `ci/jobs/collect_statistics.py` - The file to modify (around line 113 where CIDB is initialized)

## Notes

- The `Info().get_secret()` method returns a secret object that can be chained with `.join_with()` to combine multiple secrets
- Look at `ci/praktika/cidb_cluster.py` for an example of the pattern to follow
- The fix should maintain the same overall structure - only the CIDB initialization section needs to change
