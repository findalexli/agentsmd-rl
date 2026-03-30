#!/usr/bin/env bash
set -euo pipefail
cd /workspace/vllm

# Idempotent: skip if already applied
grep -q '_partial_tag_overlap' vllm/tool_parsers/hermes_tool_parser.py && exit 0

# Apply the gold patch from PR #38168
# The patch is large (full rewrite of streaming logic), so we cherry-pick
# the merge commit which contains only this PR's changes.
git fetch origin 4e54d75b4b6f --depth=1 2>/dev/null || \
    git fetch origin main --depth=50 2>/dev/null || true

# Try cherry-pick first
if git cherry-pick --no-commit 4e54d75b4b6f 2>/dev/null; then
    echo "Applied via cherry-pick"
    exit 0
fi

# Fallback: download and apply the PR patch
curl -sL "https://github.com/vllm-project/vllm/pull/38168.patch" | git apply --3way -
