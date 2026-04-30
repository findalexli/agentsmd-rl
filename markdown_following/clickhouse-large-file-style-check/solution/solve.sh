#!/bin/bash
# Gold solution: append the 5 MB size check to various_checks.sh and remove
# the unused 14 MB zookeeper_log.parquet test file.
set -euo pipefail

cd /workspace/clickhouse

SCRIPT=ci/jobs/scripts/check_style/various_checks.sh
PARQUET=tests/stress/keeper/workloads/zookeeper_log.parquet

# Idempotency: if the distinctive line is already there, do nothing.
if grep -q 'MAX_FILE_SIZE=\$((5 \* 1024 \* 1024))' "$SCRIPT"; then
    echo "size check already present"
else
    cat >>"$SCRIPT" <<'PATCH'

# Large files checked into git.
# Every byte committed is cloned by every contributor forever and cannot be removed without history rewriting.
# Binary blobs (JARs, archives, .so, datasets) should be downloaded at test time or built from source.
MAX_FILE_SIZE=$((5 * 1024 * 1024))  # 5 MB
LARGE_FILE_WHITELIST=(
    # Legitimate test data that is hard to generate at runtime
    -e multi_column_bf.gz.parquet
    -e ghdata_sample.json
    -e libcatboostmodel.so_aarch64
    -e libcatboostmodel.so_x86_64
    -e test_01946.zstd
    -e e60db19f11f94175ac682c5898cce0f77cc508ea.tar.gz
    -e npy_big.npy
    -e string_int_list_inconsistent_offset_multiple_batches.parquet
    -e known_failures.txt
    -e keeper-java-client-test.jar
    -e amazon_model.bin
    -e nbagames_sample.json
    -e 02731.arrow
    -e aes-gcm-avx512.s
    # TODO: these should be removed and the test should build the JAR from source at runtime
    -e paimon-rest-catalog/chunk_
)
# GNU stat (Linux) uses -c, BSD stat (macOS) uses -f — detect once instead of failing per file.
if stat -c '%s %n' /dev/null >/dev/null 2>&1; then
    STAT_FMT_FLAG='-c'
    STAT_FMT='%s %n'
else
    STAT_FMT_FLAG='-f'
    STAT_FMT='%z %N'
fi
# Bulk stat all tracked files via xargs (avoids fork-per-file which takes minutes on large repos).
git ls-files -z "$ROOT_PATH" | xargs -0 stat "$STAT_FMT_FLAG" "$STAT_FMT" 2>/dev/null \
    | awk -v limit="$MAX_FILE_SIZE" '$1 > limit { print substr($0, index($0, $2)) }' \
    | grep -v "${LARGE_FILE_WHITELIST[@]}" \
    | while IFS= read -r file; do
        echo "File $file is larger than 5 MB. Large files should not be committed to git — download them at test time or build from source instead."
    done
PATCH
fi

# Remove the unused 14 MB zookeeper_log.parquet (referenced only in a
# commented-out scenario that uses a different filename).
if [ -f "$PARQUET" ]; then
    git -c user.email=ci@example.com -c user.name=ci rm -q "$PARQUET" || rm -f "$PARQUET"
fi

# Commit so `git ls-files` reflects the deletion.
if ! git diff --quiet HEAD || [ -n "$(git status --porcelain)" ]; then
    git -c user.email=ci@example.com -c user.name=ci add -A
    git -c user.email=ci@example.com -c user.name=ci commit -q -m 'add size check, drop unused parquet' || true
fi

echo "solve.sh complete"
