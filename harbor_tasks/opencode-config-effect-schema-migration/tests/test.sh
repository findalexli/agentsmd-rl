#!/usr/bin/env bash
set -uo pipefail

# Standardized test runner. Pytest exit-code is the sole reward signal.
mkdir -p /logs/verifier

cd /tests
pytest -v --tb=short \
    --json-report --json-report-file=/logs/verifier/pytest-report.json \
    test_outputs.py
EXIT=$?

# Also emit a CTRF-shaped summary so harness audits can read per-test status.
python3 - <<'PY' || true
import json, os, sys
src = "/logs/verifier/pytest-report.json"
if not os.path.exists(src):
    sys.exit(0)
with open(src) as f:
    data = json.load(f)
tests = []
for t in data.get("tests", []):
    status_map = {"passed": "passed", "failed": "failed", "skipped": "skipped",
                  "error": "failed", "xfailed": "passed", "xpassed": "passed"}
    tests.append({
        "name": t.get("nodeid", ""),
        "status": status_map.get(t.get("outcome", "failed"), "failed"),
        "duration": int(t.get("duration", 0) * 1000),
    })
summary = data.get("summary", {})
ctrf = {"results": {
    "tool": {"name": "pytest"},
    "summary": {
        "tests": summary.get("total", len(tests)),
        "passed": summary.get("passed", 0),
        "failed": summary.get("failed", 0),
        "skipped": summary.get("skipped", 0),
        "pending": 0, "other": 0,
        "start": 0, "stop": int(data.get("duration", 0) * 1000),
    },
    "tests": tests,
}}
with open("/logs/verifier/ctrf.json", "w") as f:
    json.dump(ctrf, f, indent=2)
PY

if [ "$EXIT" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

exit "$EXIT"
