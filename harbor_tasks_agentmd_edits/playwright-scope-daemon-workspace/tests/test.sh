#!/bin/sh
set -e

# Ensure reward log directory exists
mkdir -p /logs/verifier

# Use full path to pytest from venv
PYTEST=/opt/venv/bin/pytest

# Run pytest and capture result
if $PYTEST /tests/test_outputs.py -v 2>&1; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
