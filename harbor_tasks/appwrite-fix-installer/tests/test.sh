#!/usr/bin/env bash
# Standardized test runner for the appwrite-fix-installer task.
set -uo pipefail

mkdir -p /logs/verifier

cd /tests || exit 1

python3 -m pytest -v --tb=short \
    --json-report --json-report-file=/logs/verifier/pytest_report.json \
    test_outputs.py
PYTEST_RC=$?

# Convert pytest-json-report output to CTRF-shaped JSON for the audit harness.
python3 - <<'PY' || true
import json, os
src = "/logs/verifier/pytest_report.json"
dst = "/logs/verifier/ctrf.json"
if not os.path.exists(src):
    open(dst, "w").write(json.dumps({"results": {"tests": []}}))
else:
    rep = json.load(open(src))
    tests = []
    for t in rep.get("tests", []):
        tests.append({
            "name": t.get("nodeid", ""),
            "status": "passed" if t.get("outcome") == "passed" else "failed",
            "duration": int(t.get("duration", 0) * 1000),
        })
    open(dst, "w").write(json.dumps({"results": {"tests": tests}}, indent=2))
PY

if [ $PYTEST_RC -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

# --- LLM Judge ---
# Track 2 (markdown_authoring config diff) is scored externally by Gemini
# using eval_manifest.yaml.config_edits, not from this script.

exit 0
