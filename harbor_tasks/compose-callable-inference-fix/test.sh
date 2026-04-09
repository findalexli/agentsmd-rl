#!/bin/bash
set -e

# Install pytest and dependencies
pip install pytest pytest-json-report -q

# Run the tests and capture output
cd /workspace/task
python -m pytest tests/test_outputs.py -v --json-report --json-report-file=/workspace/task/test_results.json 2>&1 || true

# Write binary reward
if [ -f /workspace/task/test_results.json ]; then
    # Extract pass/fail status
    passed=$(python -c "import json; data=json.load(open('/workspace/task/test_results.json')); print(data.get('summary', {}).get('passed', 0))" 2>/dev/null || echo "0")
    failed=$(python -c "import json; data=json.load(open('/workspace/task/test_results.json')); print(data.get('summary', {}).get('failed', 0))" 2>/dev/null || echo "0")
    total=$((passed + failed))

    if [ "$total" -eq 0 ]; then
        echo "0" > /workspace/task/reward
    else
        # Calculate reward as passed/total
        python -c "print($passed / $total)" > /workspace/task/reward
    fi
else
    echo "0" > /workspace/task/reward
fi

echo "Test completed. Reward: $(cat /workspace/task/reward)"
