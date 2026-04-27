#!/usr/bin/env bash
# Standardized test runner. DO NOT modify task-specific logic here.
set -uo pipefail

mkdir -p /logs/verifier

cd /tests

python -m pytest test_outputs.py \
    -v --tb=short \
    --junitxml=/logs/verifier/junit.xml
status=$?

if [ $status -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

# Convert junit.xml to a minimal CTRF report at /logs/verifier/ctrf.json
# so the audit can introspect per-test pass/fail.
python <<'PY'
import json
import os
import xml.etree.ElementTree as ET

junit_path = "/logs/verifier/junit.xml"
ctrf_path = "/logs/verifier/ctrf.json"
if not os.path.exists(junit_path):
    json.dump({"results": {"tests": []}}, open(ctrf_path, "w"))
    raise SystemExit(0)

tree = ET.parse(junit_path)
root = tree.getroot()
tests = []
for case in root.iter("testcase"):
    name = f"{case.attrib.get('classname','')}::{case.attrib.get('name','')}"
    duration = int(float(case.attrib.get("time", "0")) * 1000)
    failure = case.find("failure") is not None or case.find("error") is not None
    skipped = case.find("skipped") is not None
    if failure:
        status = "failed"
    elif skipped:
        status = "skipped"
    else:
        status = "passed"
    msg = ""
    fnode = case.find("failure")
    if fnode is None:
        fnode = case.find("error")
    if fnode is not None:
        msg = (fnode.attrib.get("message", "") + "\n" + (fnode.text or "")).strip()[:2000]
    tests.append({"name": name, "status": status, "duration": duration, "message": msg})

summary = {
    "tests": len(tests),
    "passed": sum(1 for t in tests if t["status"] == "passed"),
    "failed": sum(1 for t in tests if t["status"] == "failed"),
    "skipped": sum(1 for t in tests if t["status"] == "skipped"),
    "pending": 0,
    "other": 0,
    "start": 0,
    "stop": 0,
}
json.dump({"results": {"tool": {"name": "pytest"}, "summary": summary, "tests": tests}}, open(ctrf_path, "w"), indent=2)
PY

echo "Reward: $(cat /logs/verifier/reward.txt)"
