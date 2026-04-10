#!/bin/bash
set -e

# Install pytest if needed
pip install pytest mock time-machine -q 2>/dev/null || true

# Copy test file to writable location
cp /tests/test_outputs.py /tmp/test_outputs.py

# Set up Python path for imports
export PYTHONPATH="/workspace/airflow/providers/amazon/src:/workspace/airflow/providers/openlineage/src:/workspace/airflow/providers/common/compat/src:/workspace/airflow/airflow-core/src:/workspace/airflow/task-sdk/src:$PYTHONPATH"

# Run the tests
cd /tmp
python -m pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.log

# Extract the result
exit_code=${PIPESTATUS[0]}

# Write binary reward
if [ $exit_code -eq 0 ]; then
    echo "1" > /logs/verifier/reward
else
    echo "0" > /logs/verifier/reward
fi

exit $exit_code
