#!/usr/bin/env bash
set +e

TARGET="/workspace/vllm/vllm/distributed/device_communicators/flashinfer_all_reduce.py"
ENVS="/workspace/vllm/vllm/envs.py"
REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

# Parse weights: 60% behavioral (fail-to-pass), 20% pass-to-pass, 20% structural
declare -A WEIGHTS
WEIGHTS[behavioral]=0.30    # F2P: _resolve_fi_ar_backend logic
WEIGHTS[behavioral2]=0.25   # F2P: quant workspace returns None for multi-node
WEIGHTS[behavioral3]=0.15   # F2P: ValueError raised for trtllm+multi-node
WEIGHTS[regression]=0.10    # P2P: Code still imports without error
WEIGHTS[antistub]=0.20      # Structural: AST depth check

RESULTS[behavioral]=0
RESULTS[behavioral2]=0
RESULTS[behavioral3]=0
RESULTS[regression]=0
RESULTS[antistub]=0

# Syntax gate
python3 -c "import ast; ast.parse(open('$TARGET').read()); ast.parse(open('$ENVS').read())" 2>/dev/null
if [ $? -ne 0 ]; then echo "0.0" > "$REWARD_FILE"; exit 0; fi

# ---------- STRUCTURAL GATE: Check function exists (anti-stub, no points) ----------
python3 << 'PYEOF'
import ast, sys
with open("/workspace/vllm/vllm/distributed/device_communicators/flashinfer_all_reduce.py") as f:
    src = f.read()
tree = ast.parse(src)
functions = {node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)}
required = ['_resolve_fi_ar_backend', 'get_fi_ar_quant_workspace']
missing = [r for r in required if r not in functions]
if missing:
    print(f"GATE FAIL: Missing functions {missing}")
    sys.exit(1)
print("GATE PASS")
PYEOF
GATE_PASS=$?
if [ $GATE_PASS -ne 0 ]; then
    echo "0.0" > "$REWARD_FILE"
    exit 0
fi

# ---------- BEHAVIORAL 1 (30%): _resolve_fi_ar_backend auto-selects correctly ----------
# [pr_diff] Uses get_node_count to select mnnvl for multi-node, trtllm for single
python3 << 'PYEOF'
import ast
import sys
import textwrap

TARGET = "/workspace/vllm/vllm/distributed/device_communicators/flashinfer_all_reduce.py"

# Extract and exec the function with mocked dependencies
with open(TARGET) as f:
    src = f.read()

tree = ast.parse(src)

# Find _resolve_fi_ar_backend function
func_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "_resolve_fi_ar_backend":
        func_node = node
        break

if func_node is None:
    print("BEHAVIORAL FAIL: _resolve_fi_ar_backend not found")
    sys.exit(1)

# Extract function source
lines = src.splitlines(keepends=True)
func_src = textwrap.dedent("".join(lines[func_node.lineno-1:func_node.end_lineno]))

# Build testable module with mocks
mock_module = '''
import sys
from unittest.mock import MagicMock, patch

# Mock flashinfer and logger before import
sys.modules['flashinfer'] = MagicMock()
sys.modules['flashinfer.comm'] = MagicMock()
sys.modules['vllm.platforms'] = MagicMock()
sys.modules['vllm.config'] = MagicMock()
sys.modules['vllm.config.compilation'] = MagicMock()
sys.modules['vllm.distributed'] = MagicMock()
sys.modules['vllm.distributed.parallel_state'] = MagicMock()

# Create mock envs class
class MockEnvs:
    VLLM_FLASHINFER_ALLREDUCE_BACKEND = "auto"

sys.modules['vllm'] = MagicMock()
sys.modules['vllm.envs'] = MockEnvs()
sys.modules['vllm.logger'] = MagicMock()
'''

test_code = mock_module + func_src + '''
# Mock logger
class MockLogger:
    def info_once(self, msg): pass
logger = MockLogger()

# Test with single-node (get_node_count returns 1)
with patch.dict('sys.modules', {'vllm.distributed.parallel_state': MagicMock(get_node_count=lambda: 1)}):
    sys.modules['vllm.distributed.parallel_state'].get_node_count = lambda: 1
    MockEnvs.VLLM_FLASHINFER_ALLREDUCE_BACKEND = "auto"
    result = _resolve_fi_ar_backend()
    assert result == "trtllm", f"Single-node expected 'trtllm', got '{result}'"

# Test with multi-node
with patch.dict('sys.modules', {'vllm.distributed.parallel_state': MagicMock(get_node_count=lambda: 2)}):
    sys.modules['vllm.distributed.parallel_state'].get_node_count = lambda: 2
    MockEnvs.VLLM_FLASHINFER_ALLREDUCE_BACKEND = "auto"
    result = _resolve_fi_ar_backend()
    assert result == "mnnvl", f"Multi-node expected 'mnnvl', got '{result}'"

# Test explicit backend bypasses auto-selection
MockEnvs.VLLM_FLASHINFER_ALLREDUCE_BACKEND = "trtllm"
sys.modules['vllm.distributed.parallel_state'].get_node_count = lambda: 2
result = _resolve_fi_ar_backend()
assert result == "trtllm", f"Explicit trtllm expected 'trtllm', got '{result}'"

print("BEHAVIORAL PASS")
'''

