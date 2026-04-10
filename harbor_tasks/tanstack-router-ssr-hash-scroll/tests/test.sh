#!/bin/bash
set -e

echo "=== Installing pytest ==="
pip3 install pytest --quiet --break-system-packages

echo "=== Running tests ==="
cd /tests
python3 -m pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.log

# Write binary reward file
# If pytest exits with 0 (all tests pass), reward is 1.0, else 0.0
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo "1.0" > /logs/verifier/reward.txt
    echo "=== All tests passed ==="
else
    echo "0.0" > /logs/verifier/reward.txt
    echo "=== Some tests failed ==="
fi
