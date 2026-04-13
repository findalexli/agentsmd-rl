#!/bin/bash
# Run all tests and report results

set -e

cd /tests

# Run the Python tests with pytest
python3 -m pytest test_outputs.py -v --tb=short

# If we get here, all tests passed
echo "All tests passed!"
echo "1" > /logs/verifier/reward.txt
