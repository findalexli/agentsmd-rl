#!/usr/bin/env bash
set +e

SCORE=0
TOTAL=0
PASS=0
FAIL=0
REWARD_DIR="/logs/verifier"
mkdir -p "$REWARD_DIR" 2>/dev/null || true

log_check() {
    local weight="$1" origin="$2" desc="$3" result="$4"
    TOTAL=$((TOTAL + 1))
    if [ "$result" = "PASS" ]; then
        SCORE=$(python3 -c "print(round($SCORE + $weight, 4))")
        PASS=$((PASS + 1))
        echo "  PASS [$origin] ($weight): $desc"
    else
        FAIL=$((FAIL + 1))
        echo "  FAIL [$origin] ($weight): $desc"
    fi
}

echo "=== Gate: syntax check ==="
# [static] (0.00): Modified files must parse without syntax errors
GATE_OK=true
for f in gradio/external.py gradio/external_utils.py; do
    if [ -f "$f" ]; then
        python3 -c "import ast; ast.parse(open('$f').read())" 2>/dev/null
        if [ $? -ne 0 ]; then
            echo "  GATE FAIL: $f has syntax errors"
            GATE_OK=false
        fi
    fi
done

if [ "$GATE_OK" = "false" ]; then
    echo "0.0" > "$REWARD_DIR/reward.txt"
    echo '{"reward": 0.0, "gate": "syntax_fail"}' > "$REWARD_DIR/reward.json"
    echo "0.0"
    exit 0
fi
echo "  Gate passed."

echo ""
echo "=== Behavioral: fail-to-pass tests ==="

