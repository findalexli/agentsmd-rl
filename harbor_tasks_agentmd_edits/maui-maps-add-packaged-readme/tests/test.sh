#!/usr/bin/env bash

echo "=== Running test_outputs.py ==="
python3 -m pytest /tests/test_outputs.py -v --tb=short 2>&1
exit_code=$?

# Write reward based on test results
if [ $exit_code -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

exit $exit_code
