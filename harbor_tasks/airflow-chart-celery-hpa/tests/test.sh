#!/bin/bash
set -e

# Install pytest if needed
pip install pytest jmespath pyyaml --quiet 2>/dev/null || true

# Run the tests
cd /workspace/airflow
pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest_output.log

# Write binary reward
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