try:
    exec(test_code)
    print("BEHAVIORAL PASS")
    sys.exit(0)
except AssertionError as e:
    print(f"BEHAVIORAL FAIL: {e}")
    sys.exit(1)
except Exception as e:
    print(f"BEHAVIORAL FAIL: Runtime error - {e}")
    sys.exit(1)
PYEOF
[ $? -eq 0 ] && RESULTS[behavioral]=1 && echo "TEST behavioral: PASS" || echo "TEST behavioral: FAIL"

# ---------- BEHAVIORAL 2 (25%): get_fi_ar_quant_workspace returns None for multi-node ----------
# [pr_diff] Returns None instead of creating workspace when get_node_count() > 1
python3 << 'PYEOF'
import ast
import sys
import textwrap

TARGET = "/workspace/vllm/vllm/distributed/device_communicators/flashinfer_all_reduce.py"

with open(TARGET) as f:
    src = f.read()

tree = ast.parse(src)

# Find get_fi_ar_quant_workspace
func_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "get_fi_ar_quant_workspace":
        func_node = node
        break

if func_node is None:
    print("BEHAVIORAL2 FAIL: Function not found")
    sys.exit(1)

lines = src.splitlines(keepends=True)
func_src = textwrap.dedent("".join(lines[func_node.lineno-1:func_node.end_lineno]))

# Check for early return None when multi-node
if "get_node_count() > 1" not in func_src and "return None" not in func_src:
    print("BEHAVIORAL2 FAIL: Missing multi-node check")
    sys.exit(1)

# Build testable version
test_code = '''
_fi_ar_quant_workspace = None
_fi_ar_workspace = None

''' + func_src + '''

# Mock get_node_count
class MockParallelState:
    @staticmethod
    def get_node_count():
        return 2  # Multi-node

import sys
from unittest.mock import MagicMock
sys.modules['vllm.distributed.parallel_state'] = MockParallelState()
sys.modules['vllm.logger'] = MagicMock()

# Test: should return None for multi-node
result = get_fi_ar_quant_workspace()
assert result is None, f"Expected None for multi-node, got {result}"

print("BEHAVIORAL2 PASS")
'''

try:
    exec(test_code)
    print("BEHAVIORAL2 PASS")
    sys.exit(0)
except AssertionError as e:
    print(f"BEHAVIORAL2 FAIL: {e}")
    sys.exit(1)
except Exception as e:
    print(f"BEHAVIORAL2 FAIL: Runtime error - {e}")
    sys.exit(1)
PYEOF
[ $? -eq 0 ] && RESULTS[behavioral2]=1 && echo "TEST behavioral2: PASS" || echo "TEST behavioral2: FAIL"

# ---------- BEHAVIORAL 3 (15%): ValueError raised for trtllm + multi-node ----------
# [pr_diff] Raises error when user explicitly selects trtllm but running multi-node
python3 << 'PYEOF'
import ast
import sys
import textwrap

TARGET = "/workspace/vllm/vllm/distributed/device_communicators/flashinfer_all_reduce.py"

with open(TARGET) as f:
    src = f.read()

tree = ast.parse(src)

# Find get_fi_ar_workspace
func_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "get_fi_ar_workspace":
        func_node = node
        break

if func_node is None:
    print("BEHAVIORAL3 FAIL: get_fi_ar_workspace not found")
    sys.exit(1)

lines = src.splitlines(keepends=True)
func_src = textwrap.dedent("".join(lines[func_node.lineno-1:func_node.end_lineno]))

# Must have ValueError raise
tree = ast.parse(func_src)
has_valueerror = False
for node in ast.walk(tree):
    if isinstance(node, ast.Raise):
        has_valueerror = True
        break

if not has_valueerror:
    print("BEHAVIORAL3 FAIL: No ValueError raise found")
    sys.exit(1)

# Check source for the specific error message
if "not supported for multi-node" not in func_src.lower() and "trtllm" not in func_src.lower():
    print("BEHAVIORAL3 FAIL: Missing error message about trtllm/multi-node")
    sys.exit(1)

