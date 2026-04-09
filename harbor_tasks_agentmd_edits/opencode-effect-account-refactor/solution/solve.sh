#!/usr/bin/env bash
set -euo pipefail

cd /workspace/opencode

# Idempotent: skip if already applied
if grep -q '# opencode Effect guide' packages/opencode/AGENTS.md 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Download and apply the PR patch
curl -sL "https://github.com/anomalyco/opencode/pull/17072.diff" | git apply -

echo "Patch applied successfully."
