#!/bin/bash
set -e

# Standard test runner for benchmark tasks
# This installs pytest and runs the test_outputs.py file

cd /workspace

# Ensure pytest is available
python3 -m pip install pytest pyyaml -q 2>/dev/null || true

# Create log directory
mkdir -p /logs/verifier

# Run the pytest tests
python3 -m pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest_output.txt

# Write reward file based on test results
# Count passed tests vs total tests
PASSED=$(grep -oP '\d+ passed' /logs/verifier/pytest_output.txt | grep -oP '\d+' || echo "0")
TOTAL=$(grep -oP 'collected \d+' /logs/verifier/pytest_output.txt | grep -oP '\d+' || echo "0")

if [ "$PASSED" = "$TOTAL" ] && [ "$TOTAL" -gt 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

echo "Tests completed: $PASSED / $TOTAL passed"
cat /logs/verifier/reward.txt
