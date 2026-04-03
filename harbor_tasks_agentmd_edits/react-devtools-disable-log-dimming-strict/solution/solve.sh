#!/usr/bin/env bash
set -euo pipefail

cd /workspace/react

# Idempotent: skip if already applied
if grep -q 'disableSecondConsoleLogDimmingInStrictMode' packages/react-devtools-shared/src/hook.js 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Apply the full PR diff from GitHub
curl -sL "https://github.com/facebook/react/pull/35207.diff" | git apply --whitespace=fix -

echo "Patch applied successfully."
