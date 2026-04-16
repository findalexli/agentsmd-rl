#!/bin/bash
# Standard test runner for benchmark tasks
# Runs pytest on test_outputs.py and writes binary reward

set -e

# Install pytest if not present
pip install --quiet pytest pyyaml jmespath 2>/dev/null || true

# Run tests
cd /tests
python -m pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.txt
TEST_RESULT=${PIPESTATUS[0]}

# Write binary reward
if [ $TEST_RESULT -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

exit 0
