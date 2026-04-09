#!/bin/bash
# Standard test runner - DO NOT MODIFY
# This runs test_outputs.py and writes binary reward to /logs/verifier/reward.txt

set -e

LOGDIR="/logs/verifier"
mkdir -p "$LOGDIR"

# Clone the repo if it doesn't exist (for test environment)
if [ ! -d "/workspace/ClickHouse/.git" ]; then
    echo "Cloning ClickHouse repository..."
    mkdir -p /workspace
    cd /workspace
    git clone --filter=blob:none --depth=100 https://github.com/ClickHouse/ClickHouse.git ClickHouse
    cd ClickHouse
    git checkout 283163272e7318fb1825ebf1b68fdc510cd984d9
fi

# Run pytest with verbose output and capture results
cd /workspace/ClickHouse

if python3 -m pytest /tests/test_outputs.py -v --tb=short 2>&1; then
    echo "1" > "$LOGDIR/reward.txt"
    echo "All tests passed - reward=1"
else
    echo "0" > "$LOGDIR/reward.txt"
    echo "Tests failed - reward=0"
fi
