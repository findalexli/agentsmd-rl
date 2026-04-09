#!/bin/bash
set -e

cd /workspace/ClickHouse

# Apply the fix for materialize_skip_indexes_on_merge not suppressing text indexes
cat <<'PATCH' | git apply -
diff --git a/src/Storages/MergeTree/MergeTask.cpp b/src/Storages/MergeTree/MergeTask.cpp
index e08f608b4778..37688ca50801 100644
--- a/src/Storages/MergeTree/MergeTask.cpp
+++ b/src/Storages/MergeTree/MergeTask.cpp
@@ -883,6 +883,7 @@ bool MergeTask::ExecuteAndFinalizeHorizontalPart::prepare() const
     {
         global_ctx->merging_skip_indexes.clear();
         global_ctx->skip_indexes_by_column.clear();
+        global_ctx->text_indexes_to_merge.clear();
     }

     bool use_adaptive_granularity = global_ctx->new_data_part->index_granularity_info.mark_type.adaptive;
PATCH

# Verify the patch was applied by checking for the distinctive line
grep -q "text_indexes_to_merge.clear()" src/Storages/MergeTree/MergeTask.cpp && echo "Patch applied successfully"
