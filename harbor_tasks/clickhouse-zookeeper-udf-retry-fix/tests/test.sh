#!/bin/bash
set -uo pipefail

# Install pytest if needed
pip3 install --break-system-packages pytest pyyaml pytest-json-report 2>/dev/null || pip3 install pytest pyyaml pytest-json-report

# Create logs directory
mkdir -p /logs/verifier

# Run tests with JSON report (continue even if tests fail)
cd /tests
python3 -m pytest test_outputs.py -v --json-report --json-report-file=/logs/verifier/test_results.json 2>&1 | tee /logs/verifier/test_output.log || true

# Extract test results for reward calculation
python3 << 'PYEOF'
import json
import sys

try:
    with open('/logs/verifier/test_results.json', 'r') as f:
        results = json.load(f)

    total = results.get('summary', {}).get('total', 0)
    passed = results.get('summary', {}).get('passed', 0)
    failed = results.get('summary', {}).get('failed', 0)

    # Calculate binary reward: 1 if all passed, 0 otherwise
    reward = 1 if failed == 0 and total > 0 else 0

    # Write binary reward
    with open('/logs/verifier/reward.txt', 'w') as f:
        f.write(str(reward))

    print(f"Tests: {total} total, {passed} passed, {failed} failed")
    print(f"Reward: {reward}")

    sys.exit(0 if reward == 1 else 1)
except Exception as e:
    print(f"Error processing results: {e}")
    with open('/logs/verifier/reward.txt', 'w') as f:
        f.write('0')
    sys.exit(1)
PYEOF
