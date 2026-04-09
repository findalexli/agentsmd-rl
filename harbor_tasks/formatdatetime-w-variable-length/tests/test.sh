#!/bin/bash
set -e

# Install pytest if needed
pip3 install pytest pyyaml -q

# Run tests
cd /workspace/task/tests
pytest test_outputs.py -v

# Write reward (1 = all tests passed, 0 = any failed)
exit_code=$?
if [ $exit_code -eq 0 ]; then
    echo "1" > /logs/verifier/reward
else
    echo "0" > /logs/verifier/reward
fi

exit $exit_code
