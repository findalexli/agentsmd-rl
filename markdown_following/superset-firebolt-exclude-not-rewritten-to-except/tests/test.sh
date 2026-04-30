#!/bin/bash
# Test harness for the firebolt-exclude scaffold.
# Runs test_outputs.py via pytest and writes a binary reward to
# /logs/verifier/reward.txt based on pytest's exit code.
set -u

mkdir -p /logs/verifier

cd /tests
python -m pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest.log
PYTEST_EXIT=${PIPESTATUS[0]}

if [ "${PYTEST_EXIT}" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

echo "pytest exit: ${PYTEST_EXIT}; reward: $(cat /logs/verifier/reward.txt)"
