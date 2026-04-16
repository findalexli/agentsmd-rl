#!/bin/bash
set -e

# Install pytest if not present
python3 -m pip install pytest --quiet --break-system-packages 2>/dev/null || python3 -m pip install pytest --quiet

# Run the tests
cd /tests
python3 -m pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.txt

# Check exit code and write reward
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
