#!/bin/bash
set -e

# Setup
pip3 install pytest --quiet 2>/dev/null || true

cd /workspace/task/tests

# Run the tests and capture output
python3 -m pytest test_outputs.py -v --tb=short 2>&1 | tee /workspace/task/test_output.log

# Write reward based on test results
EXIT_CODE=${PIPESTATUS[0]}
if [ $EXIT_CODE -eq 0 ]; then
    echo "{\"reward\": 1.0, \"status\": \"pass\"}" > /workspace/task/reward.json
else
    echo "{\"reward\": 0.0, \"status\": \"fail\"}" > /workspace/task/reward.json
fi

exit $EXIT_CODE
