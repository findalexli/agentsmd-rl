#!/bin/bash
set -e

# Install pytest if not present
pip install pytest httpx orjson -q

# Run tests
cd /workspace/langgraph/libs/sdk-py
python -m pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest_output.txt

# Write binary reward based on test results
exit_code=${PIPESTATUS[0]}
if [ $exit_code -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
    echo "All tests passed - reward=1"
else
    echo "0" > /logs/verifier/reward.txt
    echo "Some tests failed - reward=0"
fi

exit 0
