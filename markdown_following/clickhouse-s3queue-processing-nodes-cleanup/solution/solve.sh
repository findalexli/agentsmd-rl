#!/bin/bash
set -e

cd /workspace/ClickHouse

# Check if fix is already applied (idempotency check)
if grep -q "nodes_to_remove.emplace_back" src/Storages/ObjectStorageQueue/ObjectStorageQueueMetadata.cpp; then
    echo "Fix already applied, skipping"
    exit 0
fi

# Apply the gold patch
cat << 'PATCH' | patch -p1
--- a/src/Storages/ObjectStorageQueue/ObjectStorageQueueMetadata.cpp
+++ b/src/Storages/ObjectStorageQueue/ObjectStorageQueueMetadata.cpp
@@ -1464,7 +1464,7 @@ void ObjectStorageQueueMetadata::cleanupPersistentProcessingNodes()
     }

     auto current_time = getCurrentTime();
-    Strings nodes_to_remove;
+    std::vector<std::pair<String, int32_t>> nodes_to_remove;
     Strings get_batch;
     auto get_paths = [&]
     {
@@ -1488,7 +1488,7 @@ void ObjectStorageQueueMetadata::cleanupPersistentProcessingNodes()
                 get_batch[i], response[i].stat.mtime, persistent_processing_node_ttl_seconds.load(), current_time);

             if (response[i].stat.mtime / 1000 + persistent_processing_node_ttl_seconds < current_time)
-                nodes_to_remove.push_back(get_batch[i]);
+                nodes_to_remove.emplace_back(get_batch[i], response[i].stat.version);
         }
         get_batch.clear();
     };
@@ -1517,18 +1517,26 @@ void ObjectStorageQueueMetadata::cleanupPersistentProcessingNodes()
         return;
     }

-    for (const auto & node : nodes_to_remove)
+    size_t removed = 0;
+    for (const auto & node_with_version : nodes_to_remove)
     {
+        const auto & node = node_with_version.first;
+        const auto version = node_with_version.second;
+        LOG_TRACE(log, "Removing stale processing node: {}", node);
         zk_retries.resetFailures();
         zk_retries.retryLoop([&]
         {
-            code = getZooKeeper(log)->tryRemove(node);
+            code = getZooKeeper(log)->tryRemove(node, version);
         });
-        if (code != Coordination::Error::ZOK && code != Coordination::Error::ZNONODE)
+        if (code == Coordination::Error::ZOK)
+            ++removed;
+        else if (code == Coordination::Error::ZNONODE || code == Coordination::Error::ZBADVERSION)
+            LOG_TRACE(log, "Processing node {} was already removed or recreated, skipping", node);
+        else
             throw zkutil::KeeperException::fromPath(code, node);
     }

-    LOG_DEBUG(log, "Removed {} persistent processing nodes", nodes_to_remove.size());
+    LOG_DEBUG(log, "Removed {}/{} stale processing nodes", removed, nodes_to_remove.size());
 }

 }
PATCH

echo "Patch applied successfully"
