#!/bin/bash
set -e

# Install pytest if needed
pip3 install pytest --quiet --break-system-packages 2>/dev/null || pip3 install pytest --quiet

# Run tests and capture output
pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /tmp/pytest_output.txt

# Write binary reward
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
    echo "PASS: All tests passed"
else
    echo "0" > /logs/verifier/reward.txt
    echo "FAIL: Some tests failed"
fi
