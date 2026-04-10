#!/bin/bash
set -e

# Install pytest if not available
pip3 install pytest --break-system-packages 2>/dev/null || pip3 install pytest

# Copy test file to workspace if mounted elsewhere
if [ -f /tests/test_outputs.py ]; then
    cp /tests/test_outputs.py /workspace/test_outputs.py
fi

# Run pytest and capture results
cd /workspace
if python3 -m pytest test_outputs.py -v 2>&1; then
    # All tests passed - write binary reward
    echo "PASS" > /logs/verifier/reward.bin
    echo "1" > /logs/verifier/reward.txt
    echo "All tests passed!"
else
    # Some tests failed - write 0 reward
    printf x00x00x00x00 > /logs/verifier/reward.bin
    echo "0" > /logs/verifier/reward.txt
    echo "Some tests failed."
    exit 1
fi
