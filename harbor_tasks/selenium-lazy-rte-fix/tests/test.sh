#!/bin/bash
set -e

echo "Installing pytest..."
pip3 install --break-system-packages pytest pyyaml --quiet 2>/dev/null || pip3 install pytest pyyaml --quiet

echo "Running tests..."
cd /workspace/task/tests
python3 -m pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.log

# Write binary reward (0 = fail, 1 = pass)
exit_code=${PIPESTATUS[0]}
if [ $exit_code -eq 0 ]; then
    echo 1 > /logs/verifier/reward
    echo "SUCCESS: All tests passed"
else
    echo 0 > /logs/verifier/reward
    echo "FAILURE: Some tests failed"
fi

exit $exit_code
