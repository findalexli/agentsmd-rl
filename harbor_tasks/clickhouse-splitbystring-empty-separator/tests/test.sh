#!/bin/bash
set -e

# Install pytest if needed
pip3 install pytest pyyaml --break-system-packages -q 2>/dev/null || pip3 install pytest pyyaml -q

# Create logs directory
mkdir -p /logs/verifier

# Run tests and capture exit code
cd /tests
python3 -m pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest.log
exit_code=${PIPESTATUS[0]}

# Write binary reward based on test results
if [ $exit_code -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
