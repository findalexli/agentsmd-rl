#!/usr/bin/env bash
set -euo pipefail

cd /workspace/deno

# Idempotent: skip if already applied
if [ -d "tests/bench_util" ] && [ ! -d "bench_util" ]; then
    echo "Patch already applied."
    exit 0
fi

# Apply patch from the external patch file
git apply /solution/patch.diff

# Stage all changes so git ls-files doesn't return deleted files
# This ensures the lint check passes because git sees the deletions
# as intentional changes rather than unstaged deletions
git add -A

echo "Patch applied successfully."
