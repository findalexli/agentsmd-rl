#!/bin/bash
set -e

# Copy repo from mount point if available
if [ -d /dagster-src ]; then
    rm -rf /workspace/dagster
    mkdir -p /workspace/dagster
    cp -r /dagster-src/. /workspace/dagster/
fi

cd /workspace/dagster

# Install pytest and required dependencies
pip install pytest pyyaml pydantic --quiet

# Run the test file
cd /workspace/task/tests
python -m pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.log

# Write binary reward based on test results
exit_code=${PIPESTATUS[0]}
if [ $exit_code -eq 0 ]; then
    echo "1" > /logs/verifier/reward
    echo "All tests passed!"
else
    echo "0" > /logs/verifier/reward
    echo "Some tests failed."
fi

exit $exit_code
