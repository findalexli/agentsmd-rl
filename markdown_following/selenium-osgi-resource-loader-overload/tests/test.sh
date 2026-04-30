#!/bin/bash
# Standardized test harness for harbor scaffold tasks.
# Reward is the literal "0" or "1" written to /logs/verifier/reward.txt and
# is taken directly from pytest's exit code (no string parsing).

set -uo pipefail

mkdir -p /logs/verifier

cd /tests

# Pytest with JUnit XML for per-test status reporting.
python3 -m pytest -v --tb=short \
    --junitxml=/logs/verifier/junit.xml \
    test_outputs.py
RC=$?

if [ "$RC" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

# Convert JUnit XML → CTRF JSON for downstream consumers.
python3 - <<'PY' || true
import json
import os
import xml.etree.ElementTree as ET

junit_path = "/logs/verifier/junit.xml"
ctrf_path = "/logs/verifier/ctrf.json"

tests = []
summary = {"tests": 0, "passed": 0, "failed": 0, "skipped": 0,
           "pending": 0, "other": 0}

if os.path.isfile(junit_path):
    root = ET.parse(junit_path).getroot()
    for tc in root.iter("testcase"):
        name = tc.get("name", "?")
        if tc.find("failure") is not None or tc.find("error") is not None:
            status = "failed"
        elif tc.find("skipped") is not None:
            status = "skipped"
        else:
            status = "passed"
        tests.append({"name": name, "status": status,
                      "duration": int(float(tc.get("time", 0)) * 1000)})
        summary["tests"] += 1
        summary[status if status in summary else "other"] += 1

ctrf = {
    "reportFormat": "CTRF",
    "specVersion": "0.0.0",
    "results": {
        "tool": {"name": "pytest"},
        "summary": summary,
        "tests": tests,
    },
}
with open(ctrf_path, "w") as f:
    json.dump(ctrf, f, indent=2)
PY

exit 0
