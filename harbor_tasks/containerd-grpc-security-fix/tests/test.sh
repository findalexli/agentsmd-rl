#!/bin/bash
set -e

# Install pytest if not available
pip3 install pytest --quiet --break-system-packages 2>/dev/null || pip3 install pytest --quiet 2>/dev/null || true

# Run tests and capture results
cd /tests
python3 -m pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.log

# Write binary reward file (1 if all tests pass, 0 otherwise)
if python3 -m pytest test_outputs.py --tb=short -q 2>&1 | grep -q "passed"; then
    echo "1" > /logs/verifier/reward
else
    echo "0" > /logs/verifier/reward
fi
