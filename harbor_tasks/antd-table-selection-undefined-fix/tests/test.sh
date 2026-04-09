#!/bin/bash
set -e

# Install pytest
cd /workspace/ant-design
pip3 install pytest --break-system-packages 2>/dev/null || pip3 install pytest

# Run tests and capture output
cd /tests
pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest.log

# Extract test results and write binary reward
# Check if all tests passed (no failures in output)
if grep -q "FAILED" /logs/verifier/pytest.log 2>/dev/null || grep -q "ERROR" /logs/verifier/pytest.log 2>/dev/null; then
    echo "0" > /logs/verifier/reward.txt
else
    # Check we actually ran tests
    if grep -q "passed" /logs/verifier/pytest.log; then
        echo "1" > /logs/verifier/reward.txt
    else
        echo "0" > /logs/verifier/reward.txt
    fi
fi

cat /logs/verifier/reward.txt
