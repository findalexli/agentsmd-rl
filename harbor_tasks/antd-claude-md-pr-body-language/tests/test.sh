#!/usr/bin/env bash
# Standardized boilerplate — do not modify.
set -uo pipefail

mkdir -p /logs/verifier

cd /tests
python3 -m pytest test_outputs.py -v --tb=short \
    --json-report --json-report-file=/logs/verifier/pytest_report.json \
    2>&1 | tee /logs/verifier/pytest.log
PYTEST_RC=${PIPESTATUS[0]}

# Convert pytest-json-report → minimal CTRF for downstream consumers.
python3 - <<'PY' || true
import json, pathlib
src = pathlib.Path("/logs/verifier/pytest_report.json")
dst = pathlib.Path("/logs/verifier/ctrf.json")
if not src.exists():
    raise SystemExit(0)
data = json.loads(src.read_text())
results = {"tests": []}
for t in data.get("tests", []):
    outcome = t.get("outcome", "skipped")
    status = {"passed": "passed", "failed": "failed", "skipped": "skipped",
              "error": "failed", "xfailed": "skipped", "xpassed": "passed"}.get(outcome, outcome)
    results["tests"].append({"name": t.get("nodeid", ""), "status": status,
                              "duration": int((t.get("duration") or 0) * 1000)})
ctrf = {"results": {"tool": {"name": "pytest"}, "summary": {
    "tests": len(results["tests"]),
    "passed": sum(1 for t in results["tests"] if t["status"] == "passed"),
    "failed": sum(1 for t in results["tests"] if t["status"] == "failed"),
    "skipped": sum(1 for t in results["tests"] if t["status"] == "skipped"),
    "pending": 0, "other": 0,
    "start": 0, "stop": 0,
}, **results}}
dst.write_text(json.dumps(ctrf, indent=2))
PY

if [ "${PYTEST_RC}" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

echo "--- pytest exit ${PYTEST_RC}; reward=$(cat /logs/verifier/reward.txt) ---"
