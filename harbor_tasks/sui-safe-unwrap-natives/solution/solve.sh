#!/bin/bash
set -e

cd /workspace/sui

# Apply the official PR patch
git apply /solution/pr.diff

# Idempotency check - verify patch was applied by checking for safe_assert_eq macro definition
if ! grep -q "safe_assert_eq" external-crates/move/crates/move-binary-format/src/lib.rs; then
    echo "ERROR: Patch was not applied successfully"
    exit 1
fi

echo "Patch applied successfully"
