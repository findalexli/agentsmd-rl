#!/usr/bin/env bash
# Standard pytest runner. Writes binary reward to /logs/verifier/reward.txt,
# and a CTRF-format report to /logs/verifier/ctrf.json.
set -uo pipefail

mkdir -p /logs/verifier

cd /tests
pytest -v --tb=short \
    --json-report \
    --json-report-file=/logs/verifier/pytest-report.json \
    test_outputs.py
RESULT=$?

# Convert pytest-json-report -> CTRF for downstream auditing.
python3 - <<'PY' || true
import json, os
src = "/logs/verifier/pytest-report.json"
dst = "/logs/verifier/ctrf.json"
if not os.path.exists(src):
    raise SystemExit(0)
with open(src) as f:
    rep = json.load(f)
status_map = {"passed": "passed", "failed": "failed", "skipped": "skipped",
              "error": "failed", "xfailed": "passed", "xpassed": "passed"}
tests = []
for t in rep.get("tests", []):
    tests.append({
        "name": t.get("nodeid", ""),
        "status": status_map.get(t.get("outcome"), "failed"),
        "duration": int((t.get("call", {}).get("duration") or 0) * 1000),
    })
summary = rep.get("summary", {})
ctrf = {
    "results": {
        "tool": {"name": "pytest"},
        "summary": {
            "tests": summary.get("total", len(tests)),
            "passed": summary.get("passed", 0),
            "failed": summary.get("failed", 0),
            "skipped": summary.get("skipped", 0),
            "pending": 0,
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

if [ $RESULT -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

# --- LLM Judge ---
# (No rubric judge invoked here; reward is purely from pytest exit code.)

exit 0
