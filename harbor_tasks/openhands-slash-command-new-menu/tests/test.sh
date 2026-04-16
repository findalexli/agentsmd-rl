#!/bin/bash
set -e

# Standard test runner - runs pytest and writes binary reward
pip install pytest --quiet --break-system-packages 2>/dev/null || pip3 install pytest --quiet --break-system-packages 2>/dev/null

# Run pytest on test_outputs.py and capture output
pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest_output.txt

# Write binary reward: 1 if all tests passed, 0 otherwise
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

cat /logs/verifier/reward.txt
