#!/bin/bash
set -e

cd /workspace/harbor_tasks/sui-framework-update-order

# Install pytest if needed
pip3 install --break-system-packages pytest -q 2>/dev/null || pip3 install pytest -q 2>/dev/null || true

# Run tests and output results
python3 -m pytest tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest_output.txt

# Write binary reward (0 or 1)
if python3 -m pytest tests/test_outputs.py --tb=short -q 2>&1 | grep -q "passed"; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
