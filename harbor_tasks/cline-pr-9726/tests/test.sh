#!/bin/bash
set -e

pip install pytest -q

cd /

pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /pytest_output.txt

if grep -q "PASSED" /pytest_output.txt && ! grep -q "FAILED" /pytest_output.txt; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
