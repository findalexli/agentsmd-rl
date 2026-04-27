#!/usr/bin/env bash
# Standardized test runner — DO NOT add task-specific logic here.
set -u

mkdir -p /logs/verifier

PYTEST_BIN="$(command -v pytest || true)"
if [ -z "${PYTEST_BIN}" ] && [ -x /opt/pytest-venv/bin/pytest ]; then
    PYTEST_BIN=/opt/pytest-venv/bin/pytest
fi

if [ -z "${PYTEST_BIN}" ]; then
    echo "pytest not found in PATH or /opt/pytest-venv/bin" >&2
    PYTEST_EXIT=2
else
    "${PYTEST_BIN}" /tests/test_outputs.py -v --tb=short \
        --ctrf=/logs/verifier/ctrf.json 2>&1 | tee /logs/verifier/pytest.log
    PYTEST_EXIT=${PIPESTATUS[0]}
fi

if [ "${PYTEST_EXIT}" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

# --- LLM Judge (optional, runs after reward is written) ---
if [ -f /tests/standalone_judge.py ] && [ -n "${ANTHROPIC_API_KEY:-}" ]; then
    python3 /tests/standalone_judge.py 2>&1 | tee /logs/verifier/judge.log || true
fi
