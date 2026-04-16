#!/bin/bash
set -e

# Run pytest and capture output
pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest_output.txt

# Count passed tests and write reward
PASSED=$(grep -c "PASSED" /logs/verifier/pytest_output.txt || true)
TOTAL=$(grep -c "test_" /tests/test_outputs.py || true)

# Calculate binary reward (1 if all pass, 0 otherwise)
if grep -q "failed\|ERROR" /logs/verifier/pytest_output.txt; then
    echo "0" > /logs/verifier/reward.txt
else
    echo "1" > /logs/verifier/reward.txt
fi

cat /logs/verifier/reward.txt
