#!/usr/bin/env bash
set -uo pipefail

mkdir -p /logs/verifier

cd /tests

python3 -m pytest test_outputs.py \
    -v --tb=short \
    --json-report --json-report-file=/logs/verifier/report.json \
    > /logs/verifier/pytest.log 2>&1
PYTEST_EXIT=$?

cat /logs/verifier/pytest.log

# Convert pytest-json-report output to CTRF (Common Test Report Format).
python3 - <<'PY'
import json, os, pathlib
src = pathlib.Path("/logs/verifier/report.json")
dst = pathlib.Path("/logs/verifier/ctrf.json")
if not src.exists():
    dst.write_text(json.dumps({"results": {"tool": {"name": "pytest"},
                                            "summary": {"tests": 0, "passed": 0,
                                                        "failed": 0, "skipped": 0,
                                                        "pending": 0, "other": 0,
                                                        "start": 0, "stop": 0},
                                            "tests": []}}))
    raise SystemExit(0)
data = json.loads(src.read_text())
status_map = {"passed": "passed", "failed": "failed", "error": "failed",
              "skipped": "skipped", "xfailed": "skipped", "xpassed": "passed"}
tests = []
for t in data.get("tests", []):
    outcome = t.get("outcome", "failed")
    tests.append({
        "name": t.get("nodeid", t.get("name", "?")),
        "status": status_map.get(outcome, "failed"),
        "duration": int(round(t.get("duration", 0) * 1000)),
    })
summary = data.get("summary", {})
ctrf = {"results": {
    "tool": {"name": "pytest"},
    "summary": {
        "tests":   summary.get("total", len(tests)),
        "passed":  summary.get("passed", 0),
        "failed":  summary.get("failed", 0) + summary.get("error", 0),
        "skipped": summary.get("skipped", 0),
        "pending": 0,
        "other":   0,
        "start":   int(data.get("created", 0)),
        "stop":    int(data.get("created", 0) + data.get("duration", 0)),
    },
    "tests": tests,
}}
dst.write_text(json.dumps(ctrf, indent=2))
PY

if [ $PYTEST_EXIT -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

echo "Reward: $(cat /logs/verifier/reward.txt)"
