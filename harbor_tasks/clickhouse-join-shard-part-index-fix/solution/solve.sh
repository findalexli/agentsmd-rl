#!/bin/bash
# Apply the fix for optimizeJoinByShards part_index_in_query bug

set -e

# Clone the repo if it doesn't exist (for test environment)
if [ ! -d "/workspace/ClickHouse/.git" ]; then
    mkdir -p /workspace
    cd /workspace
    git clone --filter=blob:none --depth=100 https://github.com/ClickHouse/ClickHouse.git ClickHouse
fi

cd /workspace/ClickHouse

# Checkout the base commit if not already there
if [ "$(git rev-parse HEAD)" != "283163272e7318fb1825ebf1b68fdc510cd984d9" ]; then
    git checkout 283163272e7318fb1825ebf1b68fdc510cd984d9 2>/dev/null || true
fi

# Check if already applied (idempotency check using distinctive line)
if grep -q "Renumber part_index_in_query to be contiguous starting from added_parts" src/Processors/QueryPlan/Optimizations/optimizeJoinByShards.cpp 2>/dev/null; then
    echo "Fix already applied"
    exit 0
fi

# Apply the patch using a heredoc
cat <<'PATCH' > /tmp/fix.patch
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

# Apply the patch
git apply /tmp/fix.patch

echo "Fix applied successfully"
