#!/usr/bin/env bash
set -euo pipefail

cd /workspace/prime-rl

# Idempotent: skip if already applied (CheckpointManager class exists)
if grep -q 'class CheckpointManager:' src/zeroband/training/ckpt.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Apply the full diff patch from PR #536
git apply --ignore-space-change /solution/full_diff.patch

echo "Patch applied successfully."
