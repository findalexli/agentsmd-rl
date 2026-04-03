#!/usr/bin/env bash
set -euo pipefail

cd /workspace/vllm

# Idempotency check
if grep -q '_partial_tag_overlap' vllm/tool_parsers/hermes_tool_parser.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Download and apply the PR patch
curl -sL "https://github.com/vllm-project/vllm/pull/38168.diff" -o /tmp/vllm-fix.patch
git apply --3way /tmp/vllm-fix.patch

echo "Patch applied successfully."
