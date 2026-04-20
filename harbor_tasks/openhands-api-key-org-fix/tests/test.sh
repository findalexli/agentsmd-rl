#!/bin/bash
set -e

# Change to tests directory
cd /workspace/task/tests

# Install pytest and pytest-asyncio for async test support
pip install pytest pytest-asyncio -q

# Run the tests and capture output
pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.log || true

# Check if all tests passed
if grep -q "FAILED" /logs/verifier/test_output.log; then
    echo "0" > /logs/verifier/reward.txt
    echo "Tests FAILED"
    exit 1
elif grep -q "passed" /logs/verifier/test_output.log; then
    # Count passed vs total
    passed=$(grep -oP '\d+ passed' /logs/verifier/test_output.log | grep -oP '\d+' | head -1)
    total=$(grep -oP '\d+ items' /logs/verifier/test_output.log | grep -oP '\d+' | head -1)

    if [ -z "$passed" ] || [ -z "$total" ]; then
        echo "0" > /logs/verifier/reward.txt
        echo "Could not determine test results"
        exit 1
    fi

    # Calculate reward as passed/total
    reward=$(python3 -c "print($passed / $total)")
    echo "$reward" > /logs/verifier/reward.txt
    echo "Tests PASSED: $passed/$total (reward: $reward)"
    exit 0
else
    echo "0" > /logs/verifier/reward.txt
    echo "No test results found"
    exit 1
fi

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
