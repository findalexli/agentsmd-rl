#!/bin/bash
set -e

# Install pytest and dependencies (including jsonschema for schema validation tests)
pip install pytest pyyaml jsonschema -q

# Run tests
set +e
pytest /tests/test_outputs.py --tb=no -q > /dev/null 2>&1
EXIT_CODE=$?
set -e

if [ $EXIT_CODE -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

cat /logs/verifier/reward.txt
