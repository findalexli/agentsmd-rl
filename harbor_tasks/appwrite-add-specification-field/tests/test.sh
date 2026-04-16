#!/bin/bash
set -e

# Create logs directory
mkdir -p /logs/verifier

# Install composer dependencies if needed
if [ ! -d "/workspace/appwrite/vendor" ]; then
    echo "Installing composer dependencies..."
    cd /workspace/appwrite
    composer install --no-dev --no-interaction --optimize-autoloader 2>/dev/null || true
fi

# Install pytest
pip3 install pytest --break-system-packages --quiet 2>/dev/null || \
pip3 install pytest --quiet 2>/dev/null || \
python3 -m pip install pytest --quiet 2>/dev/null || true

# Run tests and capture output
python3 -m pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest_output.txt || true

# Write binary reward based on test results
if python3 -m pytest /tests/test_outputs.py -q 2>/dev/null; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
