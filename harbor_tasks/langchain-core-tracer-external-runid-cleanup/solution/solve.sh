#!/bin/bash
set -e

cd /workspace/langchain

# Check if already applied (idempotency)
if grep -q "_external_run_ids" libs/core/langchain_core/tracers/core.py; then
    echo "Patch already applied, skipping"
    exit 0
fi

# Apply the patch
git apply /solution/fix.patch

echo "Patch applied successfully"
