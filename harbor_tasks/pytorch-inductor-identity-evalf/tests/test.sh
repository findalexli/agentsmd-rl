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
# Behavioral: 0.70 total
W_BEHAV_COMPARE_INT=0.20      # [pr_diff] Integer comparison no recursion
W_BEHAV_MAX_ZERO=0.20         # [pr_diff] Max(0, Identity(-6)) evaluates correctly
W_BEHAV_RATIONAL=0.15         # [pr_diff] Rational comparison works
W_BEHAV_REVERSE=0.10          # [pr_diff] Reverse comparison: 0 >= Identity(-6)
W_BEHAV_MIN=0.05              # [pr_diff] Min with Identity (same bug pattern)

# Structural: 0.30 total
W_STRUCTURAL_DUNDER=0.15      # [static] Comparison dunder methods exist with body
W_STRUCTURAL_FALLBACK=0.10    # [static] Fallback behavior for non-comparable args
W_ANTISTUB=0.05               # [static] File is not stubbed

SCORE="0.0"
BEHAVIORAL_PASSED=0

# -- TEST 1 (BEHAVIORAL): Identity integer comparison no recursion --
# [pr_diff] (0.20): Identity(0) >= 0 and Identity(-6) >= 0 work without RecursionError
echo ""
echo "TEST 1: behavioral -- Identity integer comparison works (weight=$W_BEHAV_COMPARE_INT)"
T1=$(python3 << 'PYEOF'
import sys, signal

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
    SCORE=$(python3 -c "print($SCORE + $W_BEHAV_COMPARE_INT)")
    BEHAVIORAL_PASSED=1
fi

# -- TEST 2 (BEHAVIORAL): Max(0, Identity) works --
# [pr_diff] (0.20): Max(0, Identity(-6)) evaluates to 0 without RecursionError
echo ""
echo "TEST 2: behavioral -- Max(0, Identity(-6)) evaluates correctly (weight=$W_BEHAV_MAX_ZERO)"
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
    SCORE=$(python3 -c "print($SCORE + $W_BEHAV_MAX_ZERO)")
    BEHAVIORAL_PASSED=1
else
    BEHAVIORAL_PASSED=0
fi

# -- TEST 3 (BEHAVIORAL): Rational comparison --
# [pr_diff] (0.15): Identity(1/7) >= 0 works without RecursionError
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

# -- TEST 4 (BEHAVIORAL): Reverse comparison --
# [pr_diff] (0.10): 0 >= Identity(-6) works (reverse comparison)
echo ""
echo "TEST 4: behavioral -- Reverse comparison 0 >= Identity(-6) works (weight=$W_BEHAV_REVERSE)"
T4=$(python3 << 'PYEOF'
import sys, signal

def handler(signum, frame):
    raise TimeoutError("comparison timed out -- likely infinite recursion")
signal.signal(signal.SIGALRM, handler)
signal.alarm(5)

sys.path.insert(0, "/workspace/pytorch")
try:
    import sympy
    from torch.utils._sympy.functions import Identity

    expr = Identity(sympy.sympify("-6"))

    # Reverse comparison: 0 >= Identity(-6) should be True
    result = (0 >= expr)
    assert result == True or result is sympy.S.true, \
        f"0 >= Identity(-6) should be True, got {result}"

    print("PASS: Reverse comparison 0 >= Identity(-6) works")
    sys.exit(0)
except RecursionError:
    print("FAIL: RecursionError during reverse comparison")
    sys.exit(1)
except TimeoutError as e:
    print(f"FAIL: {e}")
    sys.exit(1)
except Exception as e:
    print(f"FAIL: unexpected error: {e}")
    sys.exit(1)
PYEOF
)
echo "$T4"
if echo "$T4" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_BEHAV_REVERSE)")
fi

# -- TEST 5 (BEHAVIORAL): Min with Identity --
# [pr_diff] (0.05): Min(0, Identity(-6)) also works (same bug pattern)
echo ""
echo "TEST 5: behavioral -- Min(0, Identity(-6)) evaluates correctly (weight=$W_BEHAV_MIN)"
T5=$(python3 << 'PYEOF'
import sys, signal

def handler(signum, frame):
    raise TimeoutError("Min evaluation timed out -- likely infinite recursion")
signal.signal(signal.SIGALRM, handler)
signal.alarm(5)

sys.path.insert(0, "/workspace/pytorch")
try:
    import sympy
    from torch.utils._sympy.functions import Identity

    expr = Identity(sympy.sympify("-6"))

    # Min(0, Identity(-6)) should evaluate to -6
    result = sympy.Min(0, expr)
    assert result == -6, f"Min(0, Identity(-6)) should be -6, got {result}"

    print("PASS: Min(0, Identity(-6)) correctly evaluates to -6")
    sys.exit(0)
except RecursionError:
    print("FAIL: RecursionError during Min evaluation")
    sys.exit(1)
except TimeoutError as e:
    print(f"FAIL: {e}")
    sys.exit(1)
except Exception as e:
    print(f"FAIL: unexpected error: {e}")
    sys.exit(1)
PYEOF
)
echo "$T5"
if echo "$T5" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_BEHAV_MIN)")
fi

