#!/usr/bin/env bash
set -euo pipefail

cd /workspace/playwright

# Idempotent: skip if already applied
if grep -q 'AttachOptions' packages/playwright-core/src/tools/cli-client/program.ts 2>/dev/null; then
    echo 'Patch already applied.'
    exit 0
fi

# Copy fix script from solution mount point and run it
cp /solution/fix.js /tmp/fix.js
node /tmp/fix.js
echo 'Patch applied successfully.'
