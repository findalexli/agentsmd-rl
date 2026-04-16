#!/bin/bash
set -e

# Install pytest if needed (using --break-system-packages for container environment)
pip3 install pytest --quiet --break-system-packages 2>/dev/null || pip3 install pytest --quiet 2>/dev/null || apt-get update && apt-get install -y python3-pytest --no-install-recommends 2>/dev/null || true

# Run tests and capture results
if python3 -m pytest /tests/test_outputs.py -v --tb=short 2>&1; then
    echo "1" > /logs/verifier/reward.txt
    echo "All tests passed!"
else
    echo "0" > /logs/verifier/reward.txt
    echo "Tests failed!"
    exit 1
fi
