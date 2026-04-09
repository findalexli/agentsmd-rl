# Task: Add Error Logging for Status::unknown Responses

## Problem

The `PushLogs` function in `rust/log-service/src/lib.rs` returns `Status::unknown` errors to callers in three error paths, but these errors are not logged server-side before being returned. This makes debugging difficult because the server doesn't record what went wrong.

## Required Changes

Add `tracing::error!` calls to log errors in the following three error paths within the `PushLogs` handler:

1. **get_log_from_handle failure**: When `get_log_from_handle()` returns an error, log the error with `tracing::error!` before returning `Status::unknown`.

2. **proto encode failure**: When `record.encode()` fails, log the error with `tracing::error!` before returning `Status::unknown`.

3. **append_many failure**: When `append_many()` returns an error, log the error with `tracing::error!` before returning the status.

## Guidelines

- Use `tracing::error!(err = %err, "descriptive message")` format for all error logs
- Place the error log immediately before returning the error status
- Use descriptive messages that match the failure type:
  - `"get_log_from_handle failure"` for get_log_from_handle errors
  - `"proto encode failure"` for proto encoding errors  
  - `"append_many failure"` for append_many errors

## Files to Modify

- `rust/log-service/src/lib.rs` - Look for the `PushLogs` implementation in the `LogServer` impl block

## Verification

The code should compile successfully after your changes. The error logging should follow the pattern used elsewhere in the codebase for consistency.
