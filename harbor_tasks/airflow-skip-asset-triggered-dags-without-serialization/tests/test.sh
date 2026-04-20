#!/bin/bash
set -e

# Ensure log directory exists
mkdir -p /logs/verifier

# Initialize Airflow database (required for DB tests)
cd /workspace/airflow
export AIRFLOW__CORE__UNIT_TEST_MODE=True
export AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=sqlite:///:memory:
export PYTHONPATH="/workspace/airflow/airflow-core/src:/workspace/airflow/devel-common/src:/workspace/airflow/task-sdk/src:/workspace/airflow/shared:$PYTHONPATH"

# Run the tests from within the repo's uv environment
uv run --project airflow-core python -m pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/pytest.log || true

# Determine reward: all tests passed = 1, any failed = 0
if grep -q "passed" /logs/verifier/pytest.log && ! grep -E "FAILED|ERROR" /logs/verifier/pytest.log | grep -q "test_outputs.py"; then
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
