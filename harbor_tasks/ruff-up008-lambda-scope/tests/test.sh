#!/usr/bin/env bash
# Verifier for ruff-up008-lambda-scope
# Bug: UP008 misses super() simplification in lambda class attributes
set +e

REWARD_FILE="/logs/verifier/reward.txt"
REWARD_JSON="/logs/verifier/reward.json"
mkdir -p "$(dirname "$REWARD_FILE")"

RUST_FILE="/workspace/ruff/crates/ruff_linter/src/rules/pyupgrade/rules/super_call_with_parameters.rs"
FIXTURE="/workspace/ruff/crates/ruff_linter/resources/test/fixtures/pyupgrade/UP008.py"
SNAPSHOT="/workspace/ruff/crates/ruff_linter/src/rules/pyupgrade/snapshots/ruff_linter__rules__pyupgrade__tests__UP008.py.snap"

echo "=== ruff-up008-lambda-scope verifier ==="

# Initialize score components
SCORE_BEHAV=0.0
SCORE_STRUCT=0.0
SCORE_CONFIG=0.0

# -- GATE: files exist --
# [static] (gate): Target files must exist
echo ""
echo "GATE: Target files exist"
if [ ! -f "$RUST_FILE" ]; then
    echo "GATE FAIL: Rust source file missing"
    echo "0.0000" > "$REWARD_FILE"
    echo '{"reward": 0.0, "behavioral": 0.0, "structural": 0.0, "config": 0.0}' > "$REWARD_JSON"
    exit 0
fi
if [ ! -f "$FIXTURE" ]; then
    echo "GATE FAIL: fixture file missing"
    echo "0.0000" > "$REWARD_FILE"
    echo '{"reward": 0.0, "behavioral": 0.0, "structural": 0.0, "config": 0.0}' > "$REWARD_JSON"
    exit 0
fi
echo "GATE PASS"

# Compile ruff once for behavioral tests
echo ""
echo "SETUP: Compiling ruff (this may take a moment)..."
cd /workspace/ruff
cargo build --release -p ruff 2>/dev/null
COMPILE_STATUS=$?
if [ $COMPILE_STATUS -ne 0 ]; then
    echo "BUILD FAIL: Could not compile ruff"
    echo "0.0000" > "$REWARD_FILE"
    echo '{"reward": 0.0, "behavioral": 0.0, "structural": 0.0, "config": 0.0}' > "$REWARD_JSON"
    exit 0
fi
echo "BUILD PASS: ruff compiled successfully"

# Weights: >=60% behavioral, <=40% structural
W_BEHAV_LAMBDA_DETECTED=0.35   # [pr_diff] Lambda super() call detected by UP008
W_BEHAV_FIX_APPLIED=0.25       # [pr_diff] Fix can be applied to lambda case
W_P2P_UPSTREAM=0.15            # [repo_tests] Upstream UP008 tests pass
W_STRUCT_TODO_REMOVED=0.10     # [pr_diff] TODO comment removed
W_STRUCT_SNAPSHOT_UPDATED=0.10 # [pr_diff] Snapshot reflects lambda detection
W_CONFIG_NO_PANIC=0.05         # [agent_config] Avoid panic!/unwrap - AGENTS.md:79

# -- TEST 1 (BEHAVIORAL): Lambda super() call detected by UP008 --
# [pr_diff] (0.35): Lambda with super(LambdaMethod, self) should trigger UP008
echo ""
echo "TEST 1: behavioral -- Lambda super() call detected by UP008 (weight=$W_BEHAV_LAMBDA_DETECTED)"
T1=$(python3 << 'PYEOF'
import subprocess
import sys

# Run ruff on the fixture and capture output
result = subprocess.run(
    ['./target/release/ruff', 'check', '--select', 'UP008', '--output-format', 'text',
     'crates/ruff_linter/resources/test/fixtures/pyupgrade/UP008.py'],
    capture_output=True, text=True, cwd='/workspace/ruff', timeout=30
)

output = result.stdout + result.stderr

# Check if LambdaMethod is mentioned with UP008 (indicating detection)
# The fix should detect: f = lambda self: super(LambdaMethod, self).f()
if 'LambdaMethod' in output and ('UP008' in output or 'super()' in output):
    print("PASS: UP008 detects super() in LambdaMethod lambda")
    sys.exit(0)
else:
    print("FAIL: LambdaMethod not detected by UP008")
    print(f"Output: {output[:500]}")
    sys.exit(1)
PYEOF
)
T1_STATUS=$?
echo "$T1"
if [ $T1_STATUS -eq 0 ]; then
    SCORE_BEHAV=$(python3 -c "print($SCORE_BEHAV + $W_BEHAV_LAMBDA_DETECTED)")
