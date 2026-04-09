#!/bin/bash
set -e

# Install pytest
pip install pytest pydantic docker httpx pybase62 fastapi -q

# Run tests
cd /workspace/OpenHands
python -m pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.log

# Write reward based on test results
exit_code=${PIPESTATUS[0]}
if [ $exit_code -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

exit $exit_code
