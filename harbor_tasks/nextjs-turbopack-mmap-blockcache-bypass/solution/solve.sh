#!/usr/bin/env bash
set -euo pipefail

cd /workspace/next.js

# Idempotent: skip if already applied
if grep -q 'struct ArcBlockCacheReader' turbopack/crates/turbo-persistence/src/static_sorted_file.rs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Apply the patch from the merge commit
git diff 16dd58fa25abf87ae891628ce018114a4c333db6..d75f07b3518a69691d3190f055ca2d30d700c56c -- turbopack/crates/turbo-persistence/src/static_sorted_file.rs | git apply -

echo "Patch applied successfully."
