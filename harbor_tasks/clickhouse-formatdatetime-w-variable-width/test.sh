#!/bin/bash
set -e

# Standard test runner - do not modify
# Installs pytest and runs test_outputs.py

cd /workspace

# Install pytest if not already available
pip3 install pytest --break-system-packages 2>/dev/null || pip3 install pytest

# Run the tests
cd /workspace/task/tests
python3 -m pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.log

# Write binary reward based on test results
if grep -q "passed" /logs/verifier/test_output.log && ! grep -q "FAILED" /logs/verifier/test_output.log; then
    echo "All tests passed"
    echo '{"reward": 1, "status": "success"}' > /logs/verifier/reward.json
else
    echo "Tests failed"
    echo '{"reward": 0, "status": "failure"}' > /logs/verifier/reward.json
fi
