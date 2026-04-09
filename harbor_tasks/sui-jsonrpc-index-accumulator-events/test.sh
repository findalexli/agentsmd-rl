#!/bin/bash
set -e

REPO=/workspace/sui
cd $REPO

# Install pytest if not already installed
pip3 install pytest --break-system-packages 2>/dev/null || true

# Run the tests
cd /workspace/task
python3 -m pytest tests/test_outputs.py -v 2>&1 | tee /logs/verifier/test_output.log

# Write binary reward based on test results
EXIT_CODE=${PIPESTATUS[0]}
if [ $EXIT_CODE -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
    echo "All tests passed!"
else
    echo "0" > /logs/verifier/reward.txt
    echo "Tests failed!"
fi

exit $EXIT_CODE
