#!/usr/bin/env bash
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
REPO="/repo"
REWARD=0.0
TOTAL=0.0

cd "$REPO"

###############################################################################
# GATE: Rust syntax check — async_zero_sleep.rs must parse
###############################################################################
# [pr_diff] (gate): async_zero_sleep.rs must be valid Rust syntax
SOURCE_RS="crates/ruff_linter/src/rules/flake8_async/rules/async_zero_sleep.rs"
if ! python3 -c "
import subprocess, sys
result = subprocess.run(
    ['rustfmt', '--check', '--edition', '2021', '$SOURCE_RS'],
    capture_output=True, text=True
)
# rustfmt --check exits 1 if formatting differs, but 0 or 1 both mean parseable
# Exit code 2+ means parse error
sys.exit(0 if result.returncode < 2 else 1)
"; then
    echo "GATE FAILED: async_zero_sleep.rs has syntax errors"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    exit 0
fi
echo "GATE PASSED: async_zero_sleep.rs parses"

###############################################################################
# Build ruff (needed for behavioral tests)
###############################################################################
echo "Building ruff..."
if ! cargo build --bin ruff 2>/tmp/build_err.txt; then
    echo "BUILD FAILED — cannot run behavioral tests"
    cat /tmp/build_err.txt | tail -20
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    exit 0
fi
RUFF="./target/debug/ruff"
echo "Build succeeded."

###############################################################################
# Helper
###############################################################################
add_score() {
    local weight="$1" pass="$2" label="$3"
    TOTAL=$(python3 -c "print($TOTAL + $weight)")
    if [ "$pass" -eq 1 ]; then
        REWARD=$(python3 -c "print($REWARD + $weight)")
        echo "PASS ($weight): $label"
    else
        echo "FAIL ($weight): $label"
    fi
}

###############################################################################
# Behavioral: fail-to-pass tests (0.65 total)
###############################################################################

# Test file: anyio.sleep(0) via aliased import
cat > /tmp/test_anyio_alias.py <<'PYEOF'
from anyio import sleep as anyio_sleep

async def func():
    await anyio_sleep(0)
PYEOF

# [pr_diff] (0.30): Autofix for anyio must use `import anyio.lowlevel`, not `from anyio import lowlevel`
FIXED=$($RUFF check --select ASYNC115 --fix --no-cache --diff /tmp/test_anyio_alias.py 2>&1 || true)
if echo "$FIXED" | grep -q 'import anyio\.lowlevel'; then
    # Verify it does NOT use `from anyio import lowlevel`
    if echo "$FIXED" | grep -q 'from anyio import lowlevel'; then
        add_score 0.30 0 "anyio autofix uses submodule import (not from-import)"
    else
        add_score 0.30 1 "anyio autofix uses submodule import (not from-import)"
    fi
else
    add_score 0.30 0 "anyio autofix uses submodule import (not from-import)"
fi

# [pr_diff] (0.20): Autofix for anyio produces `anyio.lowlevel.checkpoint()` call
if echo "$FIXED" | grep -q 'anyio\.lowlevel\.checkpoint()'; then
    add_score 0.20 1 "anyio autofix produces anyio.lowlevel.checkpoint() call"
else
    add_score 0.20 0 "anyio autofix produces anyio.lowlevel.checkpoint() call"
fi

# Test file: direct anyio.sleep(0) call
cat > /tmp/test_anyio_direct.py <<'PYEOF'
import anyio

async def func():
    await anyio.sleep(0)
PYEOF

# [pr_diff] (0.15): Autofix for direct anyio.sleep(0) also uses submodule import
FIXED2=$($RUFF check --select ASYNC115 --fix --no-cache --diff /tmp/test_anyio_direct.py 2>&1 || true)
if echo "$FIXED2" | grep -q 'import anyio\.lowlevel'; then
    if echo "$FIXED2" | grep -q 'from anyio import lowlevel'; then
        add_score 0.15 0 "direct anyio.sleep(0) autofix uses submodule import"
    else
        add_score 0.15 1 "direct anyio.sleep(0) autofix uses submodule import"
    fi
else
    add_score 0.15 0 "direct anyio.sleep(0) autofix uses submodule import"
fi

###############################################################################
# Regression: pass-to-pass (0.15 total)
###############################################################################

# Test file: trio.sleep(0) should still work (trio.lowlevel is re-exported)
cat > /tmp/test_trio.py <<'PYEOF'
import trio

