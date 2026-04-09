#!/bin/bash
set -e

# Create logs directory
mkdir -p /logs/verifier

# Run the test file with pytest
cd /workspace/router
python3 /tests/test_outputs.py -v

# Write binary reward based on test results
exit_code=$?
if [ $exit_code -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

exit $exit_code
