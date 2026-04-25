#!/bin/sh

# Create log directory
mkdir -p /logs/verifier

# Run tests and capture output (need to check pytest exit code directly)
cd /tests
python3 -m pytest test_outputs.py -v --tb=short > /logs/verifier/test_output.log 2>&1
exit_code=$?

if [ $exit_code -eq 0 ]; then
    cat /logs/verifier/test_output.log
    echo ""
    echo "1" > /logs/verifier/reward.txt
    echo "SUCCESS: All tests passed"
else
    cat /logs/verifier/test_output.log
    echo ""
    echo "0" > /logs/verifier/reward.txt
    echo "FAILURE: Some tests failed"
fi
