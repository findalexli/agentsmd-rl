#!/bin/bash
set -e

# Install pytest
pip3 install pytest --quiet --break-system-packages

# Run the test file
cd /workspace/task
python3 -m pytest tests/test_outputs.py -v 2>&1 | tee /logs/verifier/test_output.log

# Write binary reward based on test results
exit_code=${PIPESTATUS[0]}
if [ $exit_code -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

exit $exit_code
