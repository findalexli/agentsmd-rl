#!/usr/bin/env bash
# Standardized test runner — do NOT modify this file per task.
# All test logic lives in test_outputs.py.
set -euo pipefail

# Ensure python3 + pip + pytest are available on any base image
if ! python3 -c "import pytest" 2>/dev/null; then
    # Install python3 + pip if missing (node:slim, rust:slim)
    if ! command -v pip3 &>/dev/null; then
        apt-get update -qq && apt-get install -y -qq python3-pip python3-venv >/dev/null 2>&1 || true
    fi
    python3 -m pip install -q pytest 2>/dev/null || \
        pip3 install -q --break-system-packages pytest 2>/dev/null
fi

# Run tests and capture exit code
python3 -m pytest /tests/test_outputs.py -rA --tb=short -q > /logs/verifier/pytest_output.txt 2>&1 || true

# Check if tests passed by looking at the output
if grep -q "passed" /logs/verifier/pytest_output.txt && ! grep -qE "(FAILED|ERROR)" /logs/verifier/pytest_output.txt; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

cat /logs/verifier/pytest_output.txt
