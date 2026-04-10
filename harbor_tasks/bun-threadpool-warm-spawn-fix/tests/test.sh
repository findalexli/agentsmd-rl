#!/bin/bash
set -e

# Install pytest if needed
python3 -m pip install pytest -q --break-system-packages 2>/dev/null || pip install pytest -q --break-system-packages 2>/dev/null || apt-get install -y python3-pytest -qq 2>/dev/null || true

# Run tests
cd /workspace/bun
python3 -m pytest /tests/test_outputs.py -v 2>&1 | tee /logs/verifier/pytest.log

# Write binary reward
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
