#!/bin/bash
set -e

# Install pytest if not present
pip3 install pytest --break-system-packages 2>/dev/null || pip3 install pytest || true

# Run tests
cd /tests
python3 -m pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest.log

# Write binary reward (1 if all tests passed, 0 otherwise)
if grep -q "passed" /logs/verifier/pytest.log && ! grep -qE "(FAILED|ERROR)" /logs/verifier/pytest.log; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

cat /logs/verifier/reward.txt
