#!/bin/bash
set -uo pipefail

echo "Running tests..."
cd /tests
set +e
python3 -m pytest test_outputs.py -v --tb=short -p no:cacheprovider --junitxml=/tmp/test-results.xml 2>&1
PYTEST_EXIT=$?
set -e

if [ $PYTEST_EXIT -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
    echo "All tests passed. Reward=1"
else
    echo 0 > /logs/verifier/reward.txt
    echo "Some tests failed. Reward=0"
fi

# --- LLM Judge ---
echo ""
echo "--- LLM Judge ---"
echo "=== ctrf.json (test results) ==="
python3 -c "
import json, os, sys, time
results = {
    'schemaVersion': '1.0.0',
    'results': {
        'tool': {'name': 'pytest', 'version': '8.3.4'},
        'summary': {
            'tests': 0, 'passed': 0, 'failed': 0, 'skipped': 0,
            'pending': 0, 'other': 0, 'startTime': int(time.time() * 1000),
            'stopTime': int(time.time() * 1000)
        },
        'tests': []
    }
}
try:
    import xml.etree.ElementTree as ET
    tree = ET.parse('/tmp/test-results.xml')
    root = tree.getroot()
    for suite in root:
        for case in suite:
            name = case.get('classname', '') + '.' + case.get('name', '')
            if case.find('skipped') is not None:
                results['results']['summary']['skipped'] += 1
                results['results']['tests'].append({'name': name, 'status': 'skipped', 'duration': int(float(case.get('time', 0)) * 1000)})
            elif case.find('failure') is not None:
                results['results']['summary']['failed'] += 1
                results['results']['tests'].append({'name': name, 'status': 'failed', 'duration': int(float(case.get('time', 0)) * 1000)})
            elif case.find('error') is not None:
                results['results']['summary']['failed'] += 1
                results['results']['tests'].append({'name': name, 'status': 'failed', 'duration': int(float(case.get('time', 0)) * 1000)})
            else:
                results['results']['summary']['passed'] += 1
                results['results']['tests'].append({'name': name, 'status': 'passed', 'duration': int(float(case.get('time', 0)) * 1000)})
    results['results']['summary']['tests'] = (results['results']['summary']['passed'] +
        results['results']['summary']['failed'] + results['results']['summary']['skipped'])
except Exception:
    pass
with open('/logs/verifier/ctrf.json', 'w') as f:
    json.dump(results, f, indent=2)
print('ctrf.json written to /logs/verifier/ctrf.json')
"
