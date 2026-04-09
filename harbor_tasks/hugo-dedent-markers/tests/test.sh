#!/bin/bash
set -e

# Install pytest if needed
pip3 install pytest --quiet 2>/dev/null || pip install pytest --quiet 2>/dev/null

# Run the tests
cd /workspace/task/tests
python3 -m pytest test_outputs.py -v 2>&1 | tee /logs/verifier/test_output.log

# Extract test results and write binary reward
exit_code=${PIPESTATUS[0]}
if [ $exit_code -eq 0 ]; then
    echo "1" > /logs/verifier/reward
else
    echo "0" > /logs/verifier/reward
fi

exit $exit_code
