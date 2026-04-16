#!/bin/bash
set -e

cd /workspace/payload

# Apply the gold patch
git apply /solution/gold.patch

# Verify the patch was applied
grep -q "oneToManyJoinedTableNames" packages/drizzle/src/find/findMany.ts || {
    echo "ERROR: Patch verification failed"
    exit 1
}

exit 0