#!/bin/bash
set -e

cd /workspace/clickhouse

# Check if already applied (idempotency) - look for the specific fix pattern
if grep -q "right_symbol_index - possible_left_symbol_index + min_ngram_length - 1" src/Functions/sparseGramsImpl.h; then
    echo "Fix already applied"
    exit 0
fi

# Apply the gold patch
cat <<'PATCH' | git apply -
diff --git a/src/Functions/sparseGramsImpl.h b/src/Functions/sparseGramsImpl.h
index 3fb5fcb1e058..d71a9ae170a4 100644
--- a/src/Functions/sparseGramsImpl.h
+++ b/src/Functions/sparseGramsImpl.h
@@ -138,7 +138,7 @@ class SparseGramsImpl
         {
             size_t possible_left_position = convex_hull.back().left_ngram_position;
             size_t possible_left_symbol_index = convex_hull.back().symbol_index;
-            size_t length = right_symbol_index - possible_left_symbol_index + 2;
+            size_t length = right_symbol_index - possible_left_symbol_index + min_ngram_length - 1;
             if (length > max_ngram_length)
             {
                 /// If the current length is greater than the current right position, it will be greater at future right positions, so we can just delete them all.
@@ -157,7 +157,7 @@ class SparseGramsImpl
         {
             size_t possible_left_position = convex_hull.back().left_ngram_position;
             size_t possible_left_symbol_index = convex_hull.back().symbol_index;
-            size_t length = right_symbol_index - possible_left_symbol_index + 2;
+            size_t length = right_symbol_index - possible_left_symbol_index + min_ngram_length - 1;
             if (length <= max_ngram_length)
                 result.push_back({
                     .left_index = possible_left_position,
PATCH

echo "Fix applied successfully"
