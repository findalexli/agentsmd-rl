#!/bin/bash
# Standardized harness — DO NOT MODIFY.
set +e
mkdir -p /logs/verifier

if ! python3 -c "import pytest" 2>/dev/null; then
    pip3 install --break-system-packages --no-cache-dir --quiet pytest==8.3.4 pytest-json-ctrf==0.4.1
fi

cd /tests
python3 -m pytest -v --tb=short test_outputs.py --ctrf /logs/verifier/ctrf.json
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi
