#!/bin/bash
# Test runner script executed inside Docker

set -e
cd /workspace/example-repo || exit 1

# Create temp directory for cache files (read-only filesystem issues)
export PYTHONDONTWRITEBYTECODE=1
export MYPY_CACHE_DIR=/tmp/mypy_cache
export RUFF_CACHE_DIR=/tmp/ruff_cache
mkdir -p "$MYPY_CACHE_DIR" "$RUFF_CACHE_DIR"

# Run pytest with the test_outputs.py file and capture results
# fail_to_pass tests: test_syntax_error_fixed, test_import_works
# pass_to_pass tests: test_repo_linter_passes, test_repo_typecheck_passes, test_repo_unit_tests_specific, test_repo_imports_clean

python -m pytest /tests/test_outputs.py -v --tb=short 2>&1 || true

# Calculate reward based on test results
# Reward = 1 if all fail_to_pass tests pass, 0 otherwise
# (pass_to_pass tests are for validation but the key metric is fail_to_pass)

# Run pytest again with json output to calculate reward
python -m pytest /tests/test_outputs.py --co -q 2>/dev/null | grep -E "^test_" > /tmp/test_list.txt

# Check if critical fail_to_pass tests pass
set +e
python -m pytest /tests/test_outputs.py::test_syntax_error_fixed -v --tb=short >/dev/null 2>&1
SYNTAX_OK=$?

python -m pytest /tests/test_outputs.py::test_import_works -v --tb=short >/dev/null 2>&1
IMPORT_OK=$?
set -e

# Calculate reward (both fail_to_pass tests must pass)
if [ $SYNTAX_OK -eq 0 ] && [ $IMPORT_OK -eq 0 ]; then
    REWARD=1
else
    REWARD=0
fi

# Write reward to file
mkdir -p /logs/verifier
echo "$REWARD" > /logs/verifier/reward.txt
echo "Reward: $REWARD"
