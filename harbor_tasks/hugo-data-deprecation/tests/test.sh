#!/bin/bash
set -e

# Install pytest if needed
pip3 install pytest --quiet --break-system-packages || pip3 install pytest --quiet || apt-get install -y python3-pytest

# Run the tests
cd /tests
if pytest test_outputs.py -v --tb=short; then
    # Write binary reward - all tests passed
    echo "1" > /logs/verifier/reward.txt
else
    # Write binary reward - some tests failed
    echo "0" > /logs/verifier/reward.txt
fi
