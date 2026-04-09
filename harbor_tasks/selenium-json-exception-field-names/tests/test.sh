#!/bin/bash

# Install pytest if needed
pip3 install pytest --break-system-packages 2>/dev/null || pip3 install pytest

# Run the test file - capture exit code without failing
pytest /tests/test_outputs.py -v --tb=short
EXIT_CODE=$?

# Write reward file based on pytest exit code
if [ $EXIT_CODE -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

# Return the actual exit code
exit $EXIT_CODE
