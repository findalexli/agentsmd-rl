#!/bin/bash
# Run tests and output results to /logs/verifier/reward.txt

set -e

mkdir -p /logs/verifier

# Run pytest on test_outputs.py
if python -m pytest /tests/test_outputs.py -v --tb=short 2>&1; then
    echo "1" > /logs/verifier/reward.txt
    echo "All tests passed!"
else
    echo "0" > /logs/verifier/reward.txt
    echo "Some tests failed."
fi
