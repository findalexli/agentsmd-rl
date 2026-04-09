#!/bin/bash

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

# Run the test file and capture exit code
python3 "$TEST_SCRIPT"
exit_code=$?

# Write binary reward (1 = all passed, 0 = some failed)
if [ $exit_code -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

exit $exit_code
