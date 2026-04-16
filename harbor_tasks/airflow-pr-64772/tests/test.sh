#!/bin/bash
# Test runner for airflow-external-link-security task
# Runs pytest and writes binary reward (0 or 1) to /logs/verifier/reward.txt

# Ensure logs directory exists
mkdir -p /logs/verifier

# Run the tests
cd /tests
if python3 -m pytest test_outputs.py -v --tb=short; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
