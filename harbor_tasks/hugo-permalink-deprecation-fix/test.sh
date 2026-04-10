#!/bin/bash
set -e

# Install pytest (with --break-system-packages for externally-managed Python)
pip3 install pytest --quiet --break-system-packages 2>/dev/null || pip3 install pytest --quiet

# Copy test file to the expected location
mkdir -p /workspace/task/tests
cp /workspace/task/test_outputs.py /workspace/task/tests/test_outputs.py

# Run the tests
cd /workspace/task
python3 -m pytest tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.log

# Write binary reward based on test result
exit_code=${PIPESTATUS[0]}
if [ $exit_code -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
    echo "SUCCESS: All tests passed"
else
    echo "0" > /logs/verifier/reward.txt
    echo "FAILURE: Some tests failed"
fi

exit $exit_code
