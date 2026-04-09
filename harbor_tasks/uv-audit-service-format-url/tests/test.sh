#!/usr/bin/env bash
# Standardized test runner — do NOT modify this file per task.
# All test logic lives in test_outputs.py.
set +e

# Ensure python3 + pip + pytest are available on any base image
if ! python3 -c "import pytest" 2>/dev/null; then
    # Install python3 + pip if missing (node:slim, rust:slim)
    if ! command -v pip3 &>/dev/null; then
        apt-get update -qq && apt-get install -y -qq python3-pip python3-venv >/dev/null 2>&1 || true
    fi
    python3 -m pip install -q pytest pytest-json-ctrf 2>/dev/null ||         pip3 install -q --break-system-packages pytest pytest-json-ctrf 2>/dev/null
fi

python3 -m pytest --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py -rA --tb=short -q

if [ $? -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi
