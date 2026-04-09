#!/bin/bash
set -e

cd /workspace/ClickHouse

# Apply the gold patch for optimizeJoinByShards.cpp fix
patch -p1 <<'PATCH'
diff --git a/src/Processors/QueryPlan/Optimizations/optimizeJoinByShards.cpp b/src/Processors/QueryPlan/Optimizations/optimizeJoinByShards.cpp
index 38de6d836d0b..6379e02aa370 100644
--- a/src/Processors/QueryPlan/Optimizations/optimizeJoinByShards.cpp
+++ b/src/Processors/QueryPlan/Optimizations/optimizeJoinByShards.cpp
@@ -238,10 +238,14 @@ static void apply(struct JoinsAndSourcesWithCommonPrimaryKeyPrefix & data)
             analysis_result = source->selectRangesToRead();

         size_t added_parts = all_parts.size();
-        for (const auto & part : analysis_result->parts_with_ranges)
+        /// Renumber part_index_in_query to be contiguous starting from added_parts.
+        /// filterPartsByQueryConditionCache may drop parts from selectRangesToRead(),
+        /// leaving non-contiguous part_index_in_query values. The distribution logic
+        /// below assumes contiguous indices to assign parts back to their sources.
+        for (size_t local_idx = 0; local_idx < analysis_result->parts_with_ranges.size(); ++local_idx)
         {
-            all_parts.push_back(part);
-            all_parts.back().part_index_in_query += added_parts;
+            all_parts.push_back(analysis_result->parts_with_ranges[local_idx]);
+            all_parts.back().part_index_in_query = added_parts + local_idx;
         }

         analysis_results.push_back(std::move(analysis_result));
PATCH

# Verify the patch was applied by checking for the distinctive line
grep -q "Renumber part_index_in_query to be contiguous" src/Processors/QueryPlan/Optimizations/optimizeJoinByShards.cpp

echo "Patch applied successfully"
