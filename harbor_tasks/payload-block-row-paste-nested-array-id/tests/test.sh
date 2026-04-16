#!/bin/bash
set -e

# Install pytest
pip install -q pytest

# Run test_outputs.py and capture reward
python -m pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/output.txt

# Determine reward based on test results
if [ -f /logs/verifier/output.txt ]; then
    if grep -q "failed" /logs/verifier/output.txt; then
        echo "0" > /logs/verifier/reward.txt
    else
        echo "1" > /logs/verifier/reward.txt
    fi
else
    echo "0" > /logs/verifier/reward.txt
fi

cat /logs/verifier/reward.txt