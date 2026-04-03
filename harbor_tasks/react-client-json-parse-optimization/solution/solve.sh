#!/usr/bin/env bash
set -euo pipefail

cd /workspace/react

# Idempotency check
if grep -q "function reviveModel(" packages/react-client/src/ReactFlightClient.js 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Download and apply the PR patch
curl -sL "https://github.com/facebook/react/pull/35776.diff" -o /tmp/react-fix.patch
git apply --3way /tmp/react-fix.patch

echo "Patch applied successfully."
