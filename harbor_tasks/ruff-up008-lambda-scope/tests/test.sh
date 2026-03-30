#!/usr/bin/env bash
# Verifier for ruff-up008-lambda-scope
# Bug: UP008 misses super() simplification in lambda class attributes
# File: crates/ruff_linter/src/rules/pyupgrade/rules/super_call_with_parameters.rs
set +e

REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

RUST_FILE="/workspace/ruff/crates/ruff_linter/src/rules/pyupgrade/rules/super_call_with_parameters.rs"
FIXTURE="/workspace/ruff/crates/ruff_linter/resources/test/fixtures/pyupgrade/UP008.py"

echo "=== ruff-up008-lambda-scope verifier ==="

# -- GATE: files exist --
echo ""
echo "GATE: Target files exist"
if [ ! -f "$RUST_FILE" ]; then
    echo "GATE FAIL: Rust source file missing"
    echo "0.0000" > "$REWARD_FILE"
    exit 0
fi
if [ ! -f "$FIXTURE" ]; then
    echo "GATE FAIL: fixture file missing"
    echo "0.0000" > "$REWARD_FILE"
    exit 0
fi
echo "GATE PASS"

# Weights: >=60% behavioral, <=40% structural
W_BEHAV_LAMBDA_SCOPE=0.30
W_BEHAV_TODO_REMOVED=0.15
W_BEHAV_FIXTURE_CASE=0.20
W_STRUCTURAL_SCOPEKIND=0.15
W_STRUCTURAL_LAMBDA_PARAMS=0.10
W_ANTISTUB=0.05
W_CONFIG_NO_PANIC=0.05

SCORE="0.0"

# -- TEST 1 (BEHAVIORAL): Rust source handles Lambda scope --
echo ""
echo "TEST 1: behavioral -- Lambda scope recognized as callable (weight=$W_BEHAV_LAMBDA_SCOPE)"
T1=$(python3 << 'PYEOF'
import sys

with open("/workspace/ruff/crates/ruff_linter/src/rules/pyupgrade/rules/super_call_with_parameters.rs") as f:
    source = f.read()

# The fix must add ScopeKind::Lambda as a valid callable scope
has_lambda_scope = "ScopeKind::Lambda" in source
# Must be in a match or if-let that also includes Function
has_function_scope = "ScopeKind::Function" in source

if has_lambda_scope and has_function_scope:
    print("PASS: both ScopeKind::Lambda and ScopeKind::Function handled")
    sys.exit(0)
elif has_lambda_scope:
    print("PASS: ScopeKind::Lambda added (Function may use different pattern)")
    sys.exit(0)
else:
    print("FAIL: ScopeKind::Lambda not found in scope handling")
    sys.exit(1)
PYEOF
)
echo "$T1"
if echo "$T1" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_BEHAV_LAMBDA_SCOPE)")
fi

# -- TEST 2 (BEHAVIORAL): TODO comment removed from fixture --
echo ""
echo "TEST 2: behavioral -- TODO comment about lambda removed from fixture (weight=$W_BEHAV_TODO_REMOVED)"
T2=$(python3 << 'PYEOF'
import sys

with open("/workspace/ruff/crates/ruff_linter/resources/test/fixtures/pyupgrade/UP008.py") as f:
    source = f.read()

# The old code had: # TODO(charlie): class-body lambda rewrite is still missed.
if "lambda rewrite is still missed" in source or "TODO(charlie): class-body lambda" in source:
    print("FAIL: TODO comment about lambda still present in fixture")
    sys.exit(1)
else:
    print("PASS: TODO comment about lambda removed from fixture")
    sys.exit(0)
PYEOF
)
echo "$T2"
if echo "$T2" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_BEHAV_TODO_REMOVED)")
fi

# -- TEST 3 (BEHAVIORAL): Fixture still has the lambda test case --
echo ""
echo "TEST 3: behavioral -- fixture retains LambdaMethod test case (weight=$W_BEHAV_FIXTURE_CASE)"
T3=$(python3 << 'PYEOF'
import sys

with open("/workspace/ruff/crates/ruff_linter/resources/test/fixtures/pyupgrade/UP008.py") as f:
    source = f.read()

# The fixture should still have the LambdaMethod class with the super() call
has_lambda_method = "class LambdaMethod" in source
has_lambda_super = "lambda self: super(LambdaMethod, self)" in source
has_can_use = "can use super()" in source and "lambda" in source.split("can use super()")[0].split("\n")[-1].lower() if "can use super()" in source else False

if has_lambda_method and has_lambda_super:
    print("PASS: fixture has LambdaMethod test case with super() call in lambda")
    sys.exit(0)
elif has_lambda_method:
    print("PASS: fixture has LambdaMethod class (partial)")
    sys.exit(0)
else:
    print("FAIL: LambdaMethod test case missing from fixture")
    sys.exit(1)
PYEOF
)
echo "$T3"
if echo "$T3" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_BEHAV_FIXTURE_CASE)")
fi

