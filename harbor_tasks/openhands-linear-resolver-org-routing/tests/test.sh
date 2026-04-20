#!/bin/bash
# Note: NOT using set -e because we want to capture pytest results even if some fail

# Install pytest if needed
pip install pytest pytest-asyncio -q

# Run tests and capture output
mkdir -p /logs/verifier
pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest_output.txt || true

# Write binary reward based on test results
# Count key test results - we need the core f2p tests to pass
passed=$(grep -c "PASSED" /logs/verifier/pytest_output.txt 2>/dev/null || echo "0")
failed=$(grep -o "FAILED" /logs/verifier/pytest_output.txt 2>/dev/null | wc -l || echo "0")

# Clean up any whitespace
passed=$(echo $passed | tr -d '[:space:]')
failed=$(echo $failed | tr -d '[:space:]')

# Binary reward: 1 if all tests pass (no failures), 0 otherwise
# This ensures complete implementation is required
if [ "$failed" = "0" ] && [ "$passed" -gt 0 ]; then
    echo "1" > /logs/verifier/reward.txt
    echo "SUCCESS: All tests passed ($passed total)"
else
    echo "0" > /logs/verifier/reward.txt
    echo "FAILURE: $failed tests failed, $passed passed"
fi

echo "Results: $passed passed, $failed failed"
cat /logs/verifier/reward.txt

# --- LLM Judge (Track 3 + Track 4) ---
if [ -f /tests/eval_manifest.yaml ] && [ -f /tests/standalone_judge.py ]; then
    # Capture agent diff
    mkdir -p /logs/verifier
    _repo_dir=""
    for candidate in /workspace/*/ /repo /app /src; do
        if [ -d "${candidate}/.git" ]; then
            _repo_dir="$candidate"
            break
        fi
    done
    if [ -z "$_repo_dir" ]; then
        _repo_dir=$(find /workspace /repo /app /src -maxdepth 3 -type d -name .git 2>/dev/null | head -1 | xargs -r dirname)
    fi
    if [ -n "$_repo_dir" ] && [ -d "$_repo_dir/.git" ]; then
        (cd "$_repo_dir" && git add -A 2>/dev/null && git diff --cached > /logs/verifier/agent.diff 2>/dev/null) || true
    fi

    # Install PyYAML if needed (lightweight, <1s)
    python3 -c "import yaml" 2>/dev/null || \
        python3 -m pip install -q pyyaml 2>/dev/null || \
        pip3 install -q --break-system-packages pyyaml 2>/dev/null || true

    # Run LLM judge (writes track3_rubric.json + track4_distractors.json)
    python3 /tests/standalone_judge.py /tests/eval_manifest.yaml /logs/verifier/agent.diff 2>&1 || true
fi
