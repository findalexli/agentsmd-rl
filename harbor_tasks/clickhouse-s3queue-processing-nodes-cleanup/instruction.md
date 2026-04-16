# Task: Fix S3Queue Processing Node Cleanup Race Condition

## Problem

The `cleanupPersistentProcessingNodes()` function in `src/Storages/ObjectStorageQueue/ObjectStorageQueueMetadata.cpp` has a race condition. When cleaning up stale ZooKeeper processing nodes, the current code collects stale node paths, then removes them — but does not verify that nodes haven't been modified between the read and delete steps. A node modified or recreated concurrently could be incorrectly cleaned up.

## Current Behavior

The function currently uses `Strings nodes_to_remove` to collect only the paths of stale nodes. During removal, it calls `tryRemove` with just the node path and only handles `Coordination::Error::ZNONODE` as a non-fatal error. This means concurrent modifications go undetected, and stale or recreated nodes can be incorrectly deleted.

## Required Behavior

Fix the race condition by implementing version-aware optimistic concurrency control. The corrected `cleanupPersistentProcessingNodes()` function must satisfy all of the following:

- **Store versions alongside paths**: Replace the `Strings nodes_to_remove` declaration with `std::vector<std::pair<String, int32_t>>` to hold each node's path and its ZooKeeper stat version number. When adding stale nodes to the collection, include both the path and the version from the stat object. The old `Strings nodes_to_remove;` declaration must not remain in the function.

- **Pass version to removal**: When calling `tryRemove`, pass both the node path and its recorded version so ZooKeeper can reject the delete if the node was modified.

- **Handle version mismatch**: Treat `Coordination::Error::ZBADVERSION` as a non-fatal condition alongside `Coordination::Error::ZNONODE`. When either error occurs, log at trace level: `"Processing node {} was already removed or recreated, skipping"` with the node path, then continue without throwing.

- **Log removal attempts**: Before each removal, log at trace level: `"Removing stale processing node: {}"` with the node path.

- **Track successful removals**: Count how many nodes are successfully removed (when the removal result is `Coordination::Error::ZOK`). The final `LOG_DEBUG` message must use the format `"Removed {}/{} stale processing nodes"` with the removed count and total count.

## Verification

Your fix will be verified by checking the source file for the patterns described above. Ensure the corrected code in `cleanupPersistentProcessingNodes()` implements all the described behavior.
