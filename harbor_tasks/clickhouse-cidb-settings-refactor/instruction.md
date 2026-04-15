# Fix CIDB Secret Configuration in collect_statistics.py

The `collect_statistics.py` script uses hardcoded AWS SSM parameter names when connecting to the CI database (CIDB). This means the script always queries the public CIDB, ignoring any per-fork secret overrides configured via `private_settings_overrides.py`.

## Symptom

When running in a private fork with custom `Settings.SECRET_CI_DB_*` values, the script still connects to the public CIDB instance instead of respecting the fork-specific configuration.

## Current Behavior

The file `ci/jobs/collect_statistics.py` contains hardcoded secret names:
- `clickhouse-test-stat-url`
- `clickhouse-test-stat-login`
- `clickhouse-test-stat-password`

These appear in calls that look like: `Secret.Config("clickhouse-test-stat-url").get_value()`

## Expected Behavior

The script should use the same secrets configured via `Settings.SECRET_CI_DB_*` that other CI job files in this repository use. These constants are defined in `ci/praktika/settings.py`:
- `Settings.SECRET_CI_DB_URL`
- `Settings.SECRET_CI_DB_USER`
- `Settings.SECRET_CI_DB_PASSWORD`

The `Info` class in `ci/praktika/info.py` provides a `get_secret()` method that retrieves these values.

## Constraints

- The `CIDB` constructor accepts `url`, `user`, and `passwd` keyword arguments
- The `Info` class must be imported from `ci.praktika.info`
- `Settings` must be imported from `ci.praktika.settings`
- The variable holding the `Info()` instance must be named `info` (lowercase) so the pattern `info.get_secret(` appears in the code
- The old `Secret` import from `ci.praktika` must be removed
- The hardcoded names above must not appear in the refactored code

## How to Discover the Solution Pattern

Look at other files in `ci/jobs/` that use `Info().get_secret(Settings.SECRET_CI_DB_*)` — for example, `runner.py` or `cidb_cluster.py` in the same directory. These files demonstrate the established pattern for accessing CIDB credentials in this codebase.
