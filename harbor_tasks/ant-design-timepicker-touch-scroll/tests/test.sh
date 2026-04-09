#!/bin/bash
set -e

# Install pytest if not present
pip3 install pytest --quiet --break-system-packages 2>/dev/null || pip3 install pytest --quiet

# Run tests and capture output
cd /workspace/task/tests
pytest test_outputs.py -v 2>&1 | tee /logs/verifier/test_output.log

# Determine pass/fail and write reward
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo "1.0" > /logs/verifier/reward.txt
    echo "All tests passed!"
else
    echo "0.0" > /logs/verifier/reward.txt
    echo "Some tests failed."
    exit 1
fi
