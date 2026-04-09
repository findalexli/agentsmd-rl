# Fix stress test post-restart timeout for sanitizer builds

## Problem

The ClickHouse stress tests are experiencing spurious failures during the post-stress server restart phase under TSan (ThreadSanitizer) builds.

After the stress test completes, the server is restarted to verify data integrity. When `async_load_databases` is set to `false` (synchronous table loading), loading all tables created during the stress test takes longer than the default timeout under sanitizers, causing false "Cannot start clickhouse-server" failures.

## Files to Modify

- `tests/docker_scripts/stress_runner.sh` - The stress test runner script

## Changes Needed

### 1. Fix the randomization of `async_load_databases`

The current implementation uses day-of-month based randomization which is not truly random per-run:

```bash
if [ $(( $(date +%-d) % 2 )) -eq 0 ]; then
```

Replace this with proper per-run randomization using `$RANDOM`:

```bash
if [ $((RANDOM % 2)) -eq 0 ]; then
```

### 2. Increase timeout for post-stress server restart

The post-stress restart uses a default timeout that is too short for sanitizer builds. Change:

```bash
start_server || { echo "Failed to start server"; exit 1; }
```

To:

```bash
# Use a larger timeout for the post-stress restart: under sanitizers with
# async_load_databases=false the server may need minutes to load all tables.
start_server 30 || { echo "Failed to start server"; exit 1; }
```

The `30` argument increases the retry attempts from 6 (default ~2 min) to 30 (~10 min).

## Context

- The `start_server` function is defined in `tests/docker_scripts/stress_tests.lib`
- Default timeout is 6 attempts with 20s sleep = ~2 minutes
- Under TSan with `async_load_databases=false`, table loading can take several minutes
- The post-stress restart occurs after the line: `rm /etc/clickhouse-server/config.d/cannot_allocate_thread_injection.xml`
