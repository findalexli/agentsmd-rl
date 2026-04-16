#!/bin/bash
set -e

# Install pytest if not already installed
pip install pytest -q

# Run the tests, overriding the airflow pytest config
# Use -p no:asyncio to avoid conflicts with asyncio mode
cd /workspace/airflow
python -m pytest /tests/test_outputs.py -v --tb=short -p no:asyncio -p no:cacheprovider -o addopts="" 2>&1 | tee /logs/verifier/pytest_output.txt

# Write binary reward: 1 if all tests pass, 0 otherwise
if [ "${PIPESTATUS[0]}" -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
    echo "All tests passed! Reward = 1"
else
    echo "0" > /logs/verifier/reward.txt
    echo "Some tests failed. Reward = 0"
fi
