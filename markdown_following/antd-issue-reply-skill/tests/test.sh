#!/bin/bash
# Test harness: runs pytest, writes binary reward to /logs/verifier/reward.txt.

set -u

mkdir -p /logs/verifier

cd /tests

python3 -m pytest test_outputs.py -v --tb=short \
    --json-report --json-report-file=/logs/verifier/report.json 2>&1 \
    | tee /logs/verifier/pytest.log
status=${PIPESTATUS[0]}

if [ "$status" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

# Best-effort CTFR-style summary so quality_gate / every_gold_test_passes
# can introspect per-test results. If pytest-json-report wasn't installed,
# this block is a no-op.
python3 - <<'PY' || true
import json, sys
from pathlib import Path
src = Path("/logs/verifier/report.json")
if not src.exists():
    sys.exit(0)
data = json.loads(src.read_text())
tests = data.get("tests", [])
ctrf = {
    "results": {
        "tests": [
            {
                "name": t.get("nodeid", ""),
                "status": "passed" if t.get("outcome") == "passed" else "failed",
                "duration": int(1000 * (t.get("duration") or 0)),
            }
            for t in tests
        ]
    }
}
Path("/logs/verifier/ctrf.json").write_text(json.dumps(ctrf))
PY

cat /logs/verifier/reward.txt
