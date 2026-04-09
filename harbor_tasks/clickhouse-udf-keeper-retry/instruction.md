# Fix UDF Registry Loss During Keeper Session Expiry

## Problem

User-defined functions (UDFs) stored in ZooKeeper can be **silently lost** when the ClickHouse server experiences transient connection issues with ZooKeeper/Keeper.

### Root Cause

In `UserDefinedSQLObjectsZooKeeperStorage`, when loading UDF definitions from ZooKeeper:

1. **tryLoadObject()** catches all `KeeperException` errors the same way - whether it's a network/hardware error (connection loss, session expiry) or a logical error (node not found)
2. **refreshObjects()** has no retry mechanism for transient failures

This means when a brief network hiccup occurs, all UDFs can be dropped from the local registry instead of being retried.

## What You Need to Fix

**File:** `src/Functions/UserDefined/UserDefinedSQLObjectsZooKeeperStorage.cpp`

### In `tryLoadObject()`:

The current code has a generic catch-all block:

```cpp
catch (...)
{
    tryLogCurrentException(...);
    return nullptr;  // Treats ALL errors as "object not found"
}
```

You need to add a specific catch block for `zkutil::KeeperException` that:
- **Re-throws hardware errors** (connection loss, session expiry) so the caller can retry
- **Returns nullptr** for non-hardware errors (like "node not found")

Hardware errors can be checked using `Coordination::isHardwareError(error_code)`.

### In `refreshObjects()`:

The current code loads all objects in a simple loop without any retry logic. When a transient Keeper error occurs, the entire refresh cycle fails and UDFs are lost.

You need to wrap the loading loop in a `ZooKeeperRetriesControl` retry mechanism:
- Clear the results vector at the start of each retry attempt
- Use exponential backoff between retries
- Constants to use: `max_retries = 5`, `initial_backoff_ms = 200`, `max_backoff_ms = 5000`

### Required Headers

You'll need to add these includes:
- `<Common/ZooKeeper/ZooKeeperCommon.h>` (for `Coordination::isHardwareError`)
- `<Common/ZooKeeper/ZooKeeperRetries.h>` (for `ZooKeeperRetriesControl`)

## Verification

Your fix will be verified by checking:
1. Hardware errors are detected and re-thrown (not swallowed)
2. Retry constants are defined correctly
3. `ZooKeeperRetriesControl` is used in `refreshObjects()`
4. Required headers are included
5. The catch blocks are in the correct order (specific before generic)

## Notes

- This is a backport fix - keep changes minimal and focused
- The fix should handle transient Keeper hiccups gracefully without dropping UDFs
- Look at how other parts of the codebase handle `KeeperException` and `ZooKeeperRetriesControl` for examples
