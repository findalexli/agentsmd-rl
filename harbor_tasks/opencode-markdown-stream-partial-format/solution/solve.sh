#!/usr/bin/env bash
set -euo pipefail

cd /workspace/opencode

# Idempotency check
if [ -f packages/ui/src/components/markdown-stream.ts ]; then
    echo "Patch already applied."
    exit 0
fi

# Download and apply the PR patch
curl -sL "https://github.com/anomalyco/opencode/pull/19403.diff" -o /tmp/opencode-fix.patch
git apply --3way /tmp/opencode-fix.patch

# Install the remend dependency
cd /workspace/opencode/packages/ui && bun add remend@1.3.0

echo "Patch applied successfully."