# [pr_diff] (0.35): Closure in from_model must not recurse due to variable shadowing
# Uses AST to detect if any free variable captured by the inner closure is
# reassigned after its definition (the root cause of the recursion bug).
# Handles ALL valid fix patterns: rename, bare pop, removal, default-param capture.
RESULT=$(python3 -c "
import ast, sys
sys.setrecursionlimit(80)

with open('gradio/external.py') as f:
    source = f.read()

tree = ast.parse(source)

# Find from_model function
fm = None
for node in ast.iter_child_nodes(tree):
    if isinstance(node, ast.FunctionDef) and node.name == 'from_model':
        fm = node
        break

if fm is None:
    print('FAIL')
    sys.exit(0)

# Find the first inner function (the closure that wraps the pipeline call)
inner_fn = None
for child in ast.iter_child_nodes(fm):
    if isinstance(child, ast.FunctionDef):
        inner_fn = child
        break

if inner_fn is None:
    print('FAIL')
    sys.exit(0)

# Collect names loaded (read) inside the inner function body
inner_reads = set()
for node in ast.walk(inner_fn):
    if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
        inner_reads.add(node.id)

# Collect names that are parameters (not free variables)
param_names = set()
for arg in inner_fn.args.args + inner_fn.args.kwonlyargs:
    param_names.add(arg.arg)
if inner_fn.args.vararg:
    param_names.add(inner_fn.args.vararg.arg)
if inner_fn.args.kwarg:
    param_names.add(inner_fn.args.kwarg.arg)

# Names captured via default args (bound at definition time, immune to shadowing)
default_captures = set()
for d in inner_fn.args.defaults + inner_fn.args.kw_defaults:
    if d and isinstance(d, ast.Name):
        default_captures.add(d.id)

free_vars = inner_reads - param_names

# Find names assigned (stored) AFTER the inner function definition within from_model
reassigned_after = set()
for child in ast.iter_child_nodes(fm):
    if hasattr(child, 'lineno') and child.lineno > inner_fn.end_lineno:
        for node in ast.walk(child):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                reassigned_after.add(node.id)

# The bug: a free variable used by the closure is reassigned after its definition,
# unless it was captured via a default parameter value
shadowed = free_vars & reassigned_after - default_captures

if shadowed:
    print('FAIL')
else:
    print('PASS')
" 2>&1)
log_check 0.35 "pr_diff" "Closure free variables not shadowed after definition" "$RESULT"

# [pr_diff] (0.10): The interface function must actually work without recursion (runtime sim)
# Complements the AST check above: actually executes a closure simulation to verify
# no RecursionError occurs at runtime.
RESULT=$(python3 -c "
import ast, sys
sys.setrecursionlimit(80)

with open('gradio/external.py') as f:
    source = f.read()

tree = ast.parse(source)

# Find what variable (if any) receives kwargs.pop('fn', ...)
fm = None
for node in ast.iter_child_nodes(tree):
    if isinstance(node, ast.FunctionDef) and node.name == 'from_model':
        fm = node
        break

if fm is None:
    print('FAIL')
    sys.exit(0)

pop_var = None
has_bare_pop = False
for child in ast.walk(fm):
    if isinstance(child, ast.Assign) and isinstance(child.value, ast.Call):
        func = child.value.func
        if (isinstance(func, ast.Attribute) and func.attr == 'pop'
            and child.value.args
            and isinstance(child.value.args[0], ast.Constant)
            and child.value.args[0].value == 'fn'):
            if child.targets and isinstance(child.targets[0], ast.Name):
                pop_var = child.targets[0].id
    elif isinstance(child, ast.Expr) and isinstance(child.value, ast.Call):
        func = child.value.func
        if (isinstance(func, ast.Attribute) and func.attr == 'pop'
            and child.value.args
            and isinstance(child.value.args[0], ast.Constant)
            and child.value.args[0].value == 'fn'):
            has_bare_pop = True

# Simulate closure behavior
original = lambda *data: 'pipeline_ok'

if pop_var == 'fn':
    # Bug: fn shadows closure var
    ns = {}
    exec('''
fn = original
def query(*data):
    return fn(*data)
kwargs = {\"fn\": query}
fn = kwargs.pop(\"fn\", None)
try:
    query(\"test\")
    _r = \"FAIL\"
except RecursionError:
    _r = \"FAIL\"
''', {'original': original}, ns)
    print(ns.get('_r', 'FAIL'))

elif pop_var is not None:
    # Renamed var — simulate to confirm no recursion
    ns = {}
    exec('''
fn = original
def query(*data):
    return fn(*data)
kwargs = {{\"fn\": query}}
{v} = kwargs.pop(\"fn\", None)
try:
    result = query(\"test\")
    _r = \"PASS\" if result == \"pipeline_ok\" else \"FAIL\"
except RecursionError:
    _r = \"FAIL\"
'''.format(v=pop_var), {'original': original}, ns)
    print(ns.get('_r', 'FAIL'))

elif has_bare_pop or pop_var is None:
    # No assignment or bare pop — fn never shadowed
    ns = {}
    exec('''
fn = original
def query(*data):
    return fn(*data)
try:
    result = query(\"test\")
    _r = \"PASS\" if result == \"pipeline_ok\" else \"FAIL\"
except RecursionError:
    _r = \"FAIL\"
''', {'original': original}, ns)
    print(ns.get('_r', 'FAIL'))
else:
    print('FAIL')
" 2>&1)
log_check 0.10 "pr_diff" "Runtime closure simulation does not recurse" "$RESULT"

# [pr_diff] (0.15): handle_hf_error must catch StopIteration and raise informative Error
RESULT=$(python3 -c "
import sys
sys.path.insert(0, '.')
from gradio.external_utils import handle_hf_error
from gradio.exceptions import Error

try:
    handle_hf_error(StopIteration())
    print('FAIL')  # Should have raised
except Error as e:
    msg = str(e).lower()
    # Any informative message about unsupported model is acceptable
    if len(msg.strip()) > 10:
        print('PASS')
    else:
        print('FAIL')
except StopIteration:
    print('FAIL')  # StopIteration leaked through unhandled
except Exception:
    print('FAIL')
" 2>&1)
log_check 0.15 "pr_diff" "StopIteration handled in handle_hf_error" "$RESULT"

# [pr_diff] (0.10): handle_hf_error must not produce empty error messages
RESULT=$(python3 -c "
import sys
sys.path.insert(0, '.')
from gradio.external_utils import handle_hf_error
from gradio.exceptions import Error

try:
    handle_hf_error(Exception())  # Exception with no message
    print('FAIL')
except Error as e:
    msg = str(e).strip()
    if len(msg) > 0:
        print('PASS')
    else:
        print('FAIL')
except Exception:
    print('FAIL')
" 2>&1)
log_check 0.10 "pr_diff" "Empty exception gets a non-empty error message" "$RESULT"

echo ""
echo "=== Pass-to-pass: regression checks ==="

# [repo_tests] (0.10): gradio.external and gradio.external_utils must remain importable
RESULT=$(python3 -c "
import sys
sys.path.insert(0, '.')
try:
    import gradio.external
    import gradio.external_utils
    print('PASS')
except Exception:
    print('FAIL')
" 2>&1)
log_check 0.10 "repo_tests" "gradio.external and gradio.external_utils importable" "$RESULT"

# [repo_tests] (0.05): handle_hf_error still raises on standard HTTP errors (401)
RESULT=$(python3 -c "
import sys
sys.path.insert(0, '.')
from gradio.external_utils import handle_hf_error
from gradio.exceptions import Error

try:
    handle_hf_error(Exception('401 Unauthorized'))
    print('FAIL')
except Error as e:
    msg = str(e).lower()
    if 'unauthorized' in msg or '401' in msg or 'signed in' in msg:
        print('PASS')
    else:
        print('FAIL')
except Exception:
    print('FAIL')
" 2>&1)
log_check 0.05 "repo_tests" "handle_hf_error still raises on 401 errors" "$RESULT"

echo ""
echo "=== Structural: anti-stub ==="

# [static] (0.05): handle_hf_error must have real branching logic (anti-stub)
RESULT=$(python3 -c "
import ast

with open('gradio/external_utils.py') as f:
    tree = ast.parse(f.read())

for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == 'handle_hf_error':
        # Count meaningful statements (exclude pass, docstrings)
        stmts = []
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.Raise, ast.Return, ast.Assign)):
                stmts.append(child)
        if len(stmts) >= 4:
            print('PASS')
        else:
            print('FAIL')
        break
else:
    print('FAIL')
" 2>&1)
log_check 0.05 "static" "handle_hf_error has real branching logic, not a stub" "$RESULT"

echo ""
echo "=== Config-derived checks ==="

# [agent_config] (0.10): "Python code is formatted with ruff" — AGENTS.md:43 @ ca84f3e
RESULT="PASS"
for f in gradio/external.py gradio/external_utils.py; do
    if [ -f "$f" ]; then
        ruff check --select E,W "$f" --quiet 2>/dev/null
        if [ $? -ne 0 ]; then
            RESULT="FAIL"
            break
        fi
    fi
done
log_check 0.10 "agent_config" "ruff lint passes on modified files — AGENTS.md:43" "$RESULT"

echo ""
echo "=== Summary ==="
echo "  Checks: $TOTAL | Passed: $PASS | Failed: $FAIL"
echo "  Score: $SCORE / 1.00"

echo "$SCORE" > "$REWARD_DIR/reward.txt"
python3 -c "
import json
reward = float('$SCORE')
data = {
    'reward': reward,
    'behavioral': min(reward, 0.70),
    'regression': min(max(reward - 0.70, 0), 0.15),
    'structural': min(max(reward - 0.85, 0), 0.05),
    'config': min(max(reward - 0.90, 0), 0.10)
}
print(json.dumps(data))
" > "$REWARD_DIR/reward.json" 2>/dev/null || true

echo "$SCORE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
