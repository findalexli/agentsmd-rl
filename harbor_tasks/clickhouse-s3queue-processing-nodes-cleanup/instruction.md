# Task: Fix Race Condition in S3Queue Processing Node Cleanup

## Problem

When S3Queue cleans up stale ZooKeeper processing nodes, there's a potential race condition: a node might be modified or recreated between when we read its metadata and when we try to delete it. Currently, nodes are collected for removal without tracking their version numbers, which means concurrent modifications go undetected.

## Current Behavior

The stale node cleanup logic in `cleanupPersistentProcessingNodes` only tracks node paths and calls `tryRemove` with just the path. If a node is modified between read and delete, the deletion proceeds anyway because there's no version checking. The code only handles `ZNONODE` errors, not `ZBADVERSION` version mismatches.

## Required Behavior

Implement optimistic concurrency control for the cleanup process:

1. **Track node versions**: When identifying stale nodes, record both the node path AND its ZooKeeper stat version number (from the `version` field of the stat object).

2. **Use versioned deletions**: Pass the recorded version to `tryRemove` so ZooKeeper can reject the operation if the node was modified. On success (`ZOK`), count the removal.

3. **Handle version conflicts**: When `tryRemove` returns `ZBADVERSION` (version mismatch, meaning the node was modified), treat it as a non-fatal condition. Use `LOG_TRACE` to log that the node was already removed or recreated, then continue without throwing. Handle `ZBADVERSION` alongside the existing `ZNONODE` check.

4. **Log removal attempts**: Before attempting to remove each node, use `LOG_TRACE` to log that the node is being removed. The message should contain "Removing" and the node path.

5. **Track actual removals**: Count how many nodes are successfully removed versus how many were attempted. Use `LOG_DEBUG` to log a final summary showing both the count of successfully removed nodes and the total number of stale nodes that were targeted.

## Affected Code

The cleanup logic is in the S3Queue metadata handler source file. Locate the `cleanupPersistentProcessingNodes` function and apply the changes there.

## Verification

Your fix will be verified by checking that:
- The data structure for tracking nodes to remove stores version information
- The removal call uses version-aware deletion, passing the node path and version
- `ZBADVERSION` errors are handled gracefully alongside `ZNONODE` errors
- Removal attempts and skips are logged at trace level using `LOG_TRACE`
- The final summary log shows removed count vs total count using `LOG_DEBUG`
