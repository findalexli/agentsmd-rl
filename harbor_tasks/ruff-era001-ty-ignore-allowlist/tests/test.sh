#!/usr/bin/env bash
set -euo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
REPO="/repo"
REWARD=0.0
TOTAL=0.0

cd "$REPO"

###############################################################################
# GATE: Rust syntax check — detection.rs must parse
###############################################################################
# [pr_diff] (gate): detection.rs must be valid Rust syntax
DETECTION_RS="crates/ruff_linter/src/rules/eradicate/detection.rs"
if ! python3 -c "
import subprocess, sys
result = subprocess.run(
    ['rustfmt', '--check', '--edition', '2021', '$DETECTION_RS'],
    capture_output=True, text=True
)
# rustfmt --check exits 1 if formatting differs, but 0 or 1 both mean parseable
# Exit code 2+ means parse error
sys.exit(0 if result.returncode < 2 else 1)
"; then
    echo "GATE FAILED: detection.rs has syntax errors"
    echo "0.0" > /logs/verifier/reward.txt
    echo '{"reward": 0.0, "behavioral": 0.0, "regression": 0.0, "config": 0.0, "style_rubric": 0.0}' > /logs/verifier/reward.json
    exit 0
fi
echo "GATE PASSED: detection.rs parses"

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

# Create test file with ty: ignore comments
cat > /tmp/test_ty_ignore.py <<'PYEOF'
import foo  # ty: ignore[unresolved-import]
# ty: ignore
x: int = "hello"  # ty:ignore
# ty: ignore[missing-argument, invalid-argument-type]
# ty: ignore[]
# ty:ignore[import]
PYEOF

# [pr_diff] (0.30): ty: ignore comments must NOT be flagged as ERA001
OUTPUT=$($RUFF check --select ERA001 --no-cache /tmp/test_ty_ignore.py 2>&1 || true)
if echo "$OUTPUT" | grep -q "ERA001"; then
    add_score 0.30 0 "ty: ignore comments should not trigger ERA001"
else
    add_score 0.30 1 "ty: ignore comments should not trigger ERA001"
fi

# [pr_diff] (0.15): ty:ignore (no space) must NOT be flagged
cat > /tmp/test_ty_nospace.py <<'PYEOF'
# ty:ignore
# ty:ignore[some-code]
PYEOF
OUTPUT=$($RUFF check --select ERA001 --no-cache /tmp/test_ty_nospace.py 2>&1 || true)
if echo "$OUTPUT" | grep -q "ERA001"; then
    add_score 0.15 0 "ty:ignore (no space) not flagged"
else
    add_score 0.15 1 "ty:ignore (no space) not flagged"
fi

# [pr_diff] (0.10): ty: ignore with multiple codes in brackets must NOT be flagged
cat > /tmp/test_ty_multi.py <<'PYEOF'
# ty: ignore[missing-argument, invalid-argument-type]
PYEOF
OUTPUT=$($RUFF check --select ERA001 --no-cache /tmp/test_ty_multi.py 2>&1 || true)
if echo "$OUTPUT" | grep -q "ERA001"; then
    add_score 0.10 0 "ty: ignore with multiple codes not flagged"
else
    add_score 0.10 1 "ty: ignore with multiple codes not flagged"
fi

# [pr_diff] (0.10): Actual commented-out code must STILL be flagged
cat > /tmp/test_real_code.py <<'PYEOF'
# import os
# x = 1 + 2
PYEOF
OUTPUT=$($RUFF check --select ERA001 --no-cache /tmp/test_real_code.py 2>&1 || true)
if echo "$OUTPUT" | grep -q "ERA001"; then
    add_score 0.10 1 "Actual commented-out code still flagged"
else
    add_score 0.10 0 "Actual commented-out code still flagged"
fi

###############################################################################
# Regression: pass-to-pass (0.15 total)
###############################################################################

# [pr_diff] (0.05): type: ignore still allowlisted
cat > /tmp/test_type_ignore.py <<'PYEOF'
# type: ignore
# type: ignore[import]
# type:ignore
PYEOF
OUTPUT=$($RUFF check --select ERA001 --no-cache /tmp/test_type_ignore.py 2>&1 || true)
if echo "$OUTPUT" | grep -q "ERA001"; then
    add_score 0.05 0 "type: ignore still allowlisted"
else
    add_score 0.05 1 "type: ignore still allowlisted"
fi

# [pr_diff] (0.05): mypy/pyright comments still allowlisted
cat > /tmp/test_other_tools.py <<'PYEOF'
# mypy: ignore-errors
# pyright: ignore-errors
PYEOF
OUTPUT=$($RUFF check --select ERA001 --no-cache /tmp/test_other_tools.py 2>&1 || true)
if echo "$OUTPUT" | grep -q "ERA001"; then
    add_score 0.05 0 "mypy/pyright still allowlisted"
else
    add_score 0.05 1 "mypy/pyright still allowlisted"
fi

# [pr_diff] (0.05): Run upstream Rust unit tests for the detection module
if cargo test -p ruff_linter -- eradicate::detection 2>&1 | tail -5 | grep -q "test result: ok"; then
    add_score 0.05 1 "Upstream detection unit tests pass"
else
    add_score 0.05 0 "Upstream detection unit tests pass"
fi

###############################################################################
# Structural: anti-stub (0.10)
###############################################################################

# [pr_diff] (0.10): ALLOWLIST_REGEX must contain a ty pattern
if grep -qP 'ty.*ignore' "$DETECTION_RS"; then
    add_score 0.10 1 "ALLOWLIST_REGEX contains ty ignore pattern"
else
    add_score 0.10 0 "ALLOWLIST_REGEX contains ty ignore pattern"
fi

###############################################################################
# Config-derived checks (0.10)
###############################################################################

# [agent_config] (0.05): "All changes must be tested" — AGENTS.md:62
# Check that the agent added at least one test assertion for ty:ignore
if grep -qP 'ty.*ignore' crates/ruff_linter/src/rules/eradicate/detection.rs | head -1 && \
   grep -c 'assert' crates/ruff_linter/src/rules/eradicate/detection.rs | grep -qP '[0-9]'; then
    # More specific: check that there's a test with ty in the test module
    if grep -A200 'mod tests' "$DETECTION_RS" | grep -q 'ty'; then
        add_score 0.05 1 "Agent added tests for ty:ignore (AGENTS.md:62)"
    else
        add_score 0.05 0 "Agent added tests for ty:ignore (AGENTS.md:62)"
    fi
else
    # Simpler check: tests section mentions ty
    if grep -A200 'mod tests' "$DETECTION_RS" | grep -q 'ty'; then
        add_score 0.05 1 "Agent added tests for ty:ignore (AGENTS.md:62)"
    else
        add_score 0.05 0 "Agent added tests for ty:ignore (AGENTS.md:62)"
    fi
fi

# [agent_config] (0.05): "Follow existing code style" — AGENTS.md:65
# The existing allowlist entries use `|   pattern` format with 4-space indent after pipe
# Check that any new line in the allowlist section follows this pattern
if grep -P '^\s+\|\s+ty' "$DETECTION_RS" | grep -qP '^\s+\|\s+ty:\s*'; then
    add_score 0.05 1 "New allowlist entry follows existing code style (AGENTS.md:65)"
else
    add_score 0.05 0 "New allowlist entry follows existing code style (AGENTS.md:65)"
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
