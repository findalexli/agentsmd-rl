#!/bin/bash
set -e

# Install pytest if not present
pip install pytest --quiet 2>/dev/null || true

# Run tests and capture results
cd /workspace/dagster/python_modules/libraries/dagster-hightouch
python3 -m pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.txt

# Write binary reward
if [ "${PIPESTATUS[0]}" -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
    echo "All tests passed!"
else
    echo "0" > /logs/verifier/reward.txt
    echo "Some tests failed."
fi

cat /logs/verifier/reward.txt
