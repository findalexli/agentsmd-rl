#!/usr/bin/env bash
set -e

# Run pytest and capture result
if /opt/venv/bin/pytest /tests/test_outputs.py -v 2>&1; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

cat /logs/verifier/reward.txt
