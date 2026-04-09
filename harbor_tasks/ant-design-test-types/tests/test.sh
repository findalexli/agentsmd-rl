#!/bin/bash
set -e

# Install pytest if needed
pip3 install pytest --break-system-packages 2>/dev/null || pip3 install pytest

# Run the tests
cd /workspace/ant-design
pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest.log

# Determine pass/fail
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
    echo "SUCCESS: All tests passed"
else
    echo "0" > /logs/verifier/reward.txt
    echo "FAILURE: Some tests failed"
fi
