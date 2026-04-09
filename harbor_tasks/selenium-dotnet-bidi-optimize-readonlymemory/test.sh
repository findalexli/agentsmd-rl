#!/bin/bash
set -e

cd /workspace/selenium

# Install pytest
pip3 install pytest --quiet

# Run the tests
python3 /workspace/task/tests/test_outputs.py "$@"

# Write binary reward
EXIT_CODE=$?
if [ $EXIT_CODE -eq 0 ]; then
    echo "0" > /logs/verifier/reward.txt
else
    echo "1" > /logs/verifier/reward.txt
fi

exit $EXIT_CODE
