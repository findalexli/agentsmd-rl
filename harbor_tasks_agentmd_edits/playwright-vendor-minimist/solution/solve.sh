#!/bin/bash
set -e

cd /workspace/playwright

# Check if already patched (idempotency)
if [ -f "packages/playwright-core/src/tools/cli-client/minimist.ts" ]; then
    echo "Gold patch already applied"
    exit 0
fi

# Apply the gold patch
cd /workspace/playwright
git apply /solution/gold.patch

echo "Gold patch applied successfully"
