#!/bin/bash
set -e

# Run pytest on test_outputs.py and write binary reward
cd /workspace
pytest -v /tests/test_outputs.py --tb=short 2>&1 | tail -20

# Write reward: 1 if all passed, 0 if any failed
if pytest /tests/test_outputs.py --tb=short -q 2>&1 | grep -q "failed"; then
    echo "0" > /logs/verifier/reward.txt
else
    echo "1" > /logs/verifier/reward.txt
fi
