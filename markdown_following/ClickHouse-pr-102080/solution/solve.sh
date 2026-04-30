#!/bin/bash
set -e

cd /workspace/ClickHouse

# Apply the gold patch for PR #102080
# Adds large file check to various_checks.sh

patch -p1 <<'PATCH'
diff --git a/ci/jobs/scripts/check_style/various_checks.sh b/ci/jobs/scripts/check_style/various_checks.sh
index 3e2250b171b6..111e446b62e6 100755
--- a/ci/jobs/scripts/check_style/various_checks.sh
+++ b/ci/jobs/scripts/check_style/various_checks.sh
@@ -246,3 +246,42 @@ done

 # CLICKHOUSE_URL already includes "?"
 git grep -P 'CLICKHOUSE_URL(|_HTTPS)(}|}/|/|)\?' $ROOT_PATH/tests/queries/0_stateless/*.sh && echo "CLICKHOUSE_URL already includes '?', use '&' to append query parameters"
+
+# Large files checked into git.
+# Every byte committed is cloned by every contributor forever and cannot be removed without history rewriting.
+# Binary blobs (JARs, archives, .so, datasets) should be downloaded at test time or built from source.
+MAX_FILE_SIZE=$((5 * 1024 * 1024))  # 5 MB
+LARGE_FILE_WHITELIST=(
+    # Legitimate test data that is hard to generate at runtime
+    -e multi_column_bf.gz.parquet
+    -e ghdata_sample.json
+    -e libcatboostmodel.so_aarch64
+    -e libcatboostmodel.so_x86_64
+    -e test_01946.zstd
+    -e e60db19f11f94175ac682c5898cce0f77cc508ea.tar.gz
+    -e npy_big.npy
+    -e string_int_list_inconsistent_offset_multiple_batches.parquet
+    -e known_failures.txt
+    -e keeper-java-client-test.jar
+    -e amazon_model.bin
+    -e nbagames_sample.json
+    -e 02731.arrow
+    -e aes-gcm-avx512.s
+    # TODO: these should be removed and the test should build the JAR from source at runtime
+    -e paimon-rest-catalog/chunk_
+)
+# GNU stat (Linux) uses -c, BSD stat (macOS) uses -f — detect once instead of failing per file.
+if stat -c '%s %n' /dev/null >/dev/null 2>&1; then
+    STAT_FMT_FLAG='-c'
+    STAT_FMT='%s %n'
+else
+    STAT_FMT_FLAG='-f'
+    STAT_FMT='%z %N'
+fi
+# Bulk stat all tracked files via xargs (avoids fork-per-file which takes minutes on large repos).
+git ls-files -z "$ROOT_PATH" | xargs -0 stat "$STAT_FMT_FLAG" "$STAT_FMT" 2>/dev/null \
+    | awk -v limit="$MAX_FILE_SIZE" '$1 > limit { print substr($0, index($0, $2)) }' \
+    | grep -v "${LARGE_FILE_WHITELIST[@]}" \
+    | while IFS= read -r file; do
+        echo "File $file is larger than 5 MB. Large files should not be committed to git — download them at test time or build from source instead."
+    done
PATCH

echo "Gold patch applied successfully"
