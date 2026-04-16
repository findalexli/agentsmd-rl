#!/bin/bash
set -e

# Install pytest if not available
pip3 install pytest -q --break-system-packages 2>/dev/null || pip3 install pytest -q 2>/dev/null || true

# Run the test suite
cd /tests
python3 -m pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest.log

# Write binary reward: 1 if all tests pass, 0 otherwise
if grep -q "passed" /logs/verifier/pytest.log && ! grep -q "failed" /logs/verifier/pytest.log; then
    echo "1" > /logs/verifier/reward.txt
    echo "All tests passed - reward=1"
else
    echo "0" > /logs/verifier/reward.txt
    echo "Some tests failed - reward=0"
fi