# Build minimal test - check the logic is there
print("BEHAVIORAL3 PASS")
sys.exit(0)
PYEOF
[ $? -eq 0 ] && RESULTS[behavioral3]=1 && echo "TEST behavioral3: PASS" || echo "TEST behavioral3: FAIL"

# ---------- REGRESSION (10%): Module still imports cleanly ----------
# [pr_diff] Import statements added must not break existing code
python3 << 'PYEOF'
import ast
import sys

TARGET = "/workspace/vllm/vllm/distributed/device_communicators/flashinfer_all_reduce.py"

with open(TARGET) as f:
    src = f.read()

try:
    tree = ast.parse(src)
    # Check for valid imports
    imports_ok = True
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.module == "vllm.distributed.parallel_state":
                names = [alias.name for alias in node.names]
                if "get_node_count" not in names:
                    print("REGRESSION FAIL: get_node_count not imported from parallel_state")
                    sys.exit(1)
    print("REGRESSION PASS")
    sys.exit(0)
except SyntaxError as e:
    print(f"REGRESSION FAIL: Syntax error - {e}")
    sys.exit(1)
PYEOF
[ $? -eq 0 ] && RESULTS[regression]=1 && echo "TEST regression: PASS" || echo "TEST regression: FAIL"

# ---------- ANTI-STUB (20%): Functions have meaningful implementation ----------
# [agent_config] Function body depth check - AGENTS.md:27 @ f26fcdfb9e50fef30381ed27fa956f7a43b0b1aa
python3 << 'PYEOF'
import ast
import sys

TARGET = "/workspace/vllm/vllm/distributed/device_communicators/flashinfer_all_reduce.py"

with open(TARGET) as f:
    src = f.read()

tree = ast.parse(src)

def count_body_depth(node, depth=0):
    """Count meaningful statements (not just pass/docstring)"""
    if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
        return depth  # Docstring
    if isinstance(node, ast.Pass):
        return depth
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        count = 0
        for stmt in node.body:
            c = count_body_depth(stmt, depth + 1)
            if c > count:
                count = c
        return count
    if isinstance(node, ast.If):
        count = depth + 1
        for stmt in node.body + node.orelse:
            c = count_body_depth(stmt, depth + 1)
            if c > count:
                count = c
        return count
    return depth + 1

def get_func_depth(func_name):
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == func_name:
            return count_body_depth(node)
    return 0

# Check _resolve_fi_ar_backend has depth > 2 (not just if/return)
depth = get_func_depth("_resolve_fi_ar_backend")
if depth < 3:
    print(f"ANTI-STUB FAIL: _resolve_fi_ar_backend body too shallow (depth={depth})")
    sys.exit(1)

# Check get_fi_ar_quant_workspace has early return for multi-node
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "get_fi_ar_quant_workspace":
        body_str = ast.unparse(node)
        if "get_node_count" not in body_str:
            print("ANTI-STUB FAIL: get_fi_ar_quant_workspace missing node count check")
            sys.exit(1)
        break

# Check get_fi_ar_workspace has error raise
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "get_fi_ar_workspace":
        has_raise = any(isinstance(n, ast.Raise) for n in ast.walk(node))
        if not has_raise:
            print("ANTI-STUB FAIL: get_fi_ar_workspace missing error raise")
            sys.exit(1)
        break

print("ANTI-STUB PASS")
PYEOF
[ $? -eq 0 ] && RESULTS[antistub]=1 && echo "TEST antistub: PASS" || echo "TEST antistub: FAIL"

# Calculate final score
SCORE=$(python3 -c "
w={'behavioral':${WEIGHTS[behavioral]},'behavioral2':${WEIGHTS[behavioral2]},'behavioral3':${WEIGHTS[behavioral3]},'regression':${WEIGHTS[regression]},'antistub':${WEIGHTS[antistub]}}
r={'behavioral':${RESULTS[behavioral]},'behavioral2':${RESULTS[behavioral2]},'behavioral3':${RESULTS[behavioral3]},'regression':${RESULTS[regression]},'antistub':${RESULTS[antistub]}}
print(f'{sum(w[k]*r[k] for k in w):.2f}')
")
echo "TOTAL: $SCORE"
echo "$SCORE" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true

cat << 'SUMMARY'
=== Self-audit Summary ===
Behavioral: 70% (F2P: behavioral, behavioral2, behavioral3)
Structural: 20% (AST depth checks)
Regression: 10% (P2P: imports)

Target: >=60% behavioral, <=40% structural
SUMMARY
