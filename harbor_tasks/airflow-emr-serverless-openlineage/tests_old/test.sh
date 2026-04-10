#!/bin/bash
set -e

# Install pytest if needed
pip install pytest mock time-machine openlineage-client -q

# Run the tests
cd /workspace/task/tests
python -m pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.log

# Extract the result
exit_code=${PIPESTATUS[0]}

# Write binary reward
if [ $exit_code -eq 0 ]; then
    echo "1" > /logs/verifier/reward
else
    echo "0" > /logs/verifier/reward
fi

exit $exit_code
