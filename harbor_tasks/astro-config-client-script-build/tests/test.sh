#!/bin/bash
set -e

# Install pytest and dependencies (use --break-system-packages for container)
export PIP_BREAK_SYSTEM_PACKAGES=1
pip3 install pytest pytest-asyncio --quiet 2>/dev/null || \
    (python3 -m venv /tmp/venv && /tmp/venv/bin/pip install pytest pytest-asyncio)

# Run tests (use venv if created, otherwise system)
if [ -f /tmp/venv/bin/pytest ]; then
    /tmp/venv/bin/pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest.log || true
else
    pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest.log || true
fi

# Write binary reward (1 if no failures, 0 otherwise)
# Check for "FAILED" in the output
if grep -q "FAILED" /logs/verifier/pytest.log; then
    echo "0" > /logs/verifier/reward.txt
else
    echo "1" > /logs/verifier/reward.txt
fi

cat /logs/verifier/reward.txt
