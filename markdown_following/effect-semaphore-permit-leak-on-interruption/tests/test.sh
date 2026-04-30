#!/usr/bin/env bash
# Standardized test runner. Writes /logs/verifier/reward.txt as literal "0" or "1"
# from pytest's exit code.
set -u
mkdir -p /logs/verifier

# pytest + pyyaml are pre-installed in /opt/venv during the Dockerfile build.
# Do NOT install anything at test time (no network needed).
export PATH=/opt/venv/bin:$PATH

cd /tests
pytest -v --tb=short test_outputs.py
PYTEST_RC=$?

if [ $PYTEST_RC -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

# --- LLM Judge ---
# (No standalone judge configured for this task.)

exit 0
