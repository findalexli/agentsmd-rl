#!/bin/bash
set -e

cd /workspace/ant-design

# Install Python dependencies for testing
pip install pytest requests pyyaml --quiet

# Run the test file
cd /workspace/task
python -m pytest tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.log

# Write binary reward based on test results
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo "{\"reward\": 1, \"status\": \"success\"}" > /workspace/task/status.json
else
    echo "{\"reward\": 0, \"status\": \"failure\"}" > /workspace/task/status.json
fi
