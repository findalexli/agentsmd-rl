#!/bin/bash
set -e

cd /workspace/containerd

# Install pytest if not already installed
pip install pytest --quiet 2>/dev/null || true

# Run the test suite and capture results
python3 -m pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest.log

# Check if all tests passed
if grep -q "passed" /logs/verifier/pytest.log && ! grep -q "FAILED" /logs/verifier/pytest.log; then
    echo "1" > /logs/verifier/reward.txt
    echo "All tests passed!"
else
    echo "0" > /logs/verifier/reward.txt
    echo "Some tests failed!"
fi
