#!/bin/bash
set -e

# Install pytest if needed
pip3 install pytest --break-system-packages 2>/dev/null || pip3 install pytest 2>/dev/null || true

# Run the test
cd /workspace/ClickHouse
python3 -m pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest.log

# Write binary reward
if grep -q "PASSED" /logs/verifier/pytest.log && ! grep -q "FAILED" /logs/verifier/pytest.log; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
