#!/bin/bash
# Standardized test runner for benchmark tasks

# Ensure pytest and ruff are available
pip install --quiet pytest pytest-timeout ruff 2>/dev/null || true

# Run tests and capture exit code
cd /workspace/superset
python -m pytest /tests/test_outputs.py -v --tb=short --timeout=300
PYTEST_EXIT_CODE=$?

# Determine reward based on test results
if [ $PYTEST_EXIT_CODE -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

exit $PYTEST_EXIT_CODE
