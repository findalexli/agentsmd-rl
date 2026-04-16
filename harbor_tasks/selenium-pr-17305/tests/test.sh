#!/bin/bash
# Test runner for selenium-dotnet-cdp-lazy-init task
set -e

# Install pytest if needed
pip3 install pytest -q 2>/dev/null || true

# Run tests
cd /tests
python3 -m pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.txt

# Check result
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
