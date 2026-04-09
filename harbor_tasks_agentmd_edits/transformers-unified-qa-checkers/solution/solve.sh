#!/usr/bin/env bash
set -euo pipefail

cd /workspace/transformers

# Idempotent: skip if already applied
if [ -f utils/checkers.py ]; then
    echo "Patch already applied."
    exit 0
fi

# Apply the exact diff between base commit and merge commit.
# Both commits are reachable in the blob-less clone.
git diff 28af8184fb00a0e9bc778c3defdec39bbe7e8839 b3d7942fbaedda791668d7fe42eaaa323ed7a089 | git apply --whitespace=fix

echo "Patch applied successfully."
