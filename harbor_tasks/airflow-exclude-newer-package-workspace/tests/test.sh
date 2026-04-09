#!/bin/bash

# Install pytest if needed
pip install pytest -q

# Run tests and capture exit code
pytest /tests/test_outputs.py -v --tb=short
exit_code=$?

# Write binary reward
if [ $exit_code -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

exit $exit_code
