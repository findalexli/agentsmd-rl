#!/bin/bash
set -e

# Install pytest using apt or pip with --break-system-packages
pip3 install pytest --quiet --break-system-packages 2>/dev/null || apt-get update && apt-get install -y python3-pytest 2>/dev/null || true

# Run the tests
cd /tests
python3 -m pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest_output.txt

# Write binary reward: 1 if all tests pass, 0 otherwise
if grep -q "passed" /logs/verifier/pytest_output.txt && ! grep -q "FAILED" /logs/verifier/pytest_output.txt; then
    echo "1" > /logs/verifier/reward.txt
    echo "SUCCESS: All tests passed"
else
    echo "0" > /logs/verifier/reward.txt
    echo "FAILURE: Some tests failed"
fi
