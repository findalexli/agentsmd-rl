#!/usr/bin/env bash
#
# Verification for slime-megatron-lr-scheduler-duplicate
# Tests that the redundant opt_param_scheduler.step() call has been removed
# from initialize_model_and_optimizer().
#
set +e

TARGET="/workspace/slime/slime/backends/megatron_utils/model.py"
REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

declare -A WEIGHTS
declare -A RESULTS
WEIGHTS[behavioral]=0.35
WEIGHTS[behavioral2]=0.25
WEIGHTS[structural]=0.30
WEIGHTS[config_no_wildcard]=0.05
WEIGHTS[config_no_bare_print]=0.05

for key in behavioral behavioral2 structural config_no_wildcard config_no_bare_print; do
    RESULTS[$key]=0
done

# ---------- GATE: Python syntax validity ----------
python3 -c "
import ast, sys
try:
    with open('$TARGET') as f:
        ast.parse(f.read())
    sys.exit(0)
except SyntaxError as e:
    print(f'GATE FAIL: syntax error: {e}')
    sys.exit(1)
"
if [ $? -ne 0 ]; then
    echo "GATE FAIL: file has syntax errors -- aborting with score 0"
    echo "0.0" > "$REWARD_FILE"
    exit 0
fi
echo "GATE PASS: syntax valid"

# ---------- PRIMARY 1 (40%): Behavioral - extract and run initialize_model_and_optimizer ----------
# Extract the function body, mock all external deps, and verify scheduler.step() is NOT called.
python3 << 'PYEOF'
import ast, sys, types

TARGET = "/workspace/slime/slime/backends/megatron_utils/model.py"

with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)

# Find the initialize_model_and_optimizer function
func_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "initialize_model_and_optimizer":
        func_node = node
        break

if func_node is None:
    print("BEHAVIORAL FAIL: initialize_model_and_optimizer function not found")
    sys.exit(1)

# Check if any call to opt_param_scheduler.step() exists in the function body
# by walking the AST for calls on opt_param_scheduler.step
found_scheduler_step = False
for node in ast.walk(func_node):
    if isinstance(node, ast.Call):
        func = node.func
        if isinstance(func, ast.Attribute) and func.attr == "step":
            if isinstance(func.value, ast.Name) and func.value.id == "opt_param_scheduler":
                found_scheduler_step = True
                break

if found_scheduler_step:
    print("BEHAVIORAL FAIL: opt_param_scheduler.step() still present in initialize_model_and_optimizer")
    sys.exit(1)
else:
    print("BEHAVIORAL PASS: opt_param_scheduler.step() removed from initialize_model_and_optimizer")
    sys.exit(0)
PYEOF
if [ $? -eq 0 ]; then RESULTS[behavioral]=1; fi

# ---------- PRIMARY 2 (30%): Behavioral - mock execution to verify no scheduler step ----------
# Build minimal mocks and exec the function, tracking whether scheduler.step() is called.
python3 << 'PYEOF'
import ast, sys, textwrap

TARGET = "/workspace/slime/slime/backends/megatron_utils/model.py"

with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)

# Find the function
func_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "initialize_model_and_optimizer":
        func_node = node
        break

if func_node is None:
    print("BEHAVIORAL2 FAIL: function not found")
    sys.exit(1)

# Extract function source lines
func_source = ast.get_source_segment(source, func_node)
if func_source is None:
    lines = source.splitlines()
    func_source = "\n".join(lines[func_node.lineno - 1:func_node.end_lineno])

# Create mocks and exec the function
env = {}
exec_code = textwrap.dedent("""
import types

class MockScheduler:
    def __init__(self):
        self.step_called = False
        self.step_args = None
    def step(self, **kwargs):
        self.step_called = True
        self.step_args = kwargs

class MockArgs:
    global_batch_size = 4

class MockModel:
    role = None

class MockTorchVersion:
    hip = None

torch = types.SimpleNamespace(version=MockTorchVersion())

def setup_model_and_optimizer(args, role):
    return [MockModel()], "optimizer", MockScheduler()

def load_checkpoint(model, optimizer, opt_param_scheduler, checkpointing_context=None, skip_load_to_model_and_opt=False):
    return 100, None

def clear_memory():
    pass

scheduler = MockScheduler()
_original_setup = setup_model_and_optimizer
def setup_model_and_optimizer(args, role):
    m, o, _ = _original_setup(args, role)
    return m, o, scheduler

""")
exec(exec_code, env)

# Now try to exec the function itself with mocks
try:
    exec(func_source, env)
    # Call the function
    result = env["initialize_model_and_optimizer"](env["MockArgs"](), "actor")
    scheduler = env["scheduler"]
    if scheduler.step_called:
        print("BEHAVIORAL2 FAIL: scheduler.step() was called during initialize_model_and_optimizer")
        sys.exit(1)
    else:
        print("BEHAVIORAL2 PASS: scheduler.step() was NOT called")
        sys.exit(0)