fi

# -- TEST 2 (BEHAVIORAL): Lambda case fix can be applied --
# [pr_diff] (0.25): The lambda case should have a fix available (autofix)
echo ""
echo "TEST 2: behavioral -- Lambda super() fix is available (weight=$W_BEHAV_FIX_APPLIED)"
T2=$(python3 << 'PYEOF'
import subprocess
import sys

# Run ruff with --fix to check if fix is available
result = subprocess.run(
    ['./target/release/ruff', 'check', '--select', 'UP008', '--fix', '--diff',
     'crates/ruff_linter/resources/test/fixtures/pyupgrade/UP008.py'],
    capture_output=True, text=True, cwd='/workspace/ruff', timeout=30
)

output = result.stdout + result.stderr

# Check if the fix suggests super() without arguments for LambdaMethod
# The fix should change super(LambdaMethod, self) to super()
lambda_fixed = 'LambdaMethod' in output and ('super()' in output or '- super(LambdaMethod' in output)

# Alternative: check if the fix would remove the parameters
if lambda_fixed or ('super()' in output and 'LambdaMethod' in output):
    print("PASS: Fix available to simplify super() in lambda")
    sys.exit(0)
else:
    # Check the original fixture line is still there (meaning it wasn't fixed)
    with open('/workspace/ruff/crates/ruff_linter/resources/test/fixtures/pyupgrade/UP008.py') as f:
        content = f.read()
    if 'super(LambdaMethod, self)' in content:
        print("FAIL: Lambda case present but no fix applied")
    else:
        print("FAIL: Lambda case not found or check not working")
    sys.exit(1)
PYEOF
)
T2_STATUS=$?
echo "$T2"
if [ $T2_STATUS -eq 0 ]; then
    SCORE_BEHAV=$(python3 -c "print($SCORE_BEHAV + $W_BEHAV_FIX_APPLIED)")
fi

# Gate structural tests behind basic behavioral success
BEHAV_PASSED=0
if [ $(python3 -c "print(1 if $SCORE_BEHAV >= 0.30 else 0)") -eq 1 ]; then
    BEHAV_PASSED=1
    echo ""
    echo "=== Behavioral tests passed, proceeding to structural checks ==="
else
    echo ""
    echo "=== Behavioral tests failed, structural checks gated ==="
fi

# -- TEST 3 (PASS-TO-PASS): Upstream tests pass --
# [repo_tests] (0.15): UP008 tests should not break existing functionality
echo ""
echo "TEST 3: pass-to-pass -- Upstream UP008 tests pass (weight=$W_P2P_UPSTREAM)"
T3_STATUS=1
if [ $BEHAV_PASSED -eq 1 ]; then
    T3=$(cd /workspace/ruff && cargo test -p ruff_linter --lib -- rules::pyupgrade::tests::UP008 2>&1)
    T3_TEST_STATUS=$?
    echo "$T3" | tail -20
    if [ $T3_TEST_STATUS -eq 0 ]; then
        echo "PASS: Upstream UP008 tests pass"
        T3_STATUS=0
    else
        echo "FAIL: Upstream UP008 tests failed"
    fi
else
    echo "SKIP: Gated behind behavioral tests"
fi
if [ $T3_STATUS -eq 0 ]; then
    SCORE_BEHAV=$(python3 -c "print($SCORE_BEHAV + $W_P2P_UPSTREAM)")
fi

# -- TEST 4 (STRUCTURAL): TODO comment removed from fixture --
# [pr_diff] (0.10): TODO comment about lambda being missed is no longer needed
echo ""
echo "TEST 4: structural -- TODO comment removed (weight=$W_STRUCT_TODO_REMOVED)"
T4_STATUS=1
if [ $BEHAV_PASSED -eq 1 ]; then
    T4=$(python3 << 'PYEOF'
import sys
with open("/workspace/ruff/crates/ruff_linter/resources/test/fixtures/pyupgrade/UP008.py") as f:
    source = f.read()
# The old code had: # TODO(charlie): class-body lambda rewrite is still missed.
if "lambda rewrite is still missed" in source or "TODO(charlie): class-body lambda" in source:
    print("FAIL: TODO comment about lambda still present")
    sys.exit(1)
else:
    print("PASS: TODO comment about lambda removed from fixture")
    sys.exit(0)
PYEOF
)
    T4_STATUS=$?
    echo "$T4"
