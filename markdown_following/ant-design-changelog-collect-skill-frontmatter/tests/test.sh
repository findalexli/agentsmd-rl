#!/bin/bash
# Standardized test runner. Do not add task-specific logic.
set -uo pipefail

mkdir -p /logs/verifier

cd /tests
pytest -v --tb=short \
    --json-report --json-report-file=/logs/verifier/pytest-report.json \
    test_outputs.py 2>&1 | tee /logs/verifier/pytest.log
PYTEST_RC=${PIPESTATUS[0]}

# Convert pytest-json-report to a minimal CTRF-shaped file so downstream
# tooling (lint rubric `every_gold_test_passes`) can read individual test
# statuses from /logs/verifier/ctrf.json.
python3 - <<'PY'
import json, pathlib
src = pathlib.Path("/logs/verifier/pytest-report.json")
dst = pathlib.Path("/logs/verifier/ctrf.json")
if not src.is_file():
    dst.write_text(json.dumps({"results": {"tests": []}}))
else:
    data = json.loads(src.read_text())
    tests = []
    for t in data.get("tests", []):
        tests.append({
            "name": t.get("nodeid", ""),
            "status": t.get("outcome", "unknown"),
            "duration": int(1000 * (t.get("duration", 0) or 0)),
        })
    dst.write_text(json.dumps({"results": {"tests": tests}}, indent=2))
PY

if [ "$PYTEST_RC" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

echo "--- LLM Judge ---"
echo "Track 1 reward: $(cat /logs/verifier/reward.txt)"
