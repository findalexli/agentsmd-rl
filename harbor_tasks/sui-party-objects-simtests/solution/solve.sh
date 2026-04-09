#!/bin/bash
set -e

cd /workspace/sui

# Idempotency check: check if the distinctive new test function exists
if grep -q "async fn coin_deny_list_v2_party_owner_test" crates/sui-e2e-tests/tests/per_epoch_config_stress_tests.rs 2>/dev/null; then
    echo "Patch already applied, skipping..."
    exit 0
fi

# Run the Python patch script
python3 /solution/apply_patch.py

echo "Patch applied successfully"
