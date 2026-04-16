#!/bin/bash
set -e

# Install pytest if needed
pip install --quiet pytest 2>/dev/null || true

# Run the test outputs file
cd /tests
python -m pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest_output.txt

# Write binary reward (1 if all tests passed, 0 otherwise)
EXIT_CODE=${PIPESTATUS[0]}
if [ $EXIT_CODE -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

exit $EXIT_CODE
