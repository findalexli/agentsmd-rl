#!/bin/bash
set -e

REPO="/workspace/router"
LOG_DIR="/logs/verifier"
REWARD_FILE="$LOG_DIR/reward.txt"

mkdir -p "$LOG_DIR"

# Install pytest (use --break-system-packages for externally-managed env)
pip3 install pytest --quiet --break-system-packages || pip3 install pytest --quiet

# Run the test file - allow failure since we're testing
set +e
cd "$REPO"
python3 -m pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee "$LOG_DIR/test_output.log"
set -e

# Calculate reward from pytest output - only count fail_to_pass tests
# The fail_to_pass tests are the first 6 tests (indices 0-5 in eval_manifest.yaml)
# These are the tests that should fail on buggy code and pass on fixed code

FAIL_TO_PASS_TESTS="test_script_file_exists test_script_is_valid_javascript test_changeset_version_script_updated test_script_updates_example_dependencies test_script_preserves_json_formatting test_script_excludes_node_modules"

F2P_PASSED=0
F2P_FAILED=0

for test_name in $FAIL_TO_PASS_TESTS; do
    if grep -q "$test_name.*PASSED" "$LOG_DIR/test_output.log"; then
        F2P_PASSED=$((F2P_PASSED + 1))
    elif grep -q "$test_name.*FAILED" "$LOG_DIR/test_output.log"; then
        F2P_FAILED=$((F2P_FAILED + 1))
    fi
done

F2P_TOTAL=$((F2P_PASSED + F2P_FAILED))

if [ "$F2P_TOTAL" -eq 0 ]; then
    echo "0" > "$REWARD_FILE"
else
    # Calculate reward as passed/total for fail-to-pass tests only
    python3 -c "print($F2P_PASSED / $F2P_TOTAL)" > "$REWARD_FILE"
fi

# Also log the full results for reference
echo "Fail-to-pass tests: $F2P_PASSED passed, $F2P_FAILED failed out of $F2P_TOTAL"

echo "Reward: $(cat $REWARD_FILE)"
