#!/bin/bash
# Standardized boilerplate test runner.
set -uo pipefail

mkdir -p /logs/verifier

cd /tests

python -m pytest /tests/test_outputs.py \
    --asyncio-mode=auto \
    -v --tb=short \
    --no-header \
    -p no:cacheprovider \
    > /logs/verifier/pytest.log 2>&1
PYTEST_EXIT=$?

cat /logs/verifier/pytest.log

# Best-effort CTFR-style summary for the audit checklist.
python - <<'PY' || true
import json, re, os
log = open("/logs/verifier/pytest.log").read()
results = []
for m in re.finditer(r"::(test_[\w]+)\s+(PASSED|FAILED|ERROR)\b", log):
    results.append({"name": m.group(1), "status": m.group(2).lower()})
out = {"results": {"tests": results}}
with open("/logs/verifier/ctrf.json", "w") as f:
    json.dump(out, f, indent=2)
PY

if [ "$PYTEST_EXIT" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

echo "Reward: $(cat /logs/verifier/reward.txt)"
exit 0
