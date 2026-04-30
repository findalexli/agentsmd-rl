#!/usr/bin/env bash
# Standardized verifier test runner — DO NOT customize.
set -uo pipefail

mkdir -p /logs/verifier

# pytest is preinstalled in the image; if for some reason it's missing,
# fail loudly rather than silently.
if ! command -v pytest >/dev/null 2>&1; then
    pip3 install --no-cache-dir --break-system-packages pytest==8.3.4 pytest-json-report==1.5.0
fi

cd /tests
pytest -v --tb=short --json-report --json-report-file=/logs/verifier/ctrf.json test_outputs.py
PYTEST_RC=$?

if [ $PYTEST_RC -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

# --- LLM Judge ---
# The standalone_judge.py file is read by the harness if present; we don't
# invoke it from this script. The reward above is the binary signal.
exit 0
