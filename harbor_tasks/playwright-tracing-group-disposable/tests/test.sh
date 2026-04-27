#!/usr/bin/env bash
# Test runner: rebuild compiled JS / regenerated types from any source changes,
# then run pytest. Reward is pytest's exit code.

set +e

mkdir -p /logs/verifier

cd /workspace/playwright

# Rebuild lib/ and regenerate types.d.ts so tests see the agent's edits.
# Stay loud on real failures (no `|| true`); a broken build = reward 0.
node utils/build/build.js --disable-install >/logs/verifier/build.log 2>&1
build_status=$?
if [ "$build_status" -ne 0 ]; then
    echo "Build failed (exit=$build_status); see /logs/verifier/build.log" >&2
    tail -50 /logs/verifier/build.log >&2
fi

# Run pytest. Reward = pytest exit code (literal "0" or "1").
pytest -v --tb=short \
    --ctrf /logs/verifier/ctrf.json \
    /tests/test_outputs.py
pytest_exit=$?

if [ "$pytest_exit" -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

echo "Reward written: $(cat /logs/verifier/reward.txt) (pytest exit=$pytest_exit)"
