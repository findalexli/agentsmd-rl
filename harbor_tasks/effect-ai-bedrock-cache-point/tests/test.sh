#!/bin/bash
set -e

pip install pytest -q

cd /

python -m pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /tmp/pytest.out

# Write binary reward
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo -n "1" > /logs/verifier/reward.txt
else
    echo -n "0" > /logs/verifier/reward.txt
fi