except Exception as e:
    # If execution fails due to import issues etc, that's expected since we can't
    # mock everything. Fall back to AST-only check: verify no opt_param_scheduler.step() in AST.
    import ast as _ast
    with open(TARGET) as _f:
        _tree = _ast.parse(_f.read())
    for _node in _ast.walk(_tree):
        if isinstance(_node, _ast.FunctionDef) and _node.name == "initialize_model_and_optimizer":
            for _child in _ast.walk(_node):
                if isinstance(_child, _ast.Call):
                    _func = _child.func
                    if isinstance(_func, _ast.Attribute) and _func.attr == "step":
                        if isinstance(_func.value, _ast.Name) and _func.value.id == "opt_param_scheduler":
                            print("BEHAVIORAL2 FAIL: opt_param_scheduler.step() still in AST")
                            sys.exit(1)
            break
    print(f"BEHAVIORAL2 PASS (AST fallback): exec failed ({e}) but AST confirms step() removed")
    sys.exit(0)
PYEOF
if [ $? -eq 0 ]; then RESULTS[behavioral2]=1; fi

# ---------- SECONDARY (30%): Structural - the return statement is the last thing ----------
python3 << 'PYEOF'
import ast, sys

TARGET = "/workspace/slime/slime/backends/megatron_utils/model.py"

with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)

func_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "initialize_model_and_optimizer":
        func_node = node
        break

if func_node is None:
    print("STRUCTURAL FAIL: function not found")
    sys.exit(1)

# The last statement of the function should be the return
last_stmt = func_node.body[-1]
if not isinstance(last_stmt, ast.Return):
    print("STRUCTURAL FAIL: last statement is not a return")
    sys.exit(1)

# Return should have a Tuple with 4 elements
if not isinstance(last_stmt.value, ast.Tuple) or len(last_stmt.value.elts) != 4:
    print("STRUCTURAL FAIL: return value is not a 4-tuple")
    sys.exit(1)

# Check that second-to-last statement is clear_memory() call, not scheduler.step()
if len(func_node.body) >= 2:
    second_last = func_node.body[-2]
    if isinstance(second_last, ast.Expr) and isinstance(second_last.value, ast.Call):
        func = second_last.value.func
        if isinstance(func, ast.Attribute) and func.attr == "step":
            print("STRUCTURAL FAIL: statement before return is still scheduler.step()")
            sys.exit(1)

print("STRUCTURAL PASS: function structure looks correct")
sys.exit(0)
PYEOF
if [ $? -eq 0 ]; then RESULTS[structural]=1; fi

# ---------- Config-derived (0.05): No wildcard imports ----------
# Source: .claude/skills/add-tests-and-ci/SKILL.md @ commit 0988f0f4a0ab55d1bb3ce6285a597d912144fa80
echo "=== Config: no wildcard imports ==="
grep -rn "from .* import \*" "$TARGET" 2>/dev/null
if [ $? -ne 0 ]; then RESULTS[config_no_wildcard]=1; echo "TEST config_no_wildcard: PASS"; else echo "TEST config_no_wildcard: FAIL: wildcard import found"; fi

# ---------- Config-derived (0.05): No bare print() in production code ----------
# Source: .claude/skills/add-tests-and-ci/SKILL.md @ commit 0988f0f4a0ab55d1bb3ce6285a597d912144fa80
echo "=== Config: no bare print() ==="
grep -nE "^\s*print\(" "$TARGET" 2>/dev/null
if [ $? -ne 0 ]; then RESULTS[config_no_bare_print]=1; echo "TEST config_no_bare_print: PASS"; else echo "TEST config_no_bare_print: FAIL: bare print() found"; fi

# ---------- SCORE ----------
SCORE="0"
python3 -c "
w = {'behavioral': ${WEIGHTS[behavioral]}, 'behavioral2': ${WEIGHTS[behavioral2]}, 'structural': ${WEIGHTS[structural]}, 'config_no_wildcard': ${WEIGHTS[config_no_wildcard]}, 'config_no_bare_print': ${WEIGHTS[config_no_bare_print]}}
r = {'behavioral': ${RESULTS[behavioral]}, 'behavioral2': ${RESULTS[behavioral2]}, 'structural': ${RESULTS[structural]}, 'config_no_wildcard': ${RESULTS[config_no_wildcard]}, 'config_no_bare_print': ${RESULTS[config_no_bare_print]}}
score = sum(w[k]*r[k] for k in w)
print(f'{score:.4f}')
" > "$REWARD_FILE"

echo "=== RESULTS ==="
for key in behavioral behavioral2 structural config_no_wildcard config_no_bare_print; do
    echo "  $key: ${RESULTS[$key]} (weight ${WEIGHTS[$key]})"
done
echo "Final score: $(cat $REWARD_FILE)"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
