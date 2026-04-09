# Fix UDF Registry Loss During ZooKeeper Session Expiry

## Problem

The User Defined Function (UDF) registry can be lost when the ClickHouse server's connection to ZooKeeper experiences transient failures or session expiry. When the `refreshObjects()` method encounters a Keeper hardware error (like session expiry), it currently aborts the entire refresh cycle, potentially leaving the UDF registry in an incomplete state.

## Context

The issue is in the UDF storage implementation that loads SQL objects from ZooKeeper. When transient Keeper errors occur during the refresh cycle, the current code doesn't properly retry - it just continues with a partial set of objects or aborts entirely, which can lead to:

1. Missing UDFs after a Keeper session expires and reconnects
2. Inconsistent UDF registry state across ClickHouse nodes
3. Need for manual intervention to restore UDFs

## Files to Modify

- `src/Functions/UserDefined/UserDefinedSQLObjectsZooKeeperStorage.cpp`

## Key Areas to Fix

### 1. Error Handling in tryLoadObject

The `tryLoadObject()` method needs to distinguish between:
- **Hardware errors** (session expiry, connection loss, etc.): These should be re-thrown so callers can retry
- **Other errors** (missing nodes, parse errors): These should be logged and return nullptr

Add a specific catch block for `zkutil::KeeperException` that checks for hardware errors using `Coordination::isHardwareError()`.

### 2. Retry Logic in refreshObjects

The `refreshObjects()` method needs to wrap its object loading loop in a retry mechanism:

1. Include the ZooKeeperRetries header
2. Define retry constants (max_retries=5, initial_backoff_ms=200, max_backoff_ms=5000)
3. Create a `ZooKeeperRetriesControl` instance with these settings
4. Wrap the loading loop in `retries_ctl.retryLoop()`
5. Clear the results vector at the start of each retry attempt to prevent partial results

## Requirements

- Use Allman-style braces (opening brace on a new line)
- Include proper logging for hardware errors
- Ensure the fix handles transient Keeper hiccups with exponential backoff
- The fix must ensure that if retries are exhausted, the exception propagates (don't reach setAllObjects with partial data)

## Testing

The fix should ensure that:
1. Transient Keeper errors trigger retry attempts with backoff
2. Hardware errors are properly detected and retried
3. Non-hardware errors are treated as missing objects (return nullptr)
4. The retry loop clears partial results on each attempt
