#!/bin/bash
set -e

# Install pytest if needed
pip3 install pytest --break-system-packages -q 2>/dev/null || pip3 install pytest -q 2>/dev/null || true

# Create logs directory
mkdir -p /logs/verifier

# Run the test file
cd /workspace/cline
python3 -m pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest.log

# Write binary reward (1 if all tests passed, 0 otherwise)
if grep -q "passed" /logs/verifier/pytest.log && ! grep -q "FAILED" /logs/verifier/pytest.log; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

cat /logs/verifier/reward.txt
