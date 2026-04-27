#!/bin/bash
# Standardized test runner — DO NOT add task-specific logic here.
set -uo pipefail

mkdir -p /logs/verifier

cd /workspace/prime-rl 2>/dev/null || cd /workspace || true

cd /tests
python3 -m pytest test_outputs.py -v --tb=short \
    --json-report --json-report-file=/logs/verifier/report.json
PYTEST_RC=$?

# Generate ctrf.json from pytest's json-report (best effort)
python3 - <<'PY' || true
import json, os
src = "/logs/verifier/report.json"
dst = "/logs/verifier/ctrf.json"
if not os.path.exists(src):
    raise SystemExit(0)
with open(src) as f:
    d = json.load(f)
tests = []
for t in d.get("tests", []):
    status = "passed" if t.get("outcome") == "passed" else "failed"
    tests.append({"name": t.get("nodeid", "?"), "status": status,
                   "duration": int(1000 * t.get("duration", 0))})
with open(dst, "w") as f:
    json.dump({"results": {"tests": tests}}, f)
PY

if [ $PYTEST_RC -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

cat /logs/verifier/reward.txt
