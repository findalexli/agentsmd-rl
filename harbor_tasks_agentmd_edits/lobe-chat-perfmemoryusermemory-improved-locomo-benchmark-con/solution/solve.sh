#!/usr/bin/env bash
set -euo pipefail

cd /workspace/lobe-chat

# Idempotent: skip if already applied
# Check for a distinctive line from the new query.ts file
if [ -f "packages/database/src/models/userMemory/query.ts" ]; then
    if grep -q 'scoreHybridCandidates' packages/database/src/models/userMemory/query.ts 2>/dev/null; then
        echo "Patch already applied."
        exit 0
    fi
fi

# Fetch and apply the PR patch
gh pr diff 13453 --repo lobehub/lobe-chat | git apply -

echo "Patch applied successfully."
