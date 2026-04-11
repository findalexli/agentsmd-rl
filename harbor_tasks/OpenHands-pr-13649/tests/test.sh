#!/bin/bash
set -e

echo "Installing pytest..."
pip3 install pytest --quiet --break-system-packages 2>/dev/null || pip3 install pytest --quiet

echo "Running tests..."
timeout 300 pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.log

exit_code=${PIPESTATUS[0]}

if [ $exit_code -eq 0 ]; then
    echo "All tests passed!"
    echo '{"passed": true, "score": 1.0, "metadata": {}}' > /logs/verifier/reward.json
else
    echo "Tests failed with exit code $exit_code"
    echo "{\"passed\": false, \"score\": 0.0, \"metadata\": {}}" > /logs/verifier/reward.json
fi

exit $exit_code
