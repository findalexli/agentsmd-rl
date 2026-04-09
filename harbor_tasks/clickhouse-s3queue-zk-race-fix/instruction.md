# Task: Fix Race Condition in S3Queue ZooKeeper Node Cleanup

## Problem

The S3Queue storage engine has a race condition in the `cleanupPersistentProcessingNodes()` function in `src/Storages/ObjectStorageQueue/ObjectStorageQueueMetadata.cpp`. When cleaning up stale processing nodes from ZooKeeper, there's a window between listing nodes and deleting them where another process might recreate the node. This can lead to:

1. Incorrectly deleting a newly-recreated node (if it has the same path)
2. Missing proper error handling when the node version has changed
3. Poor observability - not knowing how many nodes were actually removed vs attempted

## What You Need to Fix

The current implementation lists nodes to remove, then deletes them by path only. This is unsafe because ZooKeeper uses optimistic concurrency control with version numbers.

You need to:

1. **Track node versions**: When listing nodes to potentially remove, capture their current ZooKeeper version numbers alongside the paths.

2. **Use versioned deletes**: When removing nodes, pass the version number to `tryRemove()`. This ensures the delete only succeeds if the node hasn't been modified since it was listed.

3. **Handle ZBADVERSION**: If the version doesn't match (meaning the node was recreated), handle this gracefully by logging and continuing rather than throwing an exception.

4. **Improve logging**: Track and report how many nodes were successfully removed vs how many were attempted.

## Key Areas to Look At

- Function: `cleanupPersistentProcessingNodes()`
- File: `src/Storages/ObjectStorageQueue/ObjectStorageQueueMetadata.cpp`
- Lines around: The `nodes_to_remove` vector declaration and the removal loop

## Expected Behavior After Fix

- Stale nodes are safely removed using versioned deletes
- If a node is recreated between listing and deletion, it's skipped gracefully
- The log message shows "Removed X/Y stale processing nodes" to indicate success ratio
- The system is protected from race conditions in multi-process scenarios

## Relevant ClickHouse Conventions

From `.claude/CLAUDE.md`:
- When writing code, wrap literal class names in backticks like `MergeTree`
- When writing function names, use `f` instead of `f()` for mathematical purity
- Data deletion events must be logged at appropriate levels (trace/debug)

From `.github/copilot-instructions.md`:
- All data deletion events must be logged
- Error handling paths must have proper observability (logs for serious failure modes)
- Changes to coordination/replication code need careful concurrency review
