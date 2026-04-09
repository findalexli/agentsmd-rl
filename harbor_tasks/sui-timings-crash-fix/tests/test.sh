#!/bin/bash
set -e
pip3 install pytest --break-system-packages 2>/dev/null || pip3 install pytest || true
cd /tests
if python3 test_outputs.py; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
