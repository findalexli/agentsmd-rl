#!/bin/bash
set -e

cd /workspace/kotlin

# Install pytest if not available
pip3 install pytest --break-system-packages 2>/dev/null || pip3 install pytest 2>/dev/null || true

# Run the tests
cd /workspace
python3 -m pytest /workspace/tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.log

# Write binary reward based on test results
exit_code=${PIPESTATUS[0]}

if [ $exit_code -eq 0 ]; then
    echo "1" > /logs/verifier/reward
    echo "All tests passed!"
else
    echo "0" > /logs/verifier/reward
    echo "Some tests failed."
fi

exit $exit_code
