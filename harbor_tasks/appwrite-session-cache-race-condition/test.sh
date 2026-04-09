#!/bin/bash
set -e

cd /workspace

# Install pytest if not already available
if ! command -v pytest &> /dev/null; then
    pip install pytest pyyaml 2>/dev/null || pip3 install pytest pyyaml 2>/dev/null
fi

# Run the tests
cd /workspace/task/tests
pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.log

# Write binary reward based on test results
exit_code=${PIPESTATUS[0]}
if [ $exit_code -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

exit $exit_code
