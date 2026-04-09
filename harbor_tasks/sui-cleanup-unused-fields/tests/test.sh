#!/bin/bash
set -e

cd /workspace

# Install pytest if not already available
pip3 install pytest -q 2>/dev/null || true

# Run the test suite
echo "Running test_outputs.py..."
python3 -m pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.log

# Write binary reward: 1 if all tests pass, 0 otherwise
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo "1" > /logs/verifier/reward
    echo "All tests passed!"
else
    echo "0" > /logs/verifier/reward
    echo "Some tests failed."
    exit 1
fi
