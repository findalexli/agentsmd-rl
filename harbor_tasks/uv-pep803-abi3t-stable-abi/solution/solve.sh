#!/usr/bin/env bash
set -euo pipefail

cd /workspace/uv

# Idempotent: skip if already applied
if grep -q "is_stable_abi" crates/uv-platform-tags/src/abi_tag.rs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Download and apply the PR diff from GitHub
curl -sL https://github.com/astral-sh/uv/pull/18767.diff > /tmp/pr.diff
git apply /tmp/pr.diff

echo "Patch applied successfully."
