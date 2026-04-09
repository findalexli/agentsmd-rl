#!/bin/bash

# Install pytest if needed
pip3 install pytest -q 2>/dev/null || true

# Run the test file - capture exit code
pytest /tests/test_outputs.py -v --tb=short
exit_code=$?

# Write binary reward based on pytest exit code
if [ $exit_code -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

exit $exit_code
