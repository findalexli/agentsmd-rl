#!/usr/bin/env bash
# Standardized test runner. Executes test_outputs.py via pytest and writes
# the binary reward to /logs/verifier/reward.txt based on pytest's exit code.
set -uo pipefail

mkdir -p /logs/verifier

cd /workspace/openhands

# Run pytest. Exit code is the source of truth for reward.
python -m pytest -v --tb=short \
    /tests/test_outputs.py \
    2>&1 | tee /logs/verifier/pytest.log

PYTEST_EXIT=${PIPESTATUS[0]}

if [ "${PYTEST_EXIT}" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

# CTRF report for the harness's per-test summary (if pytest-ctrf installed).
# Best-effort; absence is not fatal.
python -m pytest --tb=no -q \
    --json-report --json-report-file=/logs/verifier/pytest_report.json \
    /tests/test_outputs.py >/dev/null 2>&1 || true

exit 0
