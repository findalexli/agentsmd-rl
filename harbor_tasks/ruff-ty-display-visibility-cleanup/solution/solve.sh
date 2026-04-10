#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ruff

# Idempotent: skip if already applied
# After patch, singleline method is private (no "pub") and has signature "fn singleline(&self)"
if grep -qE '^\s+fn singleline\(&self\)' crates/ty_python_semantic/src/types/display.rs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Apply the patch from the mounted patch file
git apply /solution/display.patch

echo "Patch applied successfully."
