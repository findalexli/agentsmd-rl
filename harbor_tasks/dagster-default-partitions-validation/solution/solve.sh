#!/bin/bash
set -e

cd /workspace/dagster

# Apply the gold patch
patch -p1 << 'PATCH'
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
diff --git a/python_modules/dagster/dagster_tests/core_tests/asset_graph_view_tests/test_serializable_entity_subset.py b/python_modules/dagster/dagster_tests/core_tests/asset_graph_view_tests/test_serializable_entity_subset.py
index 14d4ce2da3b01..084af34d76cd9 100644
--- a/python_modules/dagster/dagster_tests/core_tests/asset_graph_view_tests/test_serializable_entity_subset.py
+++ b/python_modules/dagster/dagster_tests/core_tests/asset_graph_view_tests/test_serializable_entity_subset.py
@@ -2,6 +2,7 @@
 import pytest
 from dagster._check import CheckError
 from dagster._core.asset_graph_view.serializable_entity_subset import SerializableEntitySubset
+from dagster._core.definitions.partitions.subset import DefaultPartitionsSubset


 def test_union():
@@ -318,3 +319,38 @@ def test_from_coercible_value_dynamic_partitions():
             key=a,
             value=partitions_def.subset_with_partition_keys(["3"]),
         )
+
+
+def test_is_compatible_with_partitions_def_default_subset_time_window():
+    time_window_partitions_def = dg.DailyPartitionsDefinition(start_date="2024-01-01")
+    a = dg.AssetKey("a")
+
+    # DefaultPartitionsSubset with non-time keys should NOT be compatible
+    invalid_subset = SerializableEntitySubset(
+        key=a,
+        value=DefaultPartitionsSubset({"foo", "bar"}),
+    )
+    assert invalid_subset.is_compatible_with_partitions_def(time_window_partitions_def) is False
+
+    # DefaultPartitionsSubset with valid time keys should be compatible
+    valid_subset = SerializableEntitySubset(
+        key=a,
+        value=DefaultPartitionsSubset({"2024-01-01", "2024-01-02"}),
+    )
+    assert valid_subset.is_compatible_with_partitions_def(time_window_partitions_def) is True
+
+    # DefaultPartitionsSubset with mixed keys (some valid, some invalid) should NOT be compatible
+    mixed_subset = SerializableEntitySubset(
+        key=a,
+        value=DefaultPartitionsSubset({"2024-01-01", "invalid_key"}),
+    )
+    assert mixed_subset.is_compatible_with_partitions_def(time_window_partitions_def) is False
+
+    # DefaultPartitionsSubset with keys outside the partition range should NOT be compatible
+    out_of_range_subset = SerializableEntitySubset(
+        key=a,
+        value=DefaultPartitionsSubset({"2020-01-01"}),  # before start_date
+    )
+    assert (
+        out_of_range_subset.is_compatible_with_partitions_def(time_window_partitions_def) is False
+    )
PATCH

# Idempotency check - verify the distinctive line exists
grep -q "return all(partitions_def.has_partition_key(k) for k in self.value.subset)" \
    python_modules/dagster/dagster/_core/asset_graph_view/serializable_entity_subset.py

echo "Patch applied successfully"
