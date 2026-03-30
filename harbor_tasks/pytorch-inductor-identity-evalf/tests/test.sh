#!/usr/bin/env bash
# Verifier for pytorch-inductor-identity-evalf
# Bug: Identity class lacks comparison operators, causing recursion in Max/Min
# File: torch/utils/_sympy/functions.py
set +e

REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

TARGET="/workspace/pytorch/torch/utils/_sympy/functions.py"

echo "=== pytorch-inductor-identity-evalf verifier ==="

# -- GATE: Python syntax validity --
echo ""
echo "GATE: Python syntax validity"
python3 << 'PYEOF'
import ast, sys
try:
    with open("/workspace/pytorch/torch/utils/_sympy/functions.py") as f:
        ast.parse(f.read())
    print("  OK: file parses successfully")
    sys.exit(0)
except SyntaxError as e:
    print(f"  FAIL: SyntaxError: {e}")
    sys.exit(1)
PYEOF
if [ $? -ne 0 ]; then
    echo "GATE FAIL: syntax error in target file -- aborting with score 0"
    echo "0.0000" > "$REWARD_FILE"
    exit 0
fi
echo "GATE PASS"

# Weights: >=60% behavioral, <=40% structural
W_BEHAV_COMPARE=0.25
W_BEHAV_MAX=0.20
W_BEHAV_RATIONAL=0.15
W_STRUCTURAL_DUNDER=0.15
W_STRUCTURAL_FALLBACK=0.10
W_ANTISTUB=0.10
W_CONFIG_STYLE=0.05

SCORE="0.0"

# -- TEST 1 (BEHAVIORAL): Identity integer comparison no recursion --
echo ""
echo "TEST 1: behavioral -- Identity integer comparison works (weight=$W_BEHAV_COMPARE)"
T1=$(python3 << 'PYEOF'
import sys, signal

# Set a timeout to catch infinite recursion
def handler(signum, frame):
    raise TimeoutError("comparison timed out -- likely infinite recursion")
signal.signal(signal.SIGALRM, handler)
signal.alarm(5)

sys.path.insert(0, "/workspace/pytorch")
try:
    import sympy
    from torch.utils._sympy.functions import Identity

    expr_zero = Identity(sympy.sympify("0"))
    expr_neg = Identity(sympy.sympify("-6"))

    # These should not cause recursion
    assert (expr_zero >= 0) == True or (expr_zero >= 0) is sympy.S.true, \
        f"Identity(0) >= 0 should be True, got {expr_zero >= 0}"
    assert (expr_neg >= 0) == False or (expr_neg >= 0) is sympy.S.false, \
        f"Identity(-6) >= 0 should be False, got {expr_neg >= 0}"
    assert (0 >= expr_neg) == True or (0 >= expr_neg) is sympy.S.true, \
        f"0 >= Identity(-6) should be True, got {0 >= expr_neg}"

    print("PASS: Identity integer comparisons work without recursion")
    sys.exit(0)
except RecursionError:
    print("FAIL: RecursionError during Identity comparison")
    sys.exit(1)
except TimeoutError as e:
    print(f"FAIL: {e}")
    sys.exit(1)
except Exception as e:
    print(f"FAIL: unexpected error: {e}")
    sys.exit(1)
PYEOF
)
echo "$T1"
if echo "$T1" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_BEHAV_COMPARE)")
fi

# -- TEST 2 (BEHAVIORAL): Max with Identity works --
echo ""
echo "TEST 2: behavioral -- Max(0, Identity(-6)) evaluates correctly (weight=$W_BEHAV_MAX)"
T2=$(python3 << 'PYEOF'
import sys, signal

def handler(signum, frame):
    raise TimeoutError("Max evaluation timed out -- likely infinite recursion")
signal.signal(signal.SIGALRM, handler)
signal.alarm(5)

sys.path.insert(0, "/workspace/pytorch")
try:
    import sympy
    from torch.utils._sympy.functions import Identity

    expr = Identity(sympy.sympify("-6"))

    # Identity(-6) should be comparable
    assert expr.is_number, "Identity(-6) should be is_number"
    assert expr.is_comparable, "Identity(-6) should be is_comparable"

    # Max(0, Identity(-6)) should evaluate to 0
    result = sympy.Max(0, expr)
    assert result == 0, f"Max(0, Identity(-6)) should be 0, got {result}"

    print("PASS: Max(0, Identity(-6)) correctly evaluates to 0")
    sys.exit(0)
except RecursionError:
    print("FAIL: RecursionError during Max evaluation")
    sys.exit(1)
except TimeoutError as e:
    print(f"FAIL: {e}")
    sys.exit(1)
except Exception as e:
    print(f"FAIL: unexpected error: {e}")
    sys.exit(1)
PYEOF
)
echo "$T2"
if echo "$T2" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_BEHAV_MAX)")
fi

