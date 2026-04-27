#!/usr/bin/env bash
# Standard test runner: runs pytest, writes 0/1 reward from exit code.
set -uo pipefail

mkdir -p /logs/verifier

cd /workspace/airflow

python -m pytest -v --tb=short \
    --json-report --json-report-file=/logs/verifier/pytest_report.json \
    /tests/test_outputs.py 2>&1 | tee /logs/verifier/pytest.log

PYTEST_RC=${PIPESTATUS[0]}

if [ "$PYTEST_RC" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

# Convert pytest-json-report output to a minimal CTRF-shaped report so
# downstream tooling can scan per-test pass/fail.
python - <<'PY' || true
import json, pathlib
src = pathlib.Path("/logs/verifier/pytest_report.json")
dst = pathlib.Path("/logs/verifier/ctrf.json")
if not src.exists():
    dst.write_text(json.dumps({"results": {"tests": []}}))
else:
    data = json.loads(src.read_text())
    tests = []
    for t in data.get("tests", []):
        outcome = t.get("outcome", "")
        status = "passed" if outcome == "passed" else "failed" if outcome in ("failed", "error") else outcome
        tests.append({"name": t.get("nodeid", ""), "status": status, "duration": int((t.get("duration") or 0) * 1000)})
    dst.write_text(json.dumps({"results": {"tests": tests}}, indent=2))
PY

echo "pytest exit code: $PYTEST_RC"
echo "reward: $(cat /logs/verifier/reward.txt)"
