#!/bin/bash
set -e

# Install pytest if needed
pip3 install pytest pyyaml -q

# Run tests and capture exit code
# Use a subshell to capture the exit code properly with set -e
set +e
cd /workspace/task/tests
pytest test_outputs.py -v
exit_code=$?
set -e

# Write reward (1 = all tests passed, 0 = any failed)
if [ $exit_code -eq 0 ]; then
    echo "1" > /logs/verifier/reward
else
    echo "0" > /logs/verifier/reward
fi

exit $exit_code
