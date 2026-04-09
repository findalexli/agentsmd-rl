#!/bin/bash
set -e

# Install pytest if not available
pip3 install pytest --quiet

# Run tests and capture results
cd /workspace/task
python3 -m pytest tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.log

# Write binary reward file based on test results
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo "1.0" > /logs/verifier/reward.txt
    echo "All tests passed"
else
    echo "0.0" > /logs/verifier/reward.txt
    echo "Some tests failed"
fi
