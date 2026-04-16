#!/bin/bash

cd /workspace

pip install pytest --quiet

# Run pytest, capture exit code but don't exit on failure
pytest -v --tb=short /tests/test_outputs.py || pytest_exit=$?

# Write binary reward based on test results
if [ -f /logs/verifier/reward.txt ]; then
    reward=$(cat /logs/verifier/reward.txt)
    echo "Reward: $reward"
else
    # If pytest passed (no exit code or 0), reward=1; if failed, reward=0
    if [ -z "$pytest_exit" ] || [ "$pytest_exit" -eq 0 ]; then
        echo "1" > /logs/verifier/reward.txt
    else
        echo "0" > /logs/verifier/reward.txt
    fi
    echo "Reward written based on pytest exit code: ${pytest_exit:-0}"
fi
