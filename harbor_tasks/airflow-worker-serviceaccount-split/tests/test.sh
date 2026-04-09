#!/bin/bash
set -e

# Install pytest and dependencies
pip install pytest pyyaml -q

# Run tests and capture exit code properly (not in pipeline)
pytest /tests/test_outputs.py -v --tb=short > /logs/verifier/pytest_output.log 2>&1 || true

# Get exit code from log analysis or rerun
REWARD=$(pytest /tests/test_outputs.py -v --tb=line 2>&1 | grep -q "passed" && echo "1" || echo "0")

# More robust approach - run pytest directly and capture exit code
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
