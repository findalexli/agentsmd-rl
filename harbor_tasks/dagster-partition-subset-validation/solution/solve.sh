#!/bin/bash
set -e

cd /workspace/dagster

# Apply the gold patch
patch -p1 <<'PATCH'
diff --git a/python_modules/dagster/dagster/_core/asset_graph_view/serializable_entity_subset.py b/python_modules/dagster/dagster/_core/asset_graph_view/serializable_entity_subset.py
index 6ebb4821734b0..365a6462487c6 100644
--- a/python_modules/dagster/dagster/_core/asset_graph_view/serializable_entity_subset.py
+++ b/python_modules/dagster/dagster/_core/asset_graph_view/serializable_entity_subset.py
@@ -132,6 +132,10 @@ def is_empty(self) -> bool:
     def is_compatible_with_partitions_def(
         self, partitions_def: Optional[PartitionsDefinition]
     ) -> bool:
+        from dagster._core.definitions.partitions.definition.time_window import (
+            TimeWindowPartitionsDefinition,
+        )
+
         if self.is_partitioned:
             # for some PartitionSubset types, we have access to the underlying partitions
             # definitions, so we can ensure those are identical
@@ -150,6 +154,11 @@ def is_compatible_with_partitions_def(
                     and partitions_def.has_partition_key(r.end)
                     for r in self.value.key_ranges
                 )
+            elif isinstance(self.value, DefaultPartitionsSubset) and isinstance(
+                partitions_def, TimeWindowPartitionsDefinition
+            ):
+                return all(partitions_def.has_partition_key(k) for k in self.value.subset)
+
             else:
                 return partitions_def is not None
         else:
PATCH

# Idempotency check: verify the distinctive line is present
grep -q "isinstance(self.value, DefaultPartitionsSubset)" python_modules/dagster/dagster/_core/asset_graph_view/serializable_entity_subset.py

echo "Patch applied successfully"
