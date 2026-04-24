# Fix Stale ZooKeeper Session in UDF Refresh

## Problem

In the ClickHouse codebase, there's a bug in the user-defined function (UDF) refresh mechanism located in `src/Functions/UserDefined/UserDefinedSQLObjectsZooKeeperStorage.cpp`. When ZooKeeper session expires during the refresh operation, the retry mechanism fails because it continues using the expired session handle instead of obtaining a fresh one.

### Symptoms

1. **Watches bound to expired session**: The call to `getObjectNamesAndSetWatch()` is made *before* the `retryLoop` begins. When the session expires and a retry occurs, the watches remain attached to the dead session rather than the new one.

2. **No session refresh on retry**: The ZooKeeper session handle is captured once at the start of the operation and never updated. On retry iterations, the code reuses the same (possibly expired) session handle for all subsequent operations including `tryLoadObject()`, causing the retry to fail with the same stale session.

### Error Manifestation

When a ZooKeeper session expires during UDF refresh:
- The initial attempt fails with a session expired error
- The retry attempt uses the same expired session handle
- Watches registered before the `retryLoop` are bound to the dead session
- The refresh operation fails even though a fresh session could be obtained

## Expected Behavior

The UDF refresh logic in `src/Functions/UserDefined/UserDefinedSQLObjectsZooKeeperStorage.cpp` should:

1. Check inside the `retryLoop` whether the current iteration is a retry by calling `isRetry()` on the retries control object
2. When retrying (i.e., `isRetry()` returns true), obtain a fresh ZooKeeper session by calling `getZooKeeper()` before performing any operations
3. Move the call to `getObjectNamesAndSetWatch()` inside the `retryLoop` so watches are registered using the current (potentially fresh) session
4. Ensure all ZooKeeper operations (`getObjectNamesAndSetWatch()` and `tryLoadObject()`) use the same session variable consistently

## Style Conventions

- 4-space indentation (no tabs), no trailing whitespace, lines within 140 characters
- Must pass `clang-format` checks
- Must pass ClickHouse C++ style checks via `ci/jobs/scripts/check_style/check_cpp.sh`
- Must pass `codespell` for typo detection
- When referring to logical errors in comments, use the word **"exception"** rather than **"crash"** (per the project's CLAUDE.md)
- When writing function names in comments, use backtick format like `tryLoadObject` (without parentheses)

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `typos (spell-check)`
