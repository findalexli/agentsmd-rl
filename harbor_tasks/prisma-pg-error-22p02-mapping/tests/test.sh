#!/usr/bin/env bash
# Standardized test runner. DO NOT add task-specific logic.

set -uo pipefail

mkdir -p /logs/verifier

# Run pytest. Pytest is installed in the Dockerfile (pinned); never install at test time.
pytest /tests/test_outputs.py -v --tb=short --json-report --json-report-file=/logs/verifier/pytest.json 2>&1 | tee /logs/verifier/pytest.log
PYTEST_RC=$?

if [ $PYTEST_RC -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

# Generate ctrf.json from pytest output for downstream tooling
python3 - <<'PY' || true
import json, os, sys
src = "/logs/verifier/pytest.json"
dst = "/logs/verifier/ctrf.json"
if not os.path.exists(src):
    sys.exit(0)
with open(src) as f:
    d = json.load(f)
tests = []
for t in d.get("tests", []):
    tests.append({
        "name": t.get("nodeid", ""),
        "status": "passed" if t.get("outcome") == "passed" else "failed",
        "duration": int(t.get("duration", 0) * 1000),
        "message": (t.get("call", {}) or {}).get("longrepr", "")
    })
summary = d.get("summary", {})
ctrf = {
    "results": {
        "tool": {"name": "pytest"},
        "summary": {
            "tests": summary.get("total", len(tests)),
            "passed": summary.get("passed", 0),
            "failed": summary.get("failed", 0),
            "pending": 0,
            "skipped": summary.get("skipped", 0),
            "other": 0,
            "start": 0,
            "stop": 0,
        },
        "tests": tests,
    }
}
with open(dst, "w") as f:
    json.dump(ctrf, f, indent=2)
PY

# --- LLM Judge ---
# (No LLM judge for this task; rubric checks are static.)

cat /logs/verifier/reward.txt
