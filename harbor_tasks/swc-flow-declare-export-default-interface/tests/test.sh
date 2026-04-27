#!/usr/bin/env bash
# Standardized verifier — runs pytest and writes a binary reward.
set -u

mkdir -p /logs/verifier

cd /tests

pytest -v --tb=short --json-report --json-report-file=/logs/verifier/report.json \
    test_outputs.py 2>&1 | tee /logs/verifier/pytest.log

if [ "${PIPESTATUS[0]}" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

# CTF-style result file for downstream tools.
python3 - <<'PY' || true
import json, pathlib, sys
report_path = pathlib.Path("/logs/verifier/report.json")
out_path = pathlib.Path("/logs/verifier/ctrf.json")
if not report_path.exists():
    sys.exit(0)
report = json.loads(report_path.read_text())
tests = []
for t in report.get("tests", []):
    tests.append({
        "name": t.get("nodeid", ""),
        "status": "passed" if t.get("outcome") == "passed" else "failed",
        "duration": int(t.get("duration", 0) * 1000),
    })
out_path.write_text(json.dumps({"results": {"tests": tests}}, indent=2))
PY

cat /logs/verifier/reward.txt
