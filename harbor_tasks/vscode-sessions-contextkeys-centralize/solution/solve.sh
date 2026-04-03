#!/usr/bin/env bash
set -euo pipefail

cd /workspace/vscode

# Idempotency check
if grep -q "ChatSessionProviderIdContext" src/vs/sessions/common/contextkeys.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Download and apply the PR patch
curl -sL "https://github.com/microsoft/vscode/pull/306439.diff" -o /tmp/vscode-fix.patch
git apply --3way /tmp/vscode-fix.patch

echo "Patch applied successfully."
