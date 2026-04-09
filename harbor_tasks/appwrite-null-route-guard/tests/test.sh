#!/bin/bash
set -e

# Install pytest if needed
pip install pytest -q 2>/dev/null || true

# Run the test script
cd /workspace
python3 -m pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.log

# Write binary reward based on exit code
exit_code=${PIPESTATUS[0]}
if [ $exit_code -eq 0 ]; then
    echo "1" > /logs/verifier/reward
    echo "All tests passed!"
else
    echo "0" > /logs/verifier/reward
    echo "Some tests failed."
fi

exit $exit_code
