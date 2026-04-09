#!/bin/bash
set -e

# Install pytest if not available
pip3 install pytest --break-system-packages 2>/dev/null || pip3 install pytest

# Run the test suite
cd /workspace/task
python3 -m pytest tests/test_outputs.py -v 2>&1 | tee /logs/verifier/test_output.log

# Write binary reward: 1 if all tests pass, 0 otherwise
exit_code=${PIPESTATUS[0]}
if [ $exit_code -eq 0 ]; then
    echo "1.0" > /logs/verifier/reward.txt
    echo "All tests passed!"
else
    echo "0.0" > /logs/verifier/reward.txt
    echo "Some tests failed."
fi

exit $exit_code
