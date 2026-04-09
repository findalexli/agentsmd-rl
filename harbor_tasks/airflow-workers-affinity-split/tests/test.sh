#!/bin/bash
set -e

# Install pytest and dependencies if needed
pip install -q pytest jmespath pyyaml 2>/dev/null || true

# Run the tests - tests are mounted at /tests inside container
cd /tests
python -m pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest_output.txt

# Check exit code
exit_code=${PIPESTATUS[0]}

# Calculate reward - simple binary for now (1 if all tests pass, 0 if any fail)
if [ $exit_code -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

cat /logs/verifier/reward.txt
exit 0
