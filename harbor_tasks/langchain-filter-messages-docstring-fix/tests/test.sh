#!/bin/bash

# Create logs directory
mkdir -p /logs/verifier

# Run pytest and capture exit code
pytest /tests/test_outputs.py -v --tb=short > /logs/verifier/pytest.log 2>&1
exit_code=$?

# Calculate reward (binary: 1 if pytest passes, 0 otherwise)
if [ "$exit_code" -eq 0 ]; then
    reward=1
else
    reward=0
fi

echo "pytest exit code: $exit_code"
echo "Reward: $reward"

# Write reward to file
echo "$reward" > /logs/verifier/reward.txt

# --- LLM Judge (Track 3 + Track 4) ---
if [ -f /tests/eval_manifest.yaml ] && [ -f /tests/standalone_judge.py ]; then
    # Capture agent diff
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

    # Run LLM judge (writes track3_rubric.json + track4_distractors.json)
    python3 /tests/standalone_judge.py /tests/eval_manifest.yaml /logs/verifier/agent.diff 2>&1 || true
fi
