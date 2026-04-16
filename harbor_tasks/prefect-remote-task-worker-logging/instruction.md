# Task: Fix Missing Logs on Remote Task Workers

## Problem

When tasks run on remote Dask or Ray workers, task run logs are silently lost. This happens because the `APILogHandler` is never attached to Prefect loggers on these workers.

The root cause is that `setup_logging()` normally lives in `prefect.main`, which is lazily imported via `prefect.__getattr__`. Remote workers that don't access names like `prefect.flow` or `prefect.task` never trigger that import, so logging is never configured.

## What You Need To Do

Implement a mechanism that ensures logging is configured when tasks run on remote workers, while being safe to call multiple times without re-configuring.

### Requirements

1. **Create an idempotent logging setup guard function** named `ensure_logging_setup`:
   - Must be importable from `prefect.logging.configuration`
   - Must be safe to call multiple times (idempotent - no errors or re-configuration on subsequent calls)
   - Must only configure logging when it hasn't been configured yet in the current process
   - Must include a docstring mentioning logging and remote execution environments (Dask, Ray, or workers)

2. **Integrate the guard function with remote context hydration**:
   - When a remote worker receives serialized context data to execute a task, logging must be set up before the task runs
   - The integration point is where `hydrated_context` processes serialized context from remote workers
   - The guard function should be imported and called to ensure logging is configured

### Key Information

- `PROCESS_LOGGING_CONFIG` is a dictionary in `prefect.logging.configuration` that tracks whether logging has been configured in the current process
- When this dictionary is empty, logging has not yet been configured
- `hydrated_context()` is a context manager used to restore context from serialized data on remote workers
- For local runs, `PROCESS_LOGGING_CONFIG` is already populated via the normal SDK import path, so the guard function will be a no-op
- For remote runs, the serialized context triggers the logging setup before task execution

## References

- Related issues: #18082, #10829
