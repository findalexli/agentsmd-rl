#!/bin/bash
# Standardized test runner: runs pytest on /tests/test_outputs.py and writes 0/1 reward.
set -uo pipefail

mkdir -p /logs/verifier

cd /tests
pytest -v --tb=short \
       --json-report \
       --json-report-file=/logs/verifier/pytest-report.json \
       test_outputs.py
PYTEST_EXIT=$?

# Convert pytest-json-report output to a minimal CTRF-shaped JSON
# (each test as {name, status} where status is "passed"/"failed"/"skipped"/...).
python3 - <<'PY'
import json, os
src = "/logs/verifier/pytest-report.json"
dst = "/logs/verifier/ctrf.json"
if not os.path.exists(src):
    out = {"results": {"tool": {"name": "pytest"}, "tests": []}}
else:
    with open(src) as f:
        data = json.load(f)
    tests = []
    for t in data.get("tests", []):
        tests.append({
            "name": t.get("nodeid", ""),
            "status": t.get("outcome", "unknown"),
            "duration": int((t.get("duration") or 0) * 1000),
        })
    out = {"results": {"tool": {"name": "pytest"}, "tests": tests}}
with open(dst, "w") as f:
    json.dump(out, f, indent=2)
PY

if [ ${PYTEST_EXIT} -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

cat /logs/verifier/reward.txt
exit 0
