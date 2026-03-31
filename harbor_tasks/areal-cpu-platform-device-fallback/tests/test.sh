#!/usr/bin/env bash
set +e
set -uo pipefail

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
REPO="/workspace/AReaL"
cd "$REPO"

TOTAL=0.0
B_SCORE=0.0
R_SCORE=0.0
S_SCORE=0.0
C_SCORE=0.0
add()  { TOTAL=$(python3 -c "print(round($TOTAL + $1, 2))"); }
add_b(){ B_SCORE=$(python3 -c "print(round($B_SCORE + $1, 2))"); add "$1"; }
add_r(){ R_SCORE=$(python3 -c "print(round($R_SCORE + $1, 2))"); add "$1"; }
add_s(){ S_SCORE=$(python3 -c "print(round($S_SCORE + $1, 2))"); add "$1"; }
add_c(){ C_SCORE=$(python3 -c "print(round($C_SCORE + $1, 2))"); add "$1"; }

###############################################################################
# GATE: All modified files must be valid Python
###############################################################################
GATE_PASS=1
for f in areal/infra/platforms/cpu.py areal/engine/fsdp_engine.py \
         areal/experimental/engine/archon_engine.py areal/infra/scheduler/local.py; do
    if ! python3 -c "import ast; ast.parse(open('$f').read())" 2>/dev/null; then
        echo "GATE FAIL: $f has syntax errors"
        GATE_PASS=0
    fi
done

if [ "$GATE_PASS" -eq 0 ]; then
    echo "0.0" > "/logs/verifier/reward.txt"
    echo '{"reward":0.0,"behavioral":0.0,"regression":0.0,"structural":0.0,"config":0.0}' \
        > "/logs/verifier/reward.json"
    exit 0
fi

###############################################################################
# Helper: extract CpuPlatform class via AST and exec with mock Platform base.
# This lets us CALL actual methods without torch (which isn't installed).
###############################################################################
cat > /tmp/_extract_cpu.py << 'PYEOF'
import ast, sys, textwrap

def get_cpu_platform():
    source = open("areal/infra/platforms/cpu.py").read()
    tree = ast.parse(source)
    class_node = None
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "CpuPlatform":
            class_node = node
            break
    if class_node is None:
        print("ERROR: CpuPlatform class not found", file=sys.stderr)
        sys.exit(1)
    class_src = ast.get_source_segment(source, class_node)
    if class_src is None:
        lines = source.splitlines(keepends=True)
        class_src = textwrap.dedent("".join(lines[class_node.lineno - 1 : class_node.end_lineno]))
    # Provide a lightweight Platform stub as base class
    class Platform:
        pass
    ns = {"Platform": Platform, "__builtins__": __builtins__}
    exec(class_src, ns)
    return ns["CpuPlatform"]
PYEOF

###############################################################################
# BEHAVIORAL: Fail-to-pass — Problem 1 (0.55 total)
# These use AST extraction + exec to actually CALL the methods.
###############################################################################

# [pr_diff] (0.30): CpuPlatform.memory_allocated() and memory_reserved() return 0
BEHAV1_PASS=0
python3 -c "
import sys; sys.path.insert(0, '/tmp')
from _extract_cpu import get_cpu_platform
CpuPlatform = get_cpu_platform()
p = CpuPlatform()

# On buggy code these methods don't exist → AttributeError from Platform.__getattr__
result_a = p.memory_allocated()
result_r = p.memory_reserved()
assert isinstance(result_a, (int, float)), f'memory_allocated returned {type(result_a)}, want number'
assert isinstance(result_r, (int, float)), f'memory_reserved returned {type(result_r)}, want number'
assert result_a == 0, f'memory_allocated should be 0 on CPU, got {result_a}'
assert result_r == 0, f'memory_reserved should be 0 on CPU, got {result_r}'

# Call again to ensure consistency (not random/stateful)
assert p.memory_allocated() == 0
assert p.memory_reserved() == 0
print('PASS: memory_allocated and memory_reserved return 0')
"
if [ $? -eq 0 ]; then add_b 0.30; BEHAV1_PASS=1; else echo "FAIL: CpuPlatform memory methods"; fi

# [pr_diff] (0.15): CpuPlatform.mem_get_info() returns a 2-tuple of zeros
python3 -c "
import sys; sys.path.insert(0, '/tmp')
from _extract_cpu import get_cpu_platform
p = get_cpu_platform()()

result = p.mem_get_info()
assert isinstance(result, tuple), f'mem_get_info should return tuple, got {type(result)}'
assert len(result) == 2, f'mem_get_info should return 2-tuple, got length {len(result)}'
assert all(isinstance(v, (int, float)) for v in result), f'mem_get_info values should be numeric, got {result}'
assert all(v == 0 for v in result), f'mem_get_info should be (0, 0) on CPU, got {result}'
print('PASS: mem_get_info returns (0, 0)')
" && add_b 0.15 || echo "FAIL: CpuPlatform.mem_get_info"

# [pr_diff] (0.10): CpuPlatform.empty_cache() callable without error and returns None
python3 -c "
import sys; sys.path.insert(0, '/tmp')
from _extract_cpu import get_cpu_platform
p = get_cpu_platform()()

