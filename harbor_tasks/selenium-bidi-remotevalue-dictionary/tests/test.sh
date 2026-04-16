#!/bin/bash
set -e

# Activate venv if available
if [ -f /opt/venv/bin/activate ]; then
    source /opt/venv/bin/activate
fi

# Install pytest if not present
pip install pytest -q 2>/dev/null || true

# Run the tests
cd /tests
python3 -m pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.txt

# Write reward based on test results
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
