#!/bin/bash
set -eo pipefail

# Install pytest if needed and run tests
pip3 install pytest --break-system-packages 2>/dev/null || pip3 install pytest

cd /tests
if pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest_output.txt; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
