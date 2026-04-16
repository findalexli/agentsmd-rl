#!/bin/bash
# Standardized test runner for benchmark tasks
# Runs pytest on test_outputs.py and writes binary reward

# Install pytest if not present
pip install --quiet pytest 2>/dev/null || true

# Run tests and capture exit code
cd /tests
python -m pytest test_outputs.py -v --tb=short
EXIT_CODE=$?

# Write binary reward based on test result
if [ $EXIT_CODE -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

exit 0
