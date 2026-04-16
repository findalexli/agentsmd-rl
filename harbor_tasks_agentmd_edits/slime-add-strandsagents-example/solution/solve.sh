#!/usr/bin/env bash
set -euo pipefail

cd /workspace/{{REPO_SHORT}}

# Idempotent: skip if already applied
if grep -q '{{DISTINCTIVE_LINE}}' {{TARGET_FILE}} 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Use --whitespace=fix if patch has trailing whitespace issues
# IMPORTANT: patch content MUST end with a blank line before the PATCH delimiter
git apply - <<'PATCH'
{{PATCH_CONTENT}}

PATCH

echo "Patch applied successfully."
