# Fix UDF Registry Loss During Keeper Session Expiry

## Problem

When ClickHouse's ZooKeeper (Keeper) session experiences transient hiccups (connection blips, session jitter), the UDF (User Defined Function) registry can be lost. The `UserDefinedSQLObjectsZooKeeperStorage` class loads UDF definitions from ZooKeeper, but during refresh operations, transient Keeper errors were not being handled properly - they would cause the entire refresh cycle to abort, leading to an empty or partial UDF registry.

## Required Fix

The fix must ensure that transient Keeper errors during UDF loading are handled gracefully with retry logic, instead of causing the entire UDF registry to be cleared.

### Specific Implementation Details

The file to modify is: `src/Functions/UserDefined/UserDefinedSQLObjectsZooKeeperStorage.cpp`

### Behavioral Requirements

1. **Add necessary includes**: Add these two includes near the existing Keeper includes:
   - `#include <Common/ZooKeeper/ZooKeeperCommon.h>` - provides `Coordination::isHardwareError()` function
   - `#include <Common/ZooKeeper/ZooKeeperRetries.h>` - provides `ZooKeeperRetriesControl` class

2. **Handle Keeper exceptions in object loading** (`tryLoadObject` method): When loading individual UDF objects:
   - Add a catch block specifically for `const zkutil::KeeperException & e` BEFORE the generic `catch (...)` block
   - Inside this catch block, check if the error is a hardware error using `Coordination::isHardwareError(e.code)`
   - If it's a hardware error: log a WARNING message that includes both the object name (via `backQuote(object_name)`) and the exception message (`e.message()`), then re-throw with `throw;`
   - If it's NOT a hardware error: log the exception and return `nullptr` (treat as missing object)

3. **Implement retry logic in batch refresh** (`refreshObjects` method): When refreshing all UDF objects:
   - Define three static constexpr UInt64 constants for retry configuration (e.g., `max_retries`, `initial_backoff_ms`, `max_backoff_ms`)
   - Instantiate a `ZooKeeperRetriesControl` object with a descriptive name (like `"refreshObjects"`), the logger, and a `ZooKeeperRetriesInfo` struct containing the retry parameters
   - Wrap the object loading loop in a `retryLoop` call that:
     - Clears the results vector at the start of each retry attempt (using `.clear()`)
     - Iterates through all object names and loads each one
     - Lets hardware errors propagate so the retry control can catch and retry them

4. **Add explanatory comments**: Add comments explaining:
   - That transient Keeper hiccups are handled with retry/backoff instead of aborting the refresh
   - That hardware errors are re-thrown so the retry control can handle them
   - That the goal is to avoid reaching `setAllObjects` with a partial set when retries are exhausted

## Context

The codebase has existing infrastructure for Keeper retries. The `isHardwareError()` function and `ZooKeeperRetriesControl` class are available in the Common/ZooKeeper headers.

When hardware errors occur during `tryLoadObject`, they should be re-thrown so the `ZooKeeperRetriesControl` in `refreshObjects` can catch them and retry automatically. If retries are exhausted, the exception propagates to the caller, preventing `setAllObjects` from being called with a partial set of objects.
