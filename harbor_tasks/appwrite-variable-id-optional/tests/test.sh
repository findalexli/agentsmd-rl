#!/bin/bash
set -e

# Install pytest if not available
pip3 install pytest --break-system-packages 2>/dev/null || pip3 install pytest

# Run pytest and capture results
cd /workspace
if python3 -m pytest test_outputs.py -v 2>&1; then
    # All tests passed - write binary reward
    echo "PASS" > /logs/verifier/reward.bin
    echo "All tests passed!"
else
    # Some tests failed - write 0 reward
    printf '\x00\x00\x00\x00' > /logs/verifier/reward.bin
    echo "Some tests failed."
    exit 1
fi
