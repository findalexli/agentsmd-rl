#!/bin/bash
set -e

cd /workspace/OpenHands

# Install pytest if needed
pip3 install pytest -q 2>/dev/null || true

# Run the test suite
python3 -m pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.log

# Write binary reward based on test results
exit_code=${PIPESTATUS[0]}
if [ $exit_code -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
    echo "✓ All tests passed"
else
    echo "0" > /logs/verifier/reward.txt
    echo "✗ Some tests failed"
fi

exit $exit_code
