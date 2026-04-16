#!/bin/bash
set -e

REPO="ClickHouse"
cd /workspace/${REPO}

# Apply the fix for use-after-scope in parallel Object type deserialization
# This adds a SCOPE_EXIT block after task_size calculation to ensure proper cleanup

patch -p1 << 'PATCH'
diff --git a/src/DataTypes/Serializations/SerializationObject.cpp b/src/DataTypes/Serializations/SerializationObject.cpp
index 83e89e55de39..73c4f0471cc6 100644
--- a/src/DataTypes/Serializations/SerializationObject.cpp
+++ b/src/DataTypes/Serializations/SerializationObject.cpp
@@ -551,6 +551,16 @@ void SerializationObject::deserializeBinaryBulkStatePrefix(
         };

         size_t task_size = std::max(structure_state_concrete->sorted_dynamic_paths->size() / num_tasks, 1ul);
+
+        /// Ensure all already-scheduled tasks are drained on any exit path (including exceptions),
+        /// so pool threads do not dereference dangling references to stack locals.
+        SCOPE_EXIT(
+            for (const auto & task : tasks)
+                task->tryExecute();
+            for (const auto & task : tasks)
+                task->wait();
+        );
+
         for (size_t i = 0; i != num_tasks; ++i)
         {
             auto cache_copy = cache ? std::make_unique<SubstreamsDeserializeStatesCache>(*cache) : nullptr;
PATCH

# Verify the patch was applied by checking for the distinctive line
grep -q "Ensure all already-scheduled tasks are drained" src/DataTypes/Serializations/SerializationObject.cpp && echo "Fix applied successfully"