else
    echo "SKIP: Gated behind behavioral tests"
fi
if [ $T4_STATUS -eq 0 ]; then
    SCORE_STRUCT=$(python3 -c "print($SCORE_STRUCT + $W_STRUCT_TODO_REMOVED)")
fi

# -- TEST 5 (STRUCTURAL): Snapshot shows lambda detection --
# [pr_diff] (0.10): Snapshot file contains LambdaMethod diagnostic
echo ""
echo "TEST 5: structural -- Snapshot updated with LambdaMethod (weight=$W_STRUCT_SNAPSHOT_UPDATED)"
T5_STATUS=1
if [ $BEHAV_PASSED -eq 1 ]; then
    T5=$(python3 << 'PYEOF'
import sys
with open("/workspace/ruff/crates/ruff_linter/src/rules/pyupgrade/snapshots/ruff_linter__rules__pyupgrade__tests__UP008.py.snap") as f:
    snap = f.read()
# After fix, snapshot should show LambdaMethod detection
has_lambda = "LambdaMethod" in snap
has_lambda_line = "lambda self: super" in snap or "LambdaMethod, self" in snap
if has_lambda and has_lambda_line:
    print("PASS: Snapshot contains LambdaMethod lambda detection")
    sys.exit(0)
else:
    print("FAIL: Snapshot missing LambdaMethod detection")
    sys.exit(1)
PYEOF
)
    T5_STATUS=$?
    echo "$T5"
else
    echo "SKIP: Gated behind behavioral tests"
fi
if [ $T5_STATUS -eq 0 ]; then
    SCORE_STRUCT=$(python3 -c "print($SCORE_STRUCT + $W_STRUCT_SNAPSHOT_UPDATED)")
fi

# -- TEST 6 (CONFIG): Avoid panic!/unwrap --
# [agent_config] (0.05): "Try hard to avoid patterns that require panic!, unreachable!, or unwrap()" - AGENTS.md:79
echo ""
echo "TEST 6: config-derived -- avoid panic!/unwrap (weight=$W_CONFIG_NO_PANIC)"
T6_STATUS=1
if [ $BEHAV_PASSED -eq 1 ]; then
    T6=$(python3 << 'PYEOF'
import os
import sys
import re

os.chdir('/workspace/ruff')

# Check the main changed file for panic/unwrap
with open('crates/ruff_linter/src/rules/pyupgrade/rules/super_call_with_parameters.rs') as f:
    content = f.read()

# Count problematic patterns (excluding comments)
lines = content.split('\n')
warns = 0
for line in lines:
    code = line.split('//')[0].strip()
    if not code:
        continue
    # Check for panic!, unreachable!, .unwrap() not in test context
    if 'panic!(' in code or 'unreachable!(' in code or '.unwrap()' in code:
        warns += 1

if warns > 3:  # Allow existing patterns but flag excessive new ones
    print(f'FAIL: {warns} uses of panic!/unwrap in changed file')
    sys.exit(1)
else:
    print(f'PASS: Only {warns} panic!/unwrap uses (acceptable)')
    sys.exit(0)
PYEOF
)
    T6_STATUS=$?
    echo "$T6"
else
    echo "SKIP: Gated behind behavioral tests"
fi
if [ $T6_STATUS -eq 0 ]; then
    SCORE_CONFIG=$(python3 -c "print($SCORE_CONFIG + $W_CONFIG_NO_PANIC)")
fi

# -- Final score --
echo ""
echo "================================"
TOTAL=$(python3 -c "print(min($SCORE_BEHAV + $SCORE_STRUCT + $SCORE_CONFIG, 1.0))")
echo "Behavioral: $SCORE_BEHAV"
echo "Structural: $SCORE_STRUCT"
echo "Config:     $SCORE_CONFIG"
echo "Total:      $TOTAL"
echo "================================"

printf "%.4f" "$TOTAL" > "$REWARD_FILE"
python3 -c "import json; print(json.dumps({'reward': $TOTAL, 'behavioral': $SCORE_BEHAV, 'structural': $SCORE_STRUCT, 'config': $SCORE_CONFIG}))" > "$REWARD_JSON"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
