# Fix stress test post-restart timeout for sanitizer builds

## Problem

The ClickHouse stress tests are experiencing spurious failures during the post-stress server restart phase under TSan (ThreadSanitizer) builds.

After the stress test completes, the server is restarted to verify data integrity. When `async_load_databases` is set to `false` (synchronous table loading), loading all tables created during the stress test takes longer than the default timeout under sanitizers, causing false "Cannot start clickhouse-server" failures.

Additionally, the current randomization for `async_load_databases` uses day-of-month based logic which produces the same result for all runs within a 24-hour period, rather than proper per-run randomization.

## Requirements

Modify `tests/docker_scripts/stress_runner.sh` to meet the following requirements:

### 1. Use proper per-run randomization for `async_load_databases`

In the section that randomizes `async_load_databases` settings, the current implementation uses day-of-month based logic that produces identical results for all runs within the same day. Change this to use proper per-run randomization that varies between independent test executions.

The randomization check must use a bash randomization mechanism that produces a 0 or 1 result per execution (not per day). The file must not contain any date-based randomization using patterns like `date +%-d`.

### 2. Add timeout argument to post-stress server restart

After the line that removes `cannot_allocate_thread_injection.xml`, the `start_server` call must include a timeout argument of `30` (increasing retry attempts from the default 6 to 30). This call must appear as `start_server 30`.

### 3. Add explanatory comment for the timeout

The timeout change must include an explanatory comment placed immediately before the `start_server 30` call. The comment must contain the exact phrases:
- "larger timeout for the post-stress restart"
- "under sanitizers with"

## Context

- The `start_server` function is defined in `tests/docker_scripts/stress_tests.lib`
- Default timeout is 6 attempts with 20s sleep = ~2 minutes
- Under TSan with `async_load_databases=false`, table loading can take several minutes
- The post-stress restart occurs after removing `/etc/clickhouse-server/config.d/cannot_allocate_thread_injection.xml`
