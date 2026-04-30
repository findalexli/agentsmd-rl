#!/usr/bin/env bash
# Run pytest and write a binary reward (0/1) to /logs/verifier/reward.txt based
# solely on pytest's exit code. No grep gates, no JSON wrapping. The reward path
# and format are dictated by the harbor harness.
set -uo pipefail

mkdir -p /logs/verifier

cd /workspace/ruff || exit 1

# Rebuild ty against whatever source the agent has now. The base build is cached
# in the Dockerfile, so this is incremental and fast (a few seconds for a small
# edit).
cargo build --bin ty 2>&1 | tail -40
build_status=$?
if [ "$build_status" -ne 0 ]; then
    echo "Build failed; emitting reward=0"
    echo 0 > /logs/verifier/reward.txt
    exit 0
fi

cd / || exit 1

pytest -v --tb=short --ctrf /logs/verifier/ctrf.json /tests/test_outputs.py
status=$?

if [ "$status" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi
