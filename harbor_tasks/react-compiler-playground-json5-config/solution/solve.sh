#!/usr/bin/env bash
set -euo pipefail

cd /workspace/react

# Idempotency check
if grep -q "parseConfigOverrides" compiler/apps/playground/lib/compilation.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Download and apply the PR patch
curl -sL "https://github.com/facebook/react/pull/36159.diff" -o /tmp/react-fix.patch
git apply --3way /tmp/react-fix.patch

# Install json5 dependency
cd compiler/apps/playground
npm install --legacy-peer-deps 2>&1 || yarn install 2>&1 || true

echo "Patch applied successfully."
