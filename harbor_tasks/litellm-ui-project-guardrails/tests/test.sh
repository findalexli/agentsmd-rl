#!/usr/bin/env bash
# Standardized test harness — runs pytest against test_outputs.py and writes
# binary reward to /logs/verifier/reward.txt based on pytest's exit code.
set -u
mkdir -p /logs/verifier

# pytest is already installed in the image (pinned). No network at test time.
cd /tests
pytest -v --tb=short -p no:cacheprovider --json-report --json-report-file=/logs/verifier/pytest.json test_outputs.py
PYTEST_RC=$?

if [ $PYTEST_RC -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

# Also emit a CTFR-shaped JSON for harness-side per-test inspection.
python3 - <<'PY' || true
import json, os
src = "/logs/verifier/pytest.json"
dst = "/logs/verifier/ctrf.json"
try:
    with open(src) as f:
        j = json.load(f)
    tests = []
    for t in j.get("tests", []):
        tests.append({
            "name": t.get("nodeid", ""),
            "status": "passed" if t.get("outcome") == "passed" else "failed",
            "duration": int((t.get("duration") or 0) * 1000),
        })
    out = {"results": {"tool": {"name": "pytest"}, "summary": {"tests": len(tests)}, "tests": tests}}
    with open(dst, "w") as f:
        json.dump(out, f)
except Exception as e:
    pass
PY

echo "--- LLM Judge (no-op for now) ---"

exit 0