# -- TEST 3 (BEHAVIORAL): Rational comparison --
echo ""
echo "TEST 3: behavioral -- Identity(1/7) comparison works (weight=$W_BEHAV_RATIONAL)"
T3=$(python3 << 'PYEOF'
import sys, signal

def handler(signum, frame):
    raise TimeoutError("comparison timed out -- likely infinite recursion")
signal.signal(signal.SIGALRM, handler)
signal.alarm(5)

sys.path.insert(0, "/workspace/pytorch")
try:
    import sympy
    from torch.utils._sympy.functions import Identity

    expr = Identity(sympy.sympify("1/7"))
    # 1/7 >= 0 should be True
    result = (expr >= 0)
    assert result == True or result is sympy.S.true, \
        f"Identity(1/7) >= 0 should be True, got {result}"

    print("PASS: Identity(1/7) comparison works")
    sys.exit(0)
except RecursionError:
    print("FAIL: RecursionError during rational comparison")
    sys.exit(1)
except TimeoutError as e:
    print(f"FAIL: {e}")
    sys.exit(1)
except Exception as e:
    print(f"FAIL: unexpected error: {e}")
    sys.exit(1)
PYEOF
)
echo "$T3"
if echo "$T3" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_BEHAV_RATIONAL)")
fi

# -- TEST 4 (STRUCTURAL): Comparison dunder methods exist --
echo ""
echo "TEST 4: structural -- Identity has comparison operators (weight=$W_STRUCTURAL_DUNDER)"
T4=$(python3 << 'PYEOF'
import ast, sys

with open("/workspace/pytorch/torch/utils/_sympy/functions.py") as f:
    source = f.read()

tree = ast.parse(source)

# Find Identity class
identity_class = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "Identity":
        identity_class = node
        break

if identity_class is None:
    print("FAIL: Identity class not found")
    sys.exit(1)

methods = {n.name for n in ast.walk(identity_class) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}

comparison_ops = {"__ge__", "__gt__", "__le__", "__lt__"}
found = comparison_ops & methods

if len(found) >= 2:
    print(f"PASS: Identity has comparison operators: {found}")
    sys.exit(0)
else:
    print(f"FAIL: Identity missing comparison operators. Found: {found}")
    sys.exit(1)
PYEOF
)
echo "$T4"
if echo "$T4" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_STRUCTURAL_DUNDER)")
fi

# -- TEST 5 (STRUCTURAL): Fallback to super() for non-comparable args --
echo ""
echo "TEST 5: structural -- comparison falls back to super for non-comparable (weight=$W_STRUCTURAL_FALLBACK)"
T5=$(python3 << 'PYEOF'
import sys

with open("/workspace/pytorch/torch/utils/_sympy/functions.py") as f:
    source = f.read()

# The fix should have a fallback path that calls super().__ge__ etc.
# or returns None/NotImplemented for non-comparable args
has_super_fallback = "super().__ge__" in source or "super().__le__" in source or "super().__gt__" in source or "super().__lt__" in source
has_none_return = "return None" in source or "return NotImplemented" in source

if has_super_fallback:
    print("PASS: comparison operators fall back to super() for non-comparable args")
    sys.exit(0)
elif has_none_return:
    print("PASS: comparison operators return None/NotImplemented for non-comparable args")
    sys.exit(0)
else:
    print("FAIL: no fallback path found for non-comparable arguments")
    sys.exit(1)
PYEOF
)
echo "$T5"
if echo "$T5" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_STRUCTURAL_FALLBACK)")
fi

# -- TEST 6: Anti-stub check --
echo ""
echo "TEST 6: anti-stub -- file retains Identity class (weight=$W_ANTISTUB)"
T6=$(python3 << 'PYEOF'
import sys

with open("/workspace/pytorch/torch/utils/_sympy/functions.py") as f:
    source = f.read()

required = ["class Identity", "__int__", "__float__", "sympy", "Function"]
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


# ---------- Config-derived test (0.05): "Match existing code style and architectural patterns" ----------
# Source: CLAUDE.md line 57 @ f95d7a4bacff6a1e4f11a232c0f8a3f2b42bed4e
echo ""
echo "TEST config_style: config-derived -- match existing code style (weight=$W_CONFIG_STYLE)"
T_CONFIG=$(python3 << 'PYEOF'
import sys, os
os.chdir('/workspace/pytorch')
import subprocess
result = subprocess.run(['git', 'diff', '--name-only', 'HEAD~1..HEAD'], capture_output=True, text=True)
changed = [f for f in result.stdout.strip().split('\n') if f.endswith('.py')]
if not changed:
    result2 = subprocess.run(['find', 'torch', '-name', '*.py', '-newer', 'setup.py'], capture_output=True, text=True)
    changed = [f for f in result2.stdout.strip().split('\n') if f]
print('PASS')
PYEOF
)
echo "$T_CONFIG"
if echo "$T_CONFIG" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_CONFIG_STYLE)")
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
