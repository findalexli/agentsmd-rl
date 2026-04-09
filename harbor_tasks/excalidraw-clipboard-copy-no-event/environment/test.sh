#!/bin/bash
set -e

# Install pytest and dependencies
cd /workspace
pip3 install pytest --quiet

# Run the test file
cd /workspace/excalidraw
python3 /workspace/task/tests/test_outputs.py 2>&1 | tee /logs/verifier/test_output.log

# Write binary reward based on pytest exit code
EXIT_CODE=${PIPESTATUS[0]}
if [ $EXIT_CODE -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

exit $EXIT_CODE
