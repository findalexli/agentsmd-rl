#!/usr/bin/env bash
# Standard test harness — DO NOT add task-specific logic here.
set -u

mkdir -p /logs/verifier

if ! python3 -c "import pytest" 2>/dev/null; then
    pip3 install --break-system-packages --quiet pytest==8.3.4
fi

cd /tests

python3 -m pytest test_outputs.py -v --tb=short --no-header
exit_code=$?

if [ $exit_code -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

# --- LLM Judge ---
# (no judge configured for this task)
