#!/bin/bash
set -e

# Setup logging
mkdir -p /logs/verifier
LOG_FILE="/logs/verifier/test_output.log"
REWARD_FILE="/logs/verifier/reward.txt"

# Run pytest and capture result
if pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee "$LOG_FILE"; then
    # Check if any tests actually failed (pytest returns 0 only if all pass)
    if grep -q "FAILED" "$LOG_FILE"; then
        echo "0" > "$REWARD_FILE"
        echo "FAILURE: Some tests failed"
    elif grep -q "passed" "$LOG_FILE"; then
        echo "1" > "$REWARD_FILE"
        echo "SUCCESS: All tests passed"
    else
        echo "0" > "$REWARD_FILE"
        echo "FAILURE: No test results found"
    fi
else
    # pytest command failed
    echo "0" > "$REWARD_FILE"
    echo "FAILURE: pytest command failed or tests failed"
fi

cat "$REWARD_FILE"

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
