#!/bin/bash
set -e

# Install dependencies if needed
cd /workspace/airflow/airflow-core/src/airflow/ui
if [ ! -d "node_modules" ]; then
    npm ci
fi

# Install pytest if needed
pip install pytest --quiet

# Run the tests
cd /workspace/task
python -m pytest tests/test_outputs.py -v 2>&1 | tee /logs/verifier/test_output.log

# Write binary result
exit_code=${PIPESTATUS[0]}
if [ $exit_code -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

exit $exit_code
