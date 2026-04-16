#!/bin/bash

# Install pytest
python3 -m pip install pytest --quiet --disable-pip-version-check --break-system-packages 2>/dev/null || \
    pip3 install pytest --quiet --disable-pip-version-check --break-system-packages 2>/dev/null || true

# Run the test suite
cd /tests
if python3 -m pytest test_outputs.py -v --tb=short; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
