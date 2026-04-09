#!/bin/bash
set -e

# Install pytest if needed
pip install pytest -q

# Run the tests
cd /workspace/task/tests
pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.log

# Write binary reward based on test results
exit_code=${PIPESTATUS[0]}
if [ $exit_code -eq 0 ]; then
    echo "{\"reward\": 1.0, \"status\": \"success\"}" > /logs/verifier/reward.json
else
    echo "{\"reward\": 0.0, \"status\": \"failure\"}" > /logs/verifier/reward.json
fi

exit $exit_code
