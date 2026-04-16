#!/bin/bash
set -e

# Setup venv for isolated testing to avoid system Python restrictions
VENV_PATH=/tmp/test_venv
if [ ! -d "$VENV_PATH" ]; then
    python3 -m venv "$VENV_PATH"
fi
source "$VENV_PATH/bin/activate"

# Install pytest if needed
if ! python3 -m pytest --version &>/dev/null; then
    pip install pytest --quiet
fi

# Run pytest and capture result
cd /tests
python3 -m pytest test_outputs.py -v 2>&1 | tee /logs/verifier/pytest_output.txt

# Exit with pytest's exit code
exit_code=${PIPESTATUS[0]}

# Write reward
if [ $exit_code -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi

exit $exit_code
