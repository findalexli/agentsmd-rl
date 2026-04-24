#!/bin/bash

# Standardized test runner for benchmark tasks
# This script is called by the verifier to run test_outputs.py

# Set up logging
mkdir -p /logs/verifier
REWARD_FILE="/logs/verifier/reward.txt"
LOG_FILE="/logs/verifier/test_output.log"

# Run pytest on test_outputs.py and capture output
python3 -m pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee "$LOG_FILE"
PYTEST_EXIT=${PIPESTATUS[0]}

if [ $PYTEST_EXIT -eq 0 ]; then
    # All tests passed
    echo "1" > "$REWARD_FILE"
    echo "SUCCESS: All tests passed. Reward = 1"
else
    # Some tests failed
    echo "0" > "$REWARD_FILE"
    echo "FAILURE: Some tests failed. Reward = 0"
fi

# Return 0 regardless of test results - the reward file contains the signal
# exit 0   # auto-disabled (prevented judge block from running)
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
