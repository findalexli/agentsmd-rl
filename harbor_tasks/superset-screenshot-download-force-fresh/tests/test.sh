#!/usr/bin/env bash
set -uo pipefail

mkdir -p /logs/verifier

cd /tests

# Run pytest. -v gives per-test output; --tb=short keeps tracebacks readable.
python3 -m pytest test_outputs.py \
    -v --tb=short \
    --json-report --json-report-file=/logs/verifier/pytest_report.json \
    2>&1 | tee /logs/verifier/pytest.log

PYTEST_EXIT=${PIPESTATUS[0]}

if [ "$PYTEST_EXIT" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

# Convert pytest-json-report output to CTRF format for downstream auditing.
python3 - <<'PY' || true
import json, os
src = '/logs/verifier/pytest_report.json'
if not os.path.exists(src):
    raise SystemExit
with open(src) as f:
    data = json.load(f)
tests = []
for t in data.get('tests', []):
    outcome = t.get('outcome', 'failed')
    status = 'passed' if outcome == 'passed' else 'failed' if outcome in ('failed', 'error') else outcome
    tests.append({'name': t.get('nodeid', ''), 'status': status, 'duration': int(t.get('duration', 0) * 1000)})
ctrf = {
    'results': {
        'tool': {'name': 'pytest'},
        'summary': {
            'tests': len(tests),
            'passed': sum(1 for x in tests if x['status'] == 'passed'),
            'failed': sum(1 for x in tests if x['status'] == 'failed'),
            'pending': 0, 'skipped': 0, 'other': 0,
            'start': 0, 'stop': 0,
        },
        'tests': tests,
    },
}
with open('/logs/verifier/ctrf.json', 'w') as f:
    json.dump(ctrf, f, indent=2)
PY

echo "pytest exit=$PYTEST_EXIT, reward=$(cat /logs/verifier/reward.txt)"
