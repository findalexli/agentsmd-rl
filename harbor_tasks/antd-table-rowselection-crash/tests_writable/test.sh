#!/bin/bash
set -e

REPO=/workspace/ant-design

cd $REPO

# Install Python dependencies for tests
pip install pytest --quiet --break-system-packages

# Install tsx globally for TypeScript test execution
npm install -g tsx

# Generate version file required by tests
npm run version

# Run the test file
cd /workspace
python3 -m pytest /tests/test_outputs.py -v --tb=short

# Write reward file on success
echo "1.0" > /logs/verifier/reward.txt
