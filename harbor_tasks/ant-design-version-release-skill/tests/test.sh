#!/usr/bin/env bash
set -uo pipefail

mkdir -p /logs/verifier

cd /tests

pytest -v --tb=short \
    --json-report --json-report-file=/logs/verifier/pytest_report.json \
    test_outputs.py
PYTEST_RC=$?

# Also emit a minimal CTRF-shaped report for downstream tooling that expects it.
python3 - <<'PYEOF'
import json
from pathlib import Path

src = Path("/logs/verifier/pytest_report.json")
dst = Path("/logs/verifier/ctrf.json")
if not src.exists():
    dst.write_text(json.dumps({"results": {"tests": []}}))
else:
    data = json.loads(src.read_text())
    tests = []
    for t in data.get("tests", []):
        outcome = t.get("outcome", "")
        status = {
            "passed": "passed",
            "failed": "failed",
            "error": "failed",
            "skipped": "skipped",
        }.get(outcome, outcome or "other")
        tests.append({"name": t.get("nodeid", ""), "status": status})
    dst.write_text(json.dumps({"results": {"tests": tests}}, indent=2))
PYEOF


if [ "${PYTEST_RC}" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

echo "pytest exit code: ${PYTEST_RC}"
echo "reward: $(cat /logs/verifier/reward.txt)"
