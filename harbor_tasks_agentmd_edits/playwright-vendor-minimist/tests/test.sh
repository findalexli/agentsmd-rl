#!/bin/bash
set -e

# Run pytest tests and capture exit code
python3 /tests/test_outputs.py -v
PYTEST_EXIT=$?

# Write reward based on pytest exit code
if [ $PYTEST_EXIT -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

exit $PYTEST_EXIT