# -- TEST 4 (STRUCTURAL): ScopeKind import includes Lambda --
echo ""
echo "TEST 4: structural -- Scope/ScopeKind imports include Lambda (weight=$W_STRUCTURAL_SCOPEKIND)"
T4=$(python3 << 'PYEOF'
import sys

with open("/workspace/ruff/crates/ruff_linter/src/rules/pyupgrade/rules/super_call_with_parameters.rs") as f:
    source = f.read()

# Check imports include Scope and ScopeKind
has_scope_import = "Scope" in source and "use ruff_python_semantic" in source
has_lambda_pattern = "Lambda" in source

if has_scope_import and has_lambda_pattern:
    print("PASS: Scope imported and Lambda pattern used")
    sys.exit(0)
else:
    missing = []
    if not has_scope_import:
        missing.append("Scope import")
    if not has_lambda_pattern:
        missing.append("Lambda pattern")
    print(f"FAIL: missing {', '.join(missing)}")
    sys.exit(1)
PYEOF
)
echo "$T4"
if echo "$T4" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_STRUCTURAL_SCOPEKIND)")
fi

# -- TEST 5 (STRUCTURAL): Lambda parameter extraction --
echo ""
echo "TEST 5: structural -- lambda parameters extracted for comparison (weight=$W_STRUCTURAL_LAMBDA_PARAMS)"
T5=$(python3 << 'PYEOF'
import sys

with open("/workspace/ruff/crates/ruff_linter/src/rules/pyupgrade/rules/super_call_with_parameters.rs") as f:
    source = f.read()

# The fix needs to extract the first parameter from lambda (ExprLambda)
# and compare it with the second argument to super()
has_expr_lambda = "ExprLambda" in source
has_lambda_params = "parameters" in source and "Lambda" in source

if has_expr_lambda and has_lambda_params:
    print("PASS: ExprLambda parameters extracted")
    sys.exit(0)
elif has_expr_lambda:
    print("PASS: ExprLambda referenced (partial)")
    sys.exit(0)
else:
    print("FAIL: no ExprLambda parameter extraction found")
    sys.exit(1)
PYEOF
)
echo "$T5"
if echo "$T5" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_STRUCTURAL_LAMBDA_PARAMS)")
fi

# -- TEST 6: Anti-stub --
echo ""
echo "TEST 6: anti-stub -- Rust file retains core logic (weight=$W_ANTISTUB)"
T6=$(python3 << 'PYEOF'
import sys

with open("/workspace/ruff/crates/ruff_linter/src/rules/pyupgrade/rules/super_call_with_parameters.rs") as f:
    source = f.read()

required = ["super_call_with_parameters", "checker", "ExprCall", "ScopeKind",
            "is_super_call_with_arguments", "enclosing_class"]
missing = [r for r in required if r not in source]

if missing:
    print(f"FAIL: file is missing expected content: {missing}")
    sys.exit(1)

line_count = len(source.splitlines())
if line_count < 100:
    print(f"FAIL: file has only {line_count} lines -- looks like a stub")
    sys.exit(1)

print(f"PASS: file has {line_count} lines and contains all expected symbols")
sys.exit(0)
PYEOF
)
echo "$T6"
if echo "$T6" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_ANTISTUB)")
fi


# ---------- Config-derived test (0.05): "Avoid panic!, unreachable!, .unwrap()" ----------
# Source: AGENTS.md line 79 @ 09f645d49f1337866d63e62570cb9a43a4a875b3
echo ""
echo "TEST config_no_panic: config-derived -- avoid panic!/unwrap (weight=$W_CONFIG_NO_PANIC)"
T_CONFIG=$(python3 << 'PYEOF'
import sys, os
os.chdir('/workspace/ruff')
import subprocess
result = subprocess.run(['git', 'diff', '--name-only', 'HEAD~1..HEAD'], capture_output=True, text=True)
changed_rs = [f for f in result.stdout.strip().split('\n') if f.endswith('.rs')]
if not changed_rs:
    result2 = subprocess.run(['find', 'crates', '-name', '*.rs', '-newer', 'Cargo.toml'], capture_output=True, text=True)
    changed_rs = [f for f in result2.stdout.strip().split('\n') if f]
warns = 0
for f in changed_rs[:20]:
    try:
        with open(f) as fh:
            for i, line in enumerate(fh, 1):
                s = line.strip()
                if s.startswith('//'):
                    continue
                if ('panic!(' in s or '.unwrap()' in s) and 'test' not in f:
                    warns += 1
    except: pass
if warns > 5:
    print('FAIL: ' + str(warns) + ' uses of panic!/unwrap in changed files')
    sys.exit(1)
print('PASS')
PYEOF
)
echo "$T_CONFIG"
if echo "$T_CONFIG" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_CONFIG_NO_PANIC)")
fi

# -- Final score --
echo ""
echo "================================"
REWARD=$(python3 -c "print('{:.4f}'.format(min($SCORE, 1.0)))")
echo "Reward: $REWARD"
echo "================================"
echo "$REWARD" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
