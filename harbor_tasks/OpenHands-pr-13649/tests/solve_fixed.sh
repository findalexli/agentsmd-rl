#!/bin/bash
set -e

cd /workspace/openhands

# Check if patch was already applied (idempotency check)
# The fix moves "const amount" and "const sessionId" to be adjacent to "const checkoutStatus"
if grep -A1 "const checkoutStatus = searchParams.get(\"checkout\");" frontend/src/routes/billing.tsx | grep -q "const amount = searchParams.get"; then
    echo "Patch already applied, skipping..."
    exit 0
fi

# Apply the fixes using Python scripts
python3 /tests/fix_billing.py
python3 /tests/fix_billing_test.py

echo "Patch applied successfully!"
