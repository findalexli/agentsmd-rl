#!/bin/bash
set -e

# Install pytest if not available
pip3 install pytest --break-system-packages 2>/dev/null || pip3 install pytest 2>/dev/null || pip install pytest

# Create log directory
mkdir -p /logs/verifier

# Run the tests
cd /workspace/superset/superset-frontend
python3 -m pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest.log

# Write binary reward based on test results
if grep -q "PASSED" /logs/verifier/pytest.log && ! grep -q "FAILED" /logs/verifier/pytest.log; then
    echo "1" > /logs/verifier/reward.txt
    echo "All tests passed!"
else
    echo "0" > /logs/verifier/reward.txt
    echo "Some tests failed"
fi