result = p.empty_cache()  # should be a no-op, not raise
# empty_cache should return None (no-op)
assert result is None, f'empty_cache should return None, got {result!r}'
# Call twice to ensure idempotent
p.empty_cache()
print('PASS: empty_cache callable without error')
" && add_b 0.10 || echo "FAIL: CpuPlatform.empty_cache"

###############################################################################
# BEHAVIORAL: Fail-to-pass — Problem 2 (0.15, gated behind Problem 1)
# AST justified: _create_device_model uses torch.device() which requires torch.
# Improved: verify the conditional actually references platform/device concepts,
# and that 'cpu' appears as argument to a Call (not just anywhere).
###############################################################################

if [ "$BEHAV1_PASS" -eq 1 ]; then

# [pr_diff] (0.15): _create_device_model in fsdp_engine handles cpu platform
python3 -c "
import ast, sys

source = open('areal/engine/fsdp_engine.py').read()
tree = ast.parse(source)

func_node = None
for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == '_create_device_model':
        func_node = node
        break

assert func_node is not None, '_create_device_model function not found'

# Check 1: function body has >3 statements (reject trivial stubs)
body_stmts = [n for n in ast.walk(func_node) if isinstance(n, ast.stmt)]
assert len(body_stmts) >= 4, f'_create_device_model has only {len(body_stmts)} statements — looks like a stub'

# Check 2: has a conditional that references platform or device-related names
has_platform_conditional = False
platform_names = {'platform', 'device_type', '_platform', 'device', 'is_cpu', 'cpu'}

for node in ast.walk(func_node):
    if isinstance(node, (ast.If, ast.IfExp)):
        # Get all Name nodes in the test/condition
        test_node = node.test if isinstance(node, ast.If) else node.test
        cond_names = {n.attr if isinstance(n, ast.Attribute) else n.id
                      for n in ast.walk(test_node)
                      if isinstance(n, (ast.Name, ast.Attribute))}
        if cond_names & platform_names:
            has_platform_conditional = True
            break

assert has_platform_conditional, \
    '_create_device_model needs a conditional that checks platform/device type'

# Check 3: 'cpu' string appears as an argument to a function call (e.g., torch.device('cpu'))
has_cpu_in_call = False
for node in ast.walk(func_node):
    if isinstance(node, ast.Call):
        for arg in node.args:
            if isinstance(arg, ast.Constant) and arg.value == 'cpu':
                has_cpu_in_call = True
                break
        if has_cpu_in_call:
            break

# Alternative: 'cpu' could come from a variable like platform.device_type
# Accept if there's a platform conditional even without literal 'cpu' in call
has_cpu_ref = has_cpu_in_call
if not has_cpu_ref:
    # Check if device_type is accessed (covers torch.device(platform.device_type))
    for node in ast.walk(func_node):
        if isinstance(node, ast.Attribute) and node.attr == 'device_type':
            has_cpu_ref = True
            break

assert has_cpu_ref, '_create_device_model should reference cpu device or device_type'
print('PASS: fsdp_engine _create_device_model handles cpu')
" && add_b 0.15 || echo "FAIL: fsdp_engine cpu device handling"

else
    echo "SKIP: fsdp_engine check gated behind Problem 1 behavioral pass"
fi

###############################################################################
# BEHAVIORAL: Fail-to-pass — Problem 3 (0.10, gated behind Problem 1)
# AST justified: create_workers uses distributed process control requiring torch.
# Improved: handles both if-statements and ternary expressions, verifies the
# conditional actually checks the env var or platform, not just 'if True'.
###############################################################################

if [ "$BEHAV1_PASS" -eq 1 ]; then

# [pr_diff] (0.10): scheduler guards device_control_env_var before env assignment
python3 -c "
import ast, sys

source = open('areal/infra/scheduler/local.py').read()
tree = ast.parse(source)

class GuardChecker(ast.NodeVisitor):
    '''Walk the AST to verify the device_control_env_var assignment is properly guarded.'''
    def __init__(self):
        self.guard_depth = 0
        self.found_guarded = False
        self.found_unguarded = False
        self.guard_is_meaningful = False  # tracks if guard checks something real

    def visit_If(self, node):
        # Check if the condition references relevant names
        cond_src = ast.get_source_segment(source, node.test) or ''
        meaningful = any(kw in cond_src for kw in
            ['device_control_env_var', 'env_var', 'platform', 'device_type'])
        old_meaningful = self.guard_is_meaningful
        if meaningful:
            self.guard_is_meaningful = True
        self.guard_depth += 1
        self.generic_visit(node)
        self.guard_depth -= 1
        self.guard_is_meaningful = old_meaningful

    def visit_IfExp(self, node):
        # Handle ternary: value if test else other
        cond_src = ast.get_source_segment(source, node.test) or ''
        meaningful = any(kw in cond_src for kw in
            ['device_control_env_var', 'env_var', 'platform', 'device_type'])
        old_meaningful = self.guard_is_meaningful
        if meaningful:
            self.guard_is_meaningful = True
        self.guard_depth += 1
        self.generic_visit(node)
        self.guard_depth -= 1
        self.guard_is_meaningful = old_meaningful

    def visit_Assign(self, node):
        for target in node.targets:
            if isinstance(target, ast.Subscript):
                target_src = ast.get_source_segment(source, target) or ''
                if 'device_control_env_var' in target_src:
                    if self.guard_depth > 0 and self.guard_is_meaningful:
                        self.found_guarded = True
                    else:
                        self.found_unguarded = True
        self.generic_visit(node)

