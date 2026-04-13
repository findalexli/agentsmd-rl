#!/bin/bash
# Test runner for the task

set -e

cd /tests

# Run pytest with verbose output
python -m pytest test_outputs.py -v 2>&1

exit_code=$?

# Log result for external verifier
if [ -d "/logs/verifier" ]; then
    if [ $exit_code -eq 0 ]; then
        echo "1" > /logs/verifier/reward.txt
    else
        echo "0" > /logs/verifier/reward.txt
    fi
fi

exit $exit_code
