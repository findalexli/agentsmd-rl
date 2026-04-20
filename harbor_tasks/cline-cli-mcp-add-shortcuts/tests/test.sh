#!/bin/bash
# Note: not using set -e because we need to check test results manually

# Install pytest if not already installed
pip3 install pytest --quiet --break-system-packages 2>/dev/null || pip3 install pytest --quiet

# Run tests with pytest
cd /tests
python3 -m pytest test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest_output.txt
PYTEST_EXIT=${PIPESTATUS[0]}

# Parse test counts from the summary line
# Extract numbers from "=== X passed, Y failed, Z warnings ==="
PASSED=$(grep -oE "[0-9]+ passed" /logs/verifier/pytest_output.txt 2>/dev/null | head -1 | grep -oE "[0-9]+" || echo "0")
FAILED=$(grep -oE "[0-9]+ failed" /logs/verifier/pytest_output.txt 2>/dev/null | head -1 | grep -oE "[0-9]+" || echo "0")

# If we didn't get values from summary, fall back to test definition count
if [ -z "$PASSED" ] || [ "$PASSED" = "" ]; then
    PASSED="0"
fi
if [ -z "$FAILED" ] || [ "$FAILED" = "" ]; then
    FAILED="0"
fi

# Count total tests from test file
TOTAL=$(grep -c "^def test_" /tests/test_outputs.py 2>/dev/null || echo "0")

# Strip any whitespace
TOTAL=$(echo "$TOTAL" | tr -d '[:space:]')
PASSED=$(echo "$PASSED" | tr -d '[:space:]')
FAILED=$(echo "$FAILED" | tr -d '[:space:]')

echo "Tests: $PASSED passed, $FAILED failed (out of $TOTAL total)"
echo "Pytest exit code: $PYTEST_EXIT"

# All tests must pass for reward=1
if [ "$FAILED" -eq 0 ] && [ "$PASSED" -gt 0 ] && [ "$PASSED" -eq "$TOTAL" ]; then
    echo "1" > /logs/verifier/reward.txt
    echo "SUCCESS: All tests passed"
else
    echo "0" > /logs/verifier/reward.txt
    echo "FAILURE: Some tests failed"
fi

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