checker = GuardChecker()
checker.visit(tree)

assert checker.found_guarded, \
    'device_control_env_var env assignment must be inside a conditional guard that checks the var'
assert not checker.found_unguarded, \
    'device_control_env_var env assignment found outside meaningful conditional — bug not fixed'
print('PASS: scheduler guards device_control_env_var assignment')
" && add_b 0.10 || echo "FAIL: scheduler env var guard"

else
    echo "SKIP: scheduler check gated behind Problem 1 behavioral pass"
fi

###############################################################################
# REGRESSION: Pass-to-pass (0.15)
###############################################################################

# [pr_diff] (0.10): Existing CpuPlatform API preserved (clear_memory, get_visible_devices, attrs)
python3 -c "
import sys; sys.path.insert(0, '/tmp')
from _extract_cpu import get_cpu_platform
CpuPlatform = get_cpu_platform()
p = CpuPlatform()

p.clear_memory()  # should not raise
devs = p.get_visible_devices()
assert isinstance(devs, list), f'get_visible_devices should return list, got {type(devs)}'
assert devs == [], f'get_visible_devices should return [], got {devs}'
assert p.device_type == 'cpu', f'device_type should be \"cpu\", got {p.device_type!r}'
assert p.device_control_env_var == '', f'device_control_env_var should be \"\", got {p.device_control_env_var!r}'
print('PASS: existing CpuPlatform API preserved')
" && add_r 0.10 || echo "FAIL: CpuPlatform regression"

# [pr_diff] (0.05): archon_engine also handles cpu device (same pattern as fsdp_engine)
# Only run if Problem 1 is solved (gated to prevent gaming)
if [ "$BEHAV1_PASS" -eq 1 ]; then
python3 -c "
import ast, sys

source = open('areal/experimental/engine/archon_engine.py').read()
tree = ast.parse(source)

func_node = None
for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == '_create_device_model':
        func_node = node
        break

assert func_node is not None, '_create_device_model not found in archon_engine.py'

# Must have >3 statements (reject stubs)
body_stmts = [n for n in ast.walk(func_node) if isinstance(n, ast.stmt)]
assert len(body_stmts) >= 4, 'archon_engine _create_device_model looks like a stub'

# Must have conditional referencing platform/device
platform_names = {'platform', 'device_type', '_platform', 'device', 'is_cpu', 'cpu'}
has_platform_cond = False
for node in ast.walk(func_node):
    if isinstance(node, (ast.If, ast.IfExp)):
        test_node = node.test if isinstance(node, ast.If) else node.test
        cond_names = {n.attr if isinstance(n, ast.Attribute) else n.id
                      for n in ast.walk(test_node)
                      if isinstance(n, (ast.Name, ast.Attribute))}
        if cond_names & platform_names:
            has_platform_cond = True
            break

# Must reference cpu device or device_type
has_cpu_ref = False
for node in ast.walk(func_node):
    if isinstance(node, ast.Call):
        for arg in node.args:
            if isinstance(arg, ast.Constant) and arg.value == 'cpu':
                has_cpu_ref = True
    if isinstance(node, ast.Attribute) and node.attr == 'device_type':
        has_cpu_ref = True

assert has_platform_cond and has_cpu_ref, 'archon_engine should handle cpu platform in _create_device_model'
print('PASS: archon_engine handles cpu platform')
" && add_r 0.05 || echo "FAIL: archon_engine cpu device handling"
else
    echo "SKIP: archon_engine check gated behind Problem 1 behavioral pass"
fi

###############################################################################
# CONFIG-DERIVED (0.05)
###############################################################################

# [agent_config] (0.05): No wildcard imports — CLAUDE.md:93 @ 6208006
python3 -c "
import ast
for f in ['areal/infra/platforms/cpu.py', 'areal/engine/fsdp_engine.py',
          'areal/experimental/engine/archon_engine.py', 'areal/infra/scheduler/local.py']:
    tree = ast.parse(open(f).read())
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.names:
            for alias in node.names:
                assert alias.name != '*', f'Wildcard import found in {f}'
print('PASS: no wildcard imports')
" && add_c 0.05 || echo "FAIL: wildcard imports found"

###############################################################################
# TOTAL
###############################################################################
echo ""
echo "Total score: $TOTAL"
echo "$TOTAL" > "/logs/verifier/reward.txt"

python3 -c "
import json
print(json.dumps({
    'reward': $TOTAL,
    'behavioral': $B_SCORE,
    'regression': $R_SCORE,
    'structural': $S_SCORE,
    'config': $C_SCORE,
    'style_rubric': 0.0
}))
" > "/logs/verifier/reward.json"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
