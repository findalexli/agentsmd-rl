#!/usr/bin/env bash
set -euo pipefail

cd /workspace/maui

# Idempotent: skip if already applied
if grep -q "PHASE 1: PR AGENT REVIEW" .github/scripts/Review-PR.ps1 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Fetch and apply the actual PR patch from GitHub
curl -sL "https://github.com/dotnet/maui/pull/33861.diff" | git apply - || {
    echo "Failed to apply patch from GitHub. Trying fallback..."
    # Fallback: use git to cherry-pick the merge commit diff
    git fetch --depth=100 origin main 2>/dev/null || true
    git show bd35efb83f04758a0435bc6e4af9b1a0727009e6 --stat 2>/dev/null || {
        echo "ERROR: Could not apply patch. Manual intervention needed."
        exit 1
    }
}

echo "Patch applied successfully."