async def func():
    await trio.sleep(0)
PYEOF

# [pr_diff] (0.05): trio autofix still produces valid checkpoint() replacement
FIXED_TRIO=$($RUFF check --select ASYNC115 --fix --no-cache --diff /tmp/test_trio.py 2>&1 || true)
if echo "$FIXED_TRIO" | grep -q 'trio\.lowlevel\.checkpoint()'; then
    add_score 0.05 1 "trio autofix still produces trio.lowlevel.checkpoint()"
else
    add_score 0.05 0 "trio autofix still produces trio.lowlevel.checkpoint()"
fi

# [pr_diff] (0.05): trio.sleep(1) is NOT flagged (only zero-sleep is ASYNC115)
cat > /tmp/test_trio_ok.py <<'PYEOF'
import trio

async def func():
    await trio.sleep(1)
PYEOF
OUTPUT_OK=$($RUFF check --select ASYNC115 --no-cache /tmp/test_trio_ok.py 2>&1 || true)
if echo "$OUTPUT_OK" | grep -q "ASYNC115"; then
    add_score 0.05 0 "trio.sleep(1) not flagged"
else
    add_score 0.05 1 "trio.sleep(1) not flagged"
fi

# [pr_diff] (0.05): Run upstream snapshot tests for ASYNC115
if cargo test -p ruff_linter -- flake8_async::tests::ASYNC115 2>&1 | tail -5 | grep -q "test result: ok"; then
    add_score 0.05 1 "Upstream ASYNC115 snapshot tests pass"
else
    add_score 0.05 0 "Upstream ASYNC115 snapshot tests pass"
fi

###############################################################################
# Structural: anti-stub (0.10)
###############################################################################

# [pr_diff] (0.10): The import strategy must differentiate between import and import_from
# We check that the code uses ImportRequest::import (not just import_from) for the fix.
# This is a minimal structural check — the behavioral tests above are the primary signal.
# WHY AST/grep: the distinction is in which Rust API is called, which can only be verified
# by inspecting the source, not by running ruff on Python test files (the behavioral tests
# verify the _output_ but not which code path produced it).
if grep -q 'ImportRequest::import(' "$SOURCE_RS" | head -1; then
    # Ensure it's not ONLY import_from
    if grep 'ImportRequest::import(' "$SOURCE_RS" | grep -vq 'import_from'; then
        add_score 0.10 1 "Uses ImportRequest::import (submodule-aware import strategy)"
    else
        add_score 0.10 0 "Uses ImportRequest::import (submodule-aware import strategy)"
    fi
else
    add_score 0.10 0 "Uses ImportRequest::import (submodule-aware import strategy)"
fi

###############################################################################
# Config-derived checks (0.10)
###############################################################################

# [agent_config] (0.05): "All changes must be tested" — AGENTS.md:72
# Check that the test fixture file has an anyio-specific aliased import test case
FIXTURE="crates/ruff_linter/resources/test/fixtures/flake8_async/ASYNC115.py"
if [ -f "$FIXTURE" ] && grep -q 'anyio.*sleep.*anyio_sleep\|from anyio import sleep as' "$FIXTURE"; then
    add_score 0.05 1 "Test fixture includes anyio aliased import case (AGENTS.md:62)"
else
    add_score 0.05 0 "Test fixture includes anyio aliased import case (AGENTS.md:62)"
fi

# [agent_config] (0.05): "Follow existing code style. Check neighboring files for patterns." — AGENTS.md:75
# Imports in Rust should be at top of file, not locally in functions
if grep -n 'use crate' "$SOURCE_RS" | tail -1 | grep -qP '^\d+:' && \
   ! grep -A5 'pub(crate) fn async_zero_sleep' "$SOURCE_RS" | grep -q '^[[:space:]]*use '; then
    add_score 0.05 1 "No local imports in function body (AGENTS.md:65)"
else
    add_score 0.05 0 "No local imports in function body (AGENTS.md:65)"
fi

###############################################################################
# Final score
###############################################################################
echo ""
echo "Total: $REWARD / $TOTAL"
echo "$REWARD" > /logs/verifier/reward.txt

BEHAVIORAL=$(python3 -c "print(min($REWARD, 0.65))")
echo "{\"reward\": $REWARD, \"behavioral\": $BEHAVIORAL, \"regression\": 0.0, \"config\": 0.0, \"style_rubric\": 0.0}" > /logs/verifier/reward.json

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
