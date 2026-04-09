#!/bin/bash
set -e

# Install pytest if needed
pip install pytest -q --break-system-packages

# Run the test suite, capture output and exit code
pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest_output.txt
PYTEST_EXIT=${PIPESTATUS[0]}

# Write binary reward
if [ $PYTEST_EXIT -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

exit $PYTEST_EXIT
