#!/usr/bin/env bash
set -euo pipefail

cd /workspace/opencode

# Idempotency check
if grep -q 'import { AppFileSystem }' packages/opencode/src/file/index.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Download and apply the PR patch
curl -sL "https://github.com/anomalyco/opencode/pull/19458.diff" -o /tmp/opencode-fix.patch
git apply --3way /tmp/opencode-fix.patch

echo "Patch applied successfully."
