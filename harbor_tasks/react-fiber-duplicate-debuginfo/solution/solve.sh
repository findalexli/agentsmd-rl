#!/usr/bin/env bash
set -euo pipefail

cd /workspace/react

# Idempotency check
if grep -q "We created a Fragment for this child with the debug info" packages/react-reconciler/src/ReactChildFiber.js 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Download and apply the PR patch
curl -sL "https://github.com/facebook/react/pull/35733.diff" -o /tmp/react-fix.patch
git apply --3way /tmp/react-fix.patch

echo "Patch applied successfully."
