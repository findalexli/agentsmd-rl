#!/bin/bash
set -e

# Install pytest if not present
pip3 install pytest --quiet --break-system-packages 2>/dev/null || pip3 install pytest --quiet 2>/dev/null || true

# Install composer if not present
if ! command -v composer &> /dev/null; then
    apt-get update -qq 2>/dev/null || true
    apt-get install -y -qq unzip 2>/dev/null || true
    curl -sS https://getcomposer.org/installer | php -- --install-dir=/usr/local/bin --filename=composer 2>/dev/null
fi

# Install dependencies if not present
if [ ! -d "/workspace/appwrite/vendor" ]; then
    cd /workspace/appwrite
    composer install --no-interaction --ignore-platform-reqs 2>&1 | tail -5 || true
fi

# Run tests
cd /workspace/appwrite
python3 -m pytest /workspace/task/tests/test_outputs.py -v 2>&1 | tee /logs/verifier/test_output.log || true

# Write binary reward based on test results
EXIT_CODE=${PIPESTATUS[0]}
if [ $EXIT_CODE -eq 0 ]; then
    echo "1" > /logs/verifier/reward
else
    echo "0" > /logs/verifier/reward
fi

exit $EXIT_CODE
