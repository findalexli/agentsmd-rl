# Fix Stale ZooKeeper Session in User-Defined Object Refresh

## Problem

In the ClickHouse codebase at `/workspace/ClickHouse`, the `refreshObjects` function in `src/Functions/UserDefined/UserDefinedSQLObjectsZooKeeperStorage.cpp` has a bug: when the underlying ZooKeeper session expires mid-operation, the retry mechanism fails to recover because it continues using the expired session.

### Symptoms

The function uses `ZooKeeperRetriesControl` (accessible as `retries_ctl`) to retry transient ZooKeeper errors via its `retryLoop()` method. However, two issues prevent successful recovery:

1. **Watches bound to expired session**: The call to `getObjectNamesAndSetWatch` (which retrieves object names and registers ZooKeeper watches) is made *before* the `retryLoop()` begins. When the session expires and a retry occurs, the watches remain attached to the dead session, causing subsequent operations to fail.

2. **No session refresh on retry**: The `zookeeper` function parameter is captured once at function entry and never updated. On retry iterations, the code reuses the same (possibly expired) session handle for all ZooKeeper operations, including `tryLoadObject` and `getObjectNamesAndSetWatch`.

## Verification Criteria

The fixed `refreshObjects` function must satisfy all of the following:

1. **Session tracking variable**: A local variable of type `zkutil::ZooKeeperPtr` named `current_zookeeper` must be declared, initialized from the `zookeeper` parameter. This variable tracks the potentially refreshed session.

2. **Session refresh on retry**: Inside the `retries_ctl.retryLoop()` lambda, when `retries_ctl.isRetry()` is true, the `current_zookeeper` variable must be reassigned from `zookeeper_getter.getZooKeeper().first` to obtain a fresh session handle.

3. **Watches on current session**: The `getObjectNamesAndSetWatch` call must appear inside the retry loop (not before it) and must use `current_zookeeper` as its first argument. There must be no `getObjectNamesAndSetWatch` call involving `object_names` before the retry loop.

4. **Consistent session usage**: Both `tryLoadObject` and `getObjectNamesAndSetWatch` must be called with `current_zookeeper` (not the original `zookeeper` parameter) as their first argument inside the retry loop.

5. **Terminology**: Per the project's `CLAUDE.md` (in the repository root), when referring to logical errors in comments, use the word **"exception"** rather than **"crash"**.

## Style Conventions

- 4-space indentation (no tabs), no trailing whitespace, lines within 140 characters
- Must pass `clang-format` checks
