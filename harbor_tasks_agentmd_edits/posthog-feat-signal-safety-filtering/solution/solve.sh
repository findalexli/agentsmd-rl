#!/usr/bin/env bash
set -euo pipefail

cd /workspace/posthog

# Idempotent: skip if already applied
if [ -f products/signals/backend/temporal/safety_filter.py ]; then
    echo "Patch already applied."
    exit 0
fi

# Apply the patch from file
git apply --whitespace=fix /solution/pr.patch 2>&1 || {
    echo "Git apply failed, trying with 3-way merge..."
    git apply --3way /solution/pr.patch 2>&1 || {
        echo "All patch methods failed"
        exit 1
    }
}

echo "Patch applied successfully."
