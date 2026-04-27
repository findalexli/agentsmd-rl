#!/usr/bin/env bash
# Standardized test harness — runs pytest and writes binary reward to
# /logs/verifier/reward.txt. Reward is taken from pytest's exit code.
set -u

mkdir -p /logs/verifier

cd /tests

if command -v pytest >/dev/null 2>&1; then
  pytest \
    test_outputs.py \
    -v \
    --tb=short \
    --json-report \
    --json-report-file=/logs/verifier/pytest_report.json \
    2>&1 | tee /logs/verifier/pytest_output.log
  PYTEST_RC=${PIPESTATUS[0]}
else
  echo "FATAL: pytest not installed in image" >&2
  PYTEST_RC=2
fi

# Translate pytest's JSON report to a minimal CTRF-shaped file so the audit
# step's `"status": "failed"` check works.
python3 - <<'PY' || true
import json, os
src = "/logs/verifier/pytest_report.json"
dst = "/logs/verifier/ctrf.json"
if not os.path.exists(src):
    raise SystemExit(0)
with open(src) as f:
    rep = json.load(f)
tests = []
for t in rep.get("tests", []):
    outcome = t.get("outcome", "")
    status = "passed" if outcome == "passed" else ("skipped" if outcome == "skipped" else "failed")
    tests.append({
        "name": t.get("nodeid", ""),
        "status": status,
        "duration": int(round(t.get("duration", 0) * 1000)),
    })
ctrf = {
    "results": {
        "tool": {"name": "pytest"},
        "summary": {
            "tests": len(tests),
            "passed": sum(1 for x in tests if x["status"] == "passed"),
            "failed": sum(1 for x in tests if x["status"] == "failed"),
            "skipped": sum(1 for x in tests if x["status"] == "skipped"),
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

if [ "$PYTEST_RC" -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi

echo "reward written: $(cat /logs/verifier/reward.txt) (pytest rc=$PYTEST_RC)"

# --- LLM Judge ---
# (no LLM judge configured for this task)
