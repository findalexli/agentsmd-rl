#!/usr/bin/env bash
# Standardised pytest runner for harbor benchmark tasks.
# Writes a binary 0/1 reward to /logs/verifier/reward.txt based on pytest's
# exit code. Do not add task-specific logic here.

set -u

mkdir -p /logs/verifier

cd /tests

# pytest is preinstalled in the Docker image; the line below is a no-op
# safety net for environments where it is not, and must NOT mask install
# failures with `|| true`.
python3 -m pytest --version >/dev/null 2>&1 || {
    python3 -m pip install --break-system-packages --no-cache-dir pytest==8.3.4 pytest-json-ctrf==0.3.5
}

python3 -m pytest -v --tb=short \
    --ctrf /logs/verifier/ctrf.json \
    /tests/test_outputs.py \
    2>&1 | tee /logs/verifier/pytest.log

PYTEST_RC=${PIPESTATUS[0]}
if [ "$PYTEST_RC" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

# --- LLM Judge ---
# Optional rubric pass; harness invokes /tests/standalone_judge.py if present.
if [ -f /tests/standalone_judge.py ]; then
    python3 /tests/standalone_judge.py >/logs/verifier/judge.log 2>&1 || true
fi

exit 0
