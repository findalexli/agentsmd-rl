# Fix CIDB Secret Configuration in collect_statistics.py

The `collect_statistics.py` script is hardcoding secret names for connecting to the CI database (CIDB). This prevents the script from working correctly in private forks that need to use different secret names configured via `private_settings_overrides.py`.

## Problem

The file `ci/jobs/collect_statistics.py` currently uses hardcoded `Secret.Config` calls with specific AWS SSM parameter names:
- `clickhouse-test-stat-url`
- `clickhouse-test-stat-login`
- `clickhouse-test-stat-password`

This means the script always queries the public CIDB, even when running in a private fork that overrides `Settings.SECRET_CI_DB_*` values.

## Goal

Refactor the code to use the `Settings` class for CIDB secrets instead of hardcoded names. Look at how other files like `runner.py` and `cidb_cluster.py` handle this - they use `Info().get_secret(Settings.SECRET_CI_DB_*)` pattern.

## Relevant Files

- `ci/jobs/collect_statistics.py` - The file to modify
- `ci/praktika/settings.py` - Contains `Settings.SECRET_CI_DB_URL`, `SECRET_CI_DB_USER`, `SECRET_CI_DB_PASSWORD`
- `ci/praktika/info.py` - Contains `Info` class with `get_secret()` method
- `ci/praktika/cidb.py` - The `CIDB` class constructor

## Requirements

1. Import `Settings` from `ci.praktika.settings`
2. Import `Info` from `ci.praktika.info`
3. Remove the hardcoded secret names and direct `Secret` import
4. Use `Info().get_secret(Settings.SECRET_CI_DB_*)` to get secrets
5. Pass the retrieved values to the `CIDB` constructor

The `CIDB` class constructor accepts `url`, `user`, and `passwd` parameters. You need to provide these values obtained through the `Info().get_secret()` method using the appropriate `Settings` constants.

Look at the codebase for examples of how `Info().get_secret()` is used with `Settings` constants in other CI job files.
