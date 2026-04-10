#!/bin/bash
set -e

REPO=/workspace/ant-design

cd $REPO

# Install Python dependencies for tests
pip install pytest --quiet --break-system-packages

# Run the test file
cd /workspace
python3 -m pytest /tests/test_outputs.py -v --tb=short

# Write reward file on success
echo "1.0" > /logs/verifier/reward.txt
