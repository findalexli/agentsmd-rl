#!/usr/bin/env bash
# Standardized test runner. Pure-pytest reward: writes 0/1 to /logs/verifier/reward.txt
# from pytest's exit code, no string parsing.
set -u

mkdir -p /logs/verifier

cd /tests

# pytest+pyyaml are pre-installed in the Docker image — no network at test time.
python -m pytest -v --tb=short \
    --json-report --json-report-file=/logs/verifier/pytest.json \
    /tests/test_outputs.py
PYTEST_RC=$?

if [ $PYTEST_RC -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

# CTF-style summary file (best-effort, optional)
python - <<'PY' 2>/dev/null || true
import json, os
src = "/logs/verifier/pytest.json"
dst = "/logs/verifier/ctrf.json"
if not os.path.exists(src):
    raise SystemExit(0)
with open(src) as f:
    data = json.load(f)
tests = []
for t in data.get("tests", []):
    tests.append({
        "name": t.get("nodeid", ""),
        "status": "passed" if t.get("outcome") == "passed" else "failed",
        "duration": int((t.get("call", {}).get("duration", 0)) * 1000),
    })
ctrf = {"results": {"tool": {"name": "pytest"}, "tests": tests}}
with open(dst, "w") as f:
    json.dump(ctrf, f)
PY

exit $PYTEST_RC
