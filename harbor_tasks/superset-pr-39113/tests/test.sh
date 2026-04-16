#!/bin/bash
set -e

# Install pytest if needed
pip install --quiet pytest pytest-timeout 2>/dev/null || true

# Run tests and capture result
cd /tests
python -m pytest test_outputs.py -v --tb=short --timeout=300 2>&1 | tee /logs/verifier/test_output.txt
TEST_RESULT=${PIPESTATUS[0]}

# Write binary reward
if [ $TEST_RESULT -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

exit 0