# -- TEST 6 (STRUCTURAL): Comparison dunder methods exist with non-trivial bodies --
# [static] (0.15): Check AST for meaningful implementation, not just stubs
echo ""
echo "TEST 6: structural -- Identity has comparison dunder methods (weight=$W_STRUCTURAL_DUNDER)"
T6=$(python3 << 'PYEOF'
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

# Find dunder methods
comparison_methods = {}
for node in ast.walk(identity_class):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        if node.name in {"__ge__", "__gt__", "__le__", "__lt__"}:
            comparison_methods[node.name] = node

if len(comparison_methods) < 2:
    print(f"FAIL: Need at least 2 comparison dunder methods, found {len(comparison_methods)}")
    sys.exit(1)

# Check that methods have non-trivial bodies (more than just pass/return)
all_are_stubs = True
for name, method in comparison_methods.items():
    body = method.body
    # Skip docstring
    if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, (ast.Str, ast.Constant)):
        body = body[1:]

    # Check if body has meaningful statements (>1 line OR contains non-trivial ops)
    if len(body) > 1:
        all_are_stubs = False
    elif len(body) == 1:
        stmt = body[0]
        if isinstance(stmt, ast.Return) and stmt.value is not None:
            # return with a value is somewhat meaningful
            all_are_stubs = False
        elif not isinstance(stmt, (ast.Pass, ast.Return)):
            all_are_stubs = False

if all_are_stubs:
    print("FAIL: comparison methods appear to be stubs (pass/return None only)")
    sys.exit(1)

print(f"PASS: Identity has {len(comparison_methods)} comparison operators with implementation")
sys.exit(0)
PYEOF
)
echo "$T6"
if echo "$T6" | grep -q "^PASS"; then
    if [ $BEHAVIORAL_PASSED -eq 1 ]; then
        SCORE=$(python3 -c "print($SCORE + $W_STRUCTURAL_DUNDER)")
    else
        echo "  (skipped: no behavioral pass yet)"
    fi
fi

# -- TEST 7 (STRUCTURAL): Fallback for non-comparable args --
# [static] (0.10): Methods should fallback to super() or similar for non-comparable
echo ""
echo "TEST 7: structural -- fallback for non-comparable args (weight=$W_STRUCTURAL_FALLBACK)"
T7=$(python3 << 'PYEOF'
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

# Check for super() call or NotImplemented return in comparison methods
has_fallback = False
for node in ast.walk(identity_class):
    if isinstance(node, ast.Call):
        # Check for super().__ge__ or super(Identity, self).__ge__ etc.
        if isinstance(node.func, ast.Attribute):
            if node.func.attr in {"__ge__", "__gt__", "__le__", "__lt__"}:
                if isinstance(node.func.value, ast.Call):
                    # super() or super(Identity, self)
                    func = node.func.value.func
                    if isinstance(func, ast.Name) and func.id == "super":
                        has_fallback = True
                        break
    elif isinstance(node, ast.Return):
        # Check for return NotImplemented
        if isinstance(node.value, ast.Name) and node.value.id == "NotImplemented":
            has_fallback = True
            break

if not has_fallback:
    # Alternative: check that methods don't just return a simple constant
    # Look for branching logic (if statement)
    has_branching = False
    for node in ast.walk(identity_class):
        if isinstance(node, ast.If):
            has_branching = True
            break

    if has_branching:
        print("PASS: comparison methods have branching logic (likely handles fallback)")
        sys.exit(0)
    else:
        print("WARN: no explicit fallback found")
        # Still give partial credit if behavioral tests pass
        sys.exit(0)

print("PASS: comparison methods have fallback to super() or return NotImplemented")
sys.exit(0)
PYEOF
)
echo "$T7"
if echo "$T7" | grep -q "^PASS"; then
    if [ $BEHAVIORAL_PASSED -eq 1 ]; then
        SCORE=$(python3 -c "print($SCORE + $W_STRUCTURAL_FALLBACK)")
    else
        echo "  (skipped: no behavioral pass yet)"
    fi
fi

# -- TEST 8: Anti-stub check --
# [static] (0.05): Ensure file retains original Identity class structure
echo ""
echo "TEST 8: anti-stub -- file retains Identity class (weight=$W_ANTISTUB)"
T8=$(python3 << 'PYEOF'
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

# Check for __int__ and __float__ methods
required_methods = {"__int__", "__float__"}
found_methods = set()
for node in ast.walk(identity_class):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        if node.name in required_methods:
            found_methods.add(node.name)

if len(found_methods) < 2:
    print(f"FAIL: missing methods: {required_methods - found_methods}")
    sys.exit(1)

# Check minimum class length
class_lines = identity_class.end_lineno - identity_class.lineno
if class_lines < 10:
    print(f"FAIL: Identity class has only {class_lines} lines")
    sys.exit(1)

print(f"PASS: file has Identity class with {class_lines} lines and required methods")
sys.exit(0)
PYEOF
)
echo "$T8"
if echo "$T8" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_ANTISTUB)")
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
