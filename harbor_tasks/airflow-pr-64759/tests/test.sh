#!/bin/bash
# Licensed under the Apache License, Version 2.0
# Standard test runner for benchmark tasks

set -e

# Install pytest if not available
pip install --quiet pytest pyyaml jmespath 2>/dev/null || true

# Run tests and capture result
cd /workspace/airflow
python -m pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.txt
TEST_RESULT=${PIPESTATUS[0]}

# Write reward based on test results
if [ $TEST_RESULT -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

exit 0
