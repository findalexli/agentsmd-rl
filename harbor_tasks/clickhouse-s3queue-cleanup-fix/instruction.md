# Fix S3Queue Stale Processing Node Cleanup Race Condition

## Problem

The `cleanupPersistentProcessingNodes()` function in the S3Queue storage engine has a race condition when removing stale processing nodes from ZooKeeper. Currently, nodes are removed without version checking, which can lead to:

1. Incorrectly removing nodes that have been recreated with different content
2. Not properly accounting for which removals actually succeeded

## Symptoms

- Processing nodes may be incorrectly cleaned up even if they were recently recreated
- Race conditions between node removal and node recreation by other processes
- Lack of visibility into actual cleanup success vs attempted cleanup

## Files to Modify

- `src/Storages/ObjectStorageQueue/ObjectStorageQueueMetadata.cpp`

## What Needs to Change

The fix involves several coordinated changes to `cleanupPersistentProcessingNodes()`:

1. **Store version information**: Change `nodes_to_remove` from a simple list of paths to a list of `(path, version)` pairs. The version comes from `response[i].stat.version` when checking node metadata.

2. **Use versioned removal**: When calling `tryRemove()`, pass the version as the second parameter to enable optimistic concurrency control.

3. **Handle ZBADVERSION**: Add `ZBADVERSION` to the list of acceptable error codes (alongside `ZNONODE`), logging that the node was "already removed or recreated".

4. **Track successful removals**: Add a counter to track how many removals actually succeeded (returned `ZOK`), and update the log message to show `removed/total` format.

5. **Add trace logging**: Log each node being processed for better observability.

## Expected Behavior

After the fix:
- Nodes are only removed if the version matches (no race conditions)
- Version mismatches are gracefully handled and logged
- The log shows actual successful removals vs attempted removals
- Each node removal attempt is trace-logged

## Context

This is part of the S3Queue storage engine which manages distributed processing of S3 objects. The processing nodes in ZooKeeper track which objects are currently being processed by which consumers.

**Agent Config Reference**: See `.claude/CLAUDE.md` and `.github/copilot-instructions.md` for ClickHouse-specific coding guidelines, including rules about:
- Deletion logging requirements
- Error handling patterns
- Concurrency safety
