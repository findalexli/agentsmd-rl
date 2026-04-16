# Fix CIDB Secret Configuration in collect_statistics.py

The `collect_statistics.py` script uses hardcoded AWS SSM parameter names when connecting to the CI database (CIDB). This means the script always queries the public CIDB, ignoring any per-fork secret overrides configured via `private_settings_overrides.py`.

## Symptom

When running in a private fork with custom `Settings.SECRET_CI_DB_*` values, the script still connects to the public CIDB instance instead of respecting the fork-specific configuration.

## Current Behavior

The file `ci/jobs/collect_statistics.py` contains hardcoded secret names:
- `clickhouse-test-stat-url`
- `clickhouse-test-stat-login`
- `clickhouse-test-stat-password`

These appear in calls similar to: `Secret.Config("clickhouse-test-stat-url").get_value()`

## Expected Behavior

The script should use the same secrets configured via `Settings.SECRET_CI_DB_*` that other CI job files in this repository use. These constants are defined in `ci/praktika/settings.py`:
- `Settings.SECRET_CI_DB_URL`
- `Settings.SECRET_CI_DB_USER`
- `Settings.SECRET_CI_DB_PASSWORD`

The `Info` class in `ci/praktika/info.py` provides a `get_secret()` method that retrieves these values.

## Requirements

The refactored code must:
- Import `Settings` from `ci.praktika.settings`
- Import `Info` from `ci.praktika.info`
- Use `Settings.SECRET_CI_DB_URL`, `Settings.SECRET_CI_DB_USER`, and `Settings.SECRET_CI_DB_PASSWORD` instead of hardcoded strings
- Use the `Info` class's `get_secret()` method to retrieve these values
- Pass the retrieved values to the `CIDB` constructor using keyword arguments
- Not import `Secret` from `ci.praktika`
- Not contain the hardcoded secret names `clickhouse-test-stat-url`, `clickhouse-test-stat-login`, or `clickhouse-test-stat-password`