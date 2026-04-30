#!/bin/bash
# Standardized verifier: runs pytest, writes 0/1 to /logs/verifier/reward.txt
# from pytest's exit code directly.
set -u

mkdir -p /logs/verifier

cd /tests

# pytest + ctrf reporter are pre-installed in the Docker image.
python3 -m pytest \
    -v \
    --tb=short \
    --ctrf=/logs/verifier/ctrf.json \
    test_outputs.py

PYTEST_EXIT=$?

if [ "$PYTEST_EXIT" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

echo "--- pytest exit: $PYTEST_EXIT, reward: $(cat /logs/verifier/reward.txt) ---"
exit 0
