#!/usr/bin/env bash
# Standardized test runner. Executes pytest on /tests/test_outputs.py and
# writes the binary reward (literal "0" or "1") to /logs/verifier/reward.txt.
set -uo pipefail

mkdir -p /logs/verifier

# Bootstrap pytest + pytest-json-report if the base image lacks them
# (Node-only base images, etc.).
if ! python3 -c "import pytest" >/dev/null 2>&1; then
    pip3 install --break-system-packages --no-cache-dir \
        pytest==8.3.4 pyyaml==6.0.2 pytest-json-report==1.5.0
fi

cd /tests
python3 -m pytest test_outputs.py -v --tb=short \
    --json-report --json-report-file=/logs/verifier/pytest_report.json \
    2>&1 | tee /logs/verifier/pytest.log
PYTEST_RC=${PIPESTATUS[0]}

# Translate pytest-json-report → CTRF-shaped /logs/verifier/ctrf.json so the
# post-validation gate (`check_all_gold_tests_passed`) can read it.
python3 - <<'PY' || true
import json, pathlib
src = pathlib.Path("/logs/verifier/pytest_report.json")
dst = pathlib.Path("/logs/verifier/ctrf.json")
if not src.exists():
    raise SystemExit(0)
data = json.loads(src.read_text())
status_map = {"passed": "passed", "failed": "failed", "error": "failed", "skipped": "skipped"}
tests = []
for t in data.get("tests") or []:
    tests.append({
        "name": t.get("nodeid") or t.get("name") or "<unknown>",
        "status": status_map.get(t.get("outcome", "failed"), "failed"),
    })
dst.write_text(json.dumps({"results": {"tests": tests}}, indent=2))
PY

if [ "$PYTEST_RC" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

# --- LLM Judge ---
# (No standalone judge for this task — reward is pure pytest.)

cat /logs/verifier/reward.txt
