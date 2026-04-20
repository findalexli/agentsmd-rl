#!/bin/bash

# Run pytest on test_outputs.py (mounted at /tests by harness)
set +e
python -m pytest /tests/test_outputs.py -v --tb=short
PYTEST_EXIT=$?
set -e

# Write binary reward based on pytest exit code
if [ $PYTEST_EXIT -eq 0 ]; then
    echo -n 1 > /logs/verifier/reward.txt
else
    echo -n 0 > /logs/verifier/reward.txt
fi
