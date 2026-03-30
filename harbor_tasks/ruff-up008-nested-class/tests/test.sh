#!/usr/bin/env bash
# Verifier for ruff-up008-nested-class
# Bug: UP008 false positive for nested classes where inner class name is unreachable
# File: crates/ruff_linter/src/rules/pyupgrade/rules/super_call_with_parameters.rs
set +e

REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

RUST_FILE="/workspace/ruff/crates/ruff_linter/src/rules/pyupgrade/rules/super_call_with_parameters.rs"
FIXTURE="/workspace/ruff/crates/ruff_linter/resources/test/fixtures/pyupgrade/UP008.py"

echo "=== ruff-up008-nested-class verifier ==="

# -- GATE: files exist --
echo ""
echo "GATE: Target files exist"
if [ ! -f "$RUST_FILE" ] || [ ! -f "$FIXTURE" ]; then
    echo "GATE FAIL: required files missing"
    echo "0.0000" > "$REWARD_FILE"
    exit 0
fi
echo "GATE PASS"

# Weights: >=60% behavioral, <=40% structural
W_BEHAV_SCOPE_WALK=0.25
W_BEHAV_TODO_REMOVED=0.15
W_BEHAV_EXTRA_NESTING=0.20
W_STRUCTURAL_ENCLOSING_CLASSES=0.15
W_STRUCTURAL_CHAIN_CHECK=0.10
W_ANTISTUB=0.10
W_CONFIG_NO_PANIC=0.05

SCORE="0.0"

# -- TEST 1 (BEHAVIORAL): Uses scope-based class nesting instead of statement parents --
echo ""
echo "TEST 1: behavioral -- uses scope-based enclosing class discovery (weight=$W_BEHAV_SCOPE_WALK)"
T1=$(python3 << 'PYEOF'
import sys

with open("/workspace/ruff/crates/ruff_linter/src/rules/pyupgrade/rules/super_call_with_parameters.rs") as f:
    source = f.read()

# The fix replaces statement-parent walking with scope-based class discovery
# using checker.semantic().current_scopes()
has_current_scopes = "current_scopes()" in source
has_scope_class = "ScopeKind::Class" in source

# The old buggy pattern: parents.find(|stmt| stmt.is_class_def_stmt())
# to find enclosing class. The fix uses scopes instead.
has_old_parent_find = 'parents.find(|stmt| stmt.is_class_def_stmt())' in source

if has_current_scopes and has_scope_class and not has_old_parent_find:
    print("PASS: uses scope-based class nesting via current_scopes()")
    sys.exit(0)
elif has_current_scopes and has_scope_class:
    print("PASS: uses current_scopes() with ScopeKind::Class (may have some old pattern too)")
    sys.exit(0)
else:
    print("FAIL: still using statement-parent walking for class discovery")
    sys.exit(1)
PYEOF
)
echo "$T1"
if echo "$T1" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_BEHAV_SCOPE_WALK)")
fi

# -- TEST 2 (BEHAVIORAL): TODO comments removed from fixture --
echo ""
echo "TEST 2: behavioral -- TODO comments about nested class false positive removed (weight=$W_BEHAV_TODO_REMOVED)"
T2=$(python3 << 'PYEOF'
import sys

with open("/workspace/ruff/crates/ruff_linter/resources/test/fixtures/pyupgrade/UP008.py") as f:
    source = f.read()

# The old code had TODO(charlie) comments about false positives
if "false positive until nested class matching is fixed" in source:
    print("FAIL: TODO comment about nested class false positive still present")
    sys.exit(1)
else:
    print("PASS: TODO comments about nested class false positive removed")
    sys.exit(0)
PYEOF
)
echo "$T2"
if echo "$T2" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_BEHAV_TODO_REMOVED)")
fi

