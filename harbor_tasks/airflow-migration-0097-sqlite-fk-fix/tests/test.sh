#!/bin/bash
set -e

# Install pytest and dependencies
pip install pytest pytest-json-report -q

# Run tests with JSON output
cd /workspace/task
python -m pytest tests/test_outputs.py -v \
    --json-report \
    --json-report-file=/logs/verifier/results.json \
    -x 2>&1 | tee /logs/verifier/test_output.log

# Write binary reward file based on test results
if python -m pytest tests/test_outputs.py --tb=no -q 2>&1 | grep -q "passed"; then
    echo "1" > /logs/verifier/reward
else
    echo "0" > /logs/verifier/reward
fi
