#!/bin/bash
set -e

# Install pytest if needed (use --break-system-packages for container environment)
pip3 install pytest --quiet --break-system-packages 2>/dev/null || pip3 install pytest --quiet

# Setup test directory
if [ -f "/tests/test_outputs.py" ]; then
    # Mounted from host
    TEST_SCRIPT="/tests/test_outputs.py"
else
    # Local copy
    TEST_SCRIPT="/workspace/task/tests/test_outputs.py"
fi

# Run the test file
python3 "$TEST_SCRIPT"

# Write binary reward
exit_code=$?
if [ $exit_code -eq 0 ]; then
    echo "1" > /logs/verifier/passed
else
    echo "0" > /logs/verifier/passed
fi

exit $exit_code
