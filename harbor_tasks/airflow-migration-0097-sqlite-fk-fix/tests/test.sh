#!/bin/bash
set -e

# Install pytest and dependencies
pip install pytest pytest-json-report -q

# Run tests with JSON output - ignore repo's pyproject.toml
cd /tests
python -m pytest test_outputs.py -v     -c /dev/null     --override-ini=addopts=     --json-report     --json-report-file=/logs/verifier/results.json     2>&1 | tee /logs/verifier/test_output.log

# Write binary reward file based on test results
# Reward is 1 only if ALL tests pass (no failures)
if python -m pytest test_outputs.py --tb=no -q -c /dev/null --override-ini=addopts= 2>&1 | grep -qE "failed|error"; then
    echo "0" > /logs/verifier/reward
else
    echo "1" > /logs/verifier/reward
fi
