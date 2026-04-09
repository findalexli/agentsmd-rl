#!/usr/bin/env bash
set -euo pipefail

cd /workspace/posthog

# Idempotent: skip if already applied
if grep -q 'Summarize evaluation results' products/llm_analytics/mcp/tools.yaml 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# PR head commit is reachable from master (parent of merge commit 92dcf44).
# With --filter=blob:none clone, the commit object is local; git lazy-fetches blobs.
# Fallback: fetch from remote if not locally available.
git cat-file -e 30f37cacc13303efa00c346122805352deb049ff 2>/dev/null || \
    git fetch origin 30f37cacc13303efa00c346122805352deb049ff

mkdir -p products/llm_analytics/skills/exploring-llm-evaluations
git checkout 30f37cacc13303efa00c346122805352deb049ff -- \
  products/llm_analytics/mcp/tools.yaml \
  products/llm_analytics/skills/README.md \
  products/llm_analytics/skills/exploring-llm-evaluations/SKILL.md

echo "Patch applied successfully."
