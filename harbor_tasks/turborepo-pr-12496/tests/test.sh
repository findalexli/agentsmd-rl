#!/bin/bash
set -e

# Install pytest
pip3 install pytest --break-system-packages --quiet

# Run test_outputs.py and write binary reward
cd /
python3 -m pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/output.txt
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo -n -e '\x01' > /logs/verifier/reward.txt
else
    echo -n -e '\x00' > /logs/verifier/reward.txt
fi