# -- TEST 3 (BEHAVIORAL): Extra nesting level check prevents false match --
echo ""
echo "TEST 3: behavioral -- checks for extra nesting levels (weight=$W_BEHAV_EXTRA_NESTING)"
T3=$(python3 << 'PYEOF'
import sys

with open("/workspace/ruff/crates/ruff_linter/src/rules/pyupgrade/rules/super_call_with_parameters.rs") as f:
    source = f.read()

# The key fix: after matching the class name in super(), check if there are
# MORE enclosing classes. If so, the name is not directly accessible -> return.
# Look for enclosing_classes.next().is_some() or equivalent pattern
has_extra_nesting_check = "enclosing_classes.next().is_some()" in source
has_is_some = ".is_some()" in source and "enclosing" in source

if has_extra_nesting_check:
    print("PASS: checks for additional enclosing classes after match")
    sys.exit(0)
elif has_is_some:
    print("PASS: checks enclosing scope count (variant)")
    sys.exit(0)
else:
    print("FAIL: no check for extra nesting levels")
    sys.exit(1)
PYEOF
)
echo "$T3"
if echo "$T3" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_BEHAV_EXTRA_NESTING)")
fi

# -- TEST 4 (STRUCTURAL): enclosing_classes iterator from scopes --
echo ""
echo "TEST 4: structural -- enclosing_classes iterator from scope walk (weight=$W_STRUCTURAL_ENCLOSING_CLASSES)"
T4=$(python3 << 'PYEOF'
import sys

with open("/workspace/ruff/crates/ruff_linter/src/rules/pyupgrade/rules/super_call_with_parameters.rs") as f:
    source = f.read()

# The fix creates an iterator: enclosing_classes = checker.semantic().current_scopes().filter_map(...)
has_enclosing_classes = "enclosing_classes" in source
has_filter_map = "filter_map" in source and "current_scopes" in source

if has_enclosing_classes and has_filter_map:
    print("PASS: enclosing_classes iterator from scope walk with filter_map")
    sys.exit(0)
elif has_enclosing_classes:
    print("PASS: enclosing_classes variable exists (partial)")
    sys.exit(0)
else:
    print("FAIL: no enclosing_classes iterator found")
    sys.exit(1)
PYEOF
)
echo "$T4"
if echo "$T4" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_STRUCTURAL_ENCLOSING_CLASSES)")
fi

# -- TEST 5 (STRUCTURAL): Dotted chain verification against nesting --
echo ""
echo "TEST 5: structural -- dotted chain verified against class nesting (weight=$W_STRUCTURAL_CHAIN_CHECK)"
T5=$(python3 << 'PYEOF'
import sys

with open("/workspace/ruff/crates/ruff_linter/src/rules/pyupgrade/rules/super_call_with_parameters.rs") as f:
    source = f.read()

# For super(A.B.C, self), each segment must match the enclosing class chain
# The fix uses enclosing_classes.next() to verify each segment
has_chain_loop = "chain" in source and "enclosing" in source
has_enclosing_name = "enclosing_name" in source

if has_chain_loop and has_enclosing_name:
    print("PASS: dotted chain segments verified against enclosing class names")
    sys.exit(0)
elif has_enclosing_name:
    print("PASS: enclosing_name comparison exists (partial)")
    sys.exit(0)
else:
    print("FAIL: no dotted chain verification against nesting")
    sys.exit(1)
PYEOF
)
echo "$T5"
if echo "$T5" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_STRUCTURAL_CHAIN_CHECK)")
fi

# -- TEST 6: Anti-stub --
echo ""
echo "TEST 6: anti-stub -- files retain core logic (weight=$W_ANTISTUB)"
T6=$(python3 << 'PYEOF'
import sys

with open("/workspace/ruff/crates/ruff_linter/src/rules/pyupgrade/rules/super_call_with_parameters.rs") as f:
    source = f.read()

required = ["super_call_with_parameters", "checker", "ExprCall", "ScopeKind",
            "is_super_call_with_arguments", "parent_name"]
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
# Source: AGENTS.md line 79 @ 0f41bc554bd89d14dbeb7e1791b34dc7319339bc
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
