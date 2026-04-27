#!/usr/bin/env bash
# Verifier entrypoint. Runs pytest; reward is exit code of pytest.
set -uo pipefail

mkdir -p /logs/verifier

cd /workspace/prime-rl

python3 -m pytest /tests/test_outputs.py \
    -v --tb=short --color=no \
    2>&1 | tee /logs/verifier/pytest.log
PYTEST_RC=${PIPESTATUS[0]}

# Synthesise a tiny CTRF-style summary so the audit can confirm per-test status.
python3 - "${PYTEST_RC}" <<'PY' || true
import json, re, sys, pathlib
log = pathlib.Path("/logs/verifier/pytest.log").read_text(errors="replace")
tests = []
for m in re.finditer(r"^(?P<nodeid>\S+::\S+)\s+(?P<status>PASSED|FAILED|ERROR|SKIPPED)", log, re.M):
    tests.append({
        "name": m.group("nodeid"),
        "status": {"PASSED": "passed", "FAILED": "failed", "ERROR": "failed", "SKIPPED": "skipped"}[m.group("status")],
    })
ctrf = {
    "results": {
        "tool": {"name": "pytest"},
        "summary": {
            "tests": len(tests),
            "passed": sum(1 for t in tests if t["status"] == "passed"),
            "failed": sum(1 for t in tests if t["status"] == "failed"),
            "skipped": sum(1 for t in tests if t["status"] == "skipped"),
        },
        "tests": tests,
    }
}
pathlib.Path("/logs/verifier/ctrf.json").write_text(json.dumps(ctrf, indent=2))
PY

if [ "${PYTEST_RC}" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

echo "pytest exit=${PYTEST_RC} reward=$(cat /logs/verifier/reward.txt)"
exit 0
