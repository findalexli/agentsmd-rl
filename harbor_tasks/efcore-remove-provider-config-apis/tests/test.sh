#!/bin/bash
# Standardized test harness. Pytest result code drives the binary reward.

set -u

mkdir -p /logs/verifier

cd /tests

PYTEST_JSON=/logs/verifier/pytest_report.json
CTRF_JSON=/logs/verifier/ctrf.json

pytest test_outputs.py -v --tb=short -rA \
    --json-report --json-report-file="${PYTEST_JSON}" \
    > /logs/verifier/pytest.log 2>&1
PYTEST_RC=$?

cat /logs/verifier/pytest.log

# Convert pytest-json-report output to CTRF-shape JSON (tests[].name/status).
if [ -f "${PYTEST_JSON}" ]; then
    python3 - <<'PY'
import json, pathlib
src = json.loads(pathlib.Path("/logs/verifier/pytest_report.json").read_text())
tests = []
for t in src.get("tests", []):
    outcome = t.get("outcome", "unknown")
    status = {"passed": "passed", "failed": "failed", "skipped": "skipped",
              "error": "failed"}.get(outcome, outcome)
    tests.append({
        "name": t.get("nodeid", ""),
        "status": status,
        "duration": int(t.get("duration", 0) * 1000),
    })
ctrf = {"results": {
    "tool": {"name": "pytest"},
    "summary": {
        "tests": len(tests),
        "passed": sum(1 for t in tests if t["status"] == "passed"),
        "failed": sum(1 for t in tests if t["status"] == "failed"),
        "skipped": sum(1 for t in tests if t["status"] == "skipped"),
    },
    "tests": tests,
}}
pathlib.Path("/logs/verifier/ctrf.json").write_text(json.dumps(ctrf, indent=2))
PY
fi

if [ "$PYTEST_RC" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

echo "--- LLM Judge ---"
if [ -f /tests/standalone_judge.py ]; then
    python3 /tests/standalone_judge.py || true
fi

exit "$PYTEST_RC"
