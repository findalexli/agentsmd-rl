#!/bin/bash
set -e

echo "=== Setting up test environment ==="

# Install pytest if not present
pip install pytest -q 2>/dev/null || true

# Clone ClickHouse repo if not present
if [ ! -d "/workspace/ClickHouse/.git" ]; then
    echo "=== Cloning ClickHouse repository ==="
    mkdir -p /workspace/ClickHouse
    cd /workspace/ClickHouse
    git init -q
    git remote add origin https://github.com/ClickHouse/ClickHouse.git
    # Fetch just the base commit we need
    git fetch -q --depth 1 origin f4eb1501802bc9f274870d147ae82979956939e6
    git checkout -q f4eb1501802bc9f274870d147ae82979956939e6
    echo "=== Repository cloned ==="
fi

cd /workspace/ClickHouse

# Sparse checkout only the files we need to save space
if [ -d ".git" ]; then
    git sparse-checkout init --cone 2>/dev/null || true
    git sparse-checkout set src/Processors/QueryPlan/Optimizations/optimizeJoinByShards.cpp ci/jobs/scripts/check_style/ 2>/dev/null || true
fi

echo "=== Running tests ==="

# Run pytest with detailed output - tests are mounted at /tests
if python -m pytest /tests/test_outputs.py -v --tb=short 2>&1; then
    echo "=== ALL TESTS PASSED ==="
    echo "1" > /logs/verifier/reward.txt
    exit 0
else
    echo "=== SOME TESTS FAILED ==="
    echo "0" > /logs/verifier/reward.txt
    exit 1
fi
