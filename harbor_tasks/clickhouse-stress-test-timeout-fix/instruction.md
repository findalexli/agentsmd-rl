# Fix stress test post-restart timeout for sanitizer builds

## Problem

The ClickHouse stress tests are experiencing spurious failures during the post-stress server restart phase under TSan (ThreadSanitizer) builds.

After the stress test completes, the server is restarted to verify data integrity. When `async_load_databases` is set to `false` (synchronous table loading), loading all tables created during the stress test takes longer than the default timeout under sanitizers, causing false "Cannot start clickhouse-server" failures.

Additionally, the current randomization for `async_load_databases` uses day-of-month based logic which produces the same result for all runs within a 24-hour period, rather than proper per-run randomization.

## Requirements

Modify `tests/docker_scripts/stress_runner.sh` to meet the following requirements:

### 1. Fix the async_load_databases randomization

The section that randomizes `async_load_databases` currently produces identical results for all runs within the same day because it uses day-of-month based logic. Change this so that each independent test execution gets a different randomization result.

### 2. Extend the post-stress server restart timeout

The server restart that follows the stress test (after removing `cannot_allocate_thread_injection.xml`) needs a longer timeout than the default. Under TSan with `async_load_databases=false`, the table loading phase takes several minutes.

### 3. Add an explanatory comment

Before the restart call in the post-stress section, add a comment explaining why the timeout is larger, referencing the sanitizer context and the table loading behavior.

## Context

- The `start_server` function is defined in `tests/docker_scripts/stress_tests.lib`
- Default timeout is 6 attempts with 20s sleep = ~2 minutes
- Under TSan with `async_load_databases=false`, table loading can take several minutes
- The post-stress restart occurs after removing `/etc/clickhouse-server/config.d/cannot_allocate_thread_injection.xml`
