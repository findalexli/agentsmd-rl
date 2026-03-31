#!/usr/bin/env bash
set +e

REPO=/workspace/vllm
WEIGHT_UTILS="$REPO/vllm/model_executor/model_loader/weight_utils.py"
TEST_FILE="$REPO/tests/compile/fullgraph/test_basic_correctness.py"
export WEIGHT_UTILS TEST_FILE

TOTAL=0.0
add() { TOTAL=$(python3 -c "print(round($TOTAL + $1, 2))"); }

echo "=== vllm-gptq-compile-correctness ==="

# ── GATE (0.00): Syntax check — abort on failure ──
echo ""
echo "--- GATE: Syntax check ---"
python3 -c "
import ast, sys
for f in ['$WEIGHT_UTILS', '$TEST_FILE']:
    try:
        ast.parse(open(f).read())
    except SyntaxError as e:
        print(f'GATE FAIL: {f}: {e}')
        sys.exit(1)
print('GATE PASS: Both files parse OK')
" || { echo "0.0" > /logs/verifier/reward.txt; echo '{"reward":0.0}' > /logs/verifier/reward.json; exit 0; }

# ── [pr_diff] (0.30): Integer params get zero_() on ROCm ──
# Behavioral F2P: extract initialize_single_dummy_weight, mock ROCm platform,
# call with int32/int64 tensors, verify they are zeroed.
echo ""
echo "--- [pr_diff] (0.30): Integer params zeroed on ROCm ---"
python3 << 'PYEOF'
import torch, ast, types, sys, os

src = open(os.environ["WEIGHT_UTILS"]).read()
tree = ast.parse(src)

func_src = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "initialize_single_dummy_weight":
        func_src = ast.get_source_segment(src, node)
        break

if not func_src:
    print("FAIL: initialize_single_dummy_weight not found")
    sys.exit(1)

# Mock platform as ROCm
platform = types.SimpleNamespace(is_tpu=lambda: False, is_rocm=lambda: True)
ns = {"torch": torch, "current_platform": platform}
exec(compile(ast.parse(func_src), "<test>", "exec"), ns)
fn = ns["initialize_single_dummy_weight"]

# int32 tensor with non-zero values — should be zeroed on ROCm
p = torch.ones(4, 4, dtype=torch.int32) * 42
fn(p)
assert torch.all(p == 0), f"Expected int32 param zeroed on ROCm, got non-zero values"

# int64 tensor too
p2 = torch.ones(8, dtype=torch.int64) * 99
fn(p2)
assert torch.all(p2 == 0), f"Expected int64 param zeroed on ROCm, got non-zero values"

print("PASS: Integer params (int32, int64) zeroed on ROCm")
PYEOF
if [ $? -eq 0 ]; then add 0.30; fi

# ── [pr_diff] (0.30): Test list construction — execute real code, verify matching lengths ──
# Behavioral F2P: extract test_compile_correctness, mock compare_all_settings to
# capture call args, execute the function, verify len(all_args)==len(all_envs) at
# every call site. Accepts ANY valid restructuring (list comp, extend, tuples, etc.)
echo ""
echo "--- [pr_diff] (0.30): List construction produces matching args/envs ---"
python3 << 'PYEOF'
import ast, sys, os, inspect
from enum import Enum

src = open(os.environ["TEST_FILE"]).read()
tree = ast.parse(src)

# Find test_compile_correctness function
func_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "test_compile_correctness":
        func_node = node
        break

if func_node is None:
    print("FAIL: test_compile_correctness not found")
    sys.exit(1)

# Extract function source (from def line, excluding decorators)
lines = src.splitlines(keepends=True)
func_src = "".join(lines[func_node.lineno - 1 : func_node.end_lineno])

# Mock CompilationMode
class CompilationMode(Enum):
    NONE = 0
    STOCK_TORCH_COMPILE = 1
    DYNAMO_TRACE_ONCE = 2
    VLLM_COMPILE = 3

# Track all compare_all_settings calls
calls = []
def compare_all_settings(model, all_args, all_envs, method="generate"):
    calls.append({"args_len": len(all_args), "envs_len": len(all_envs)})

ns = {
    "CompilationMode": CompilationMode,
    "compare_all_settings": compare_all_settings,
    "__builtins__": __builtins__,
}

exec(compile(ast.parse(func_src), "<test>", "exec"), ns)
fn = ns["test_compile_correctness"]

# Discover parameter names and call with mock values
sig = inspect.signature(fn)
mock_values = {
    "model": "mock-model", "tp_size": 1, "pp_size": 1,
    "method": "generate", "fullgraph": True, "model_runner": "ModelRunner",
}
kwargs = {p: mock_values.get(p, "default") for p in sig.parameters}

try:
    fn(**kwargs)
except TypeError:
    # Fallback: try positional
    fn(*[mock_values.get(p, "default") for p in sig.parameters])

# Verify all calls had matching non-empty lengths
assert len(calls) >= 1, f"Expected >=1 compare_all_settings calls, got 0"

for i, call in enumerate(calls):
    assert call["args_len"] == call["envs_len"], \
        f"compare_all_settings call {i}: len(all_args)={call['args_len']} != len(all_envs)={call['envs_len']}"
    assert call["args_len"] > 0, \
        f"compare_all_settings call {i}: 0 configurations (empty lists)"

print(f"PASS: {len(calls)} compare_all_settings call(s), all with matching non-empty list lengths")
PYEOF
if [ $? -eq 0 ]; then add 0.30; fi

# ── [pr_diff] (0.15): Float params still initialized correctly (pass-to-pass) ──
# Behavioral P2P: extract function, call with float32 params, verify range and
# reproducibility. This should pass both before and after the fix.
echo ""
echo "--- [pr_diff] (0.15): Float params still initialized (regression) ---"
python3 << 'PYEOF'
import torch, ast, types, sys, os

src = open(os.environ["WEIGHT_UTILS"]).read()
tree = ast.parse(src)

func_src = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "initialize_single_dummy_weight":
        func_src = ast.get_source_segment(src, node)
        break

if not func_src:
    print("FAIL: function not found"); sys.exit(1)

# Mock platform as standard CUDA (non-TPU, non-ROCm)
platform = types.SimpleNamespace(is_tpu=lambda: False, is_rocm=lambda: False)
ns = {"torch": torch, "current_platform": platform}
exec(compile(ast.parse(func_src), "<test>", "exec"), ns)
fn = ns["initialize_single_dummy_weight"]

# float32 param — should be initialized in [low, high]
p = torch.zeros(16, 16, dtype=torch.float32)
fn(p, low=-1e-3, high=1e-3, seed=1234)
assert not torch.all(p == 0), "Float param should not remain all zeros after initialization"
assert p.min().item() >= -1e-3 - 1e-6, f"Float param below range: {p.min().item()}"
assert p.max().item() <= 1e-3 + 1e-6, f"Float param above range: {p.max().item()}"

# Reproducibility: same seed gives same values
p2 = torch.zeros(16, 16, dtype=torch.float32)
fn(p2, low=-1e-3, high=1e-3, seed=1234)
assert torch.allclose(p, p2), "Same seed should produce identical initialization"
print("PASS: Float params initialized correctly with proper range and reproducibility")
PYEOF
if [ $? -eq 0 ]; then add 0.15; fi

# ── [pr_diff] (0.05): Non-ROCm integer params — early return, no crash ──
# Behavioral P2P: on non-ROCm, integer params should not cause an error.
echo ""
echo "--- [pr_diff] (0.05): Non-ROCm int params handled without error ---"
python3 << 'PYEOF'
import torch, ast, types, sys, os

src = open(os.environ["WEIGHT_UTILS"]).read()
tree = ast.parse(src)

func_src = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "initialize_single_dummy_weight":
        func_src = ast.get_source_segment(src, node)
        break

if not func_src:
    print("FAIL: function not found"); sys.exit(1)

# Non-ROCm platform
platform = types.SimpleNamespace(is_tpu=lambda: False, is_rocm=lambda: False)
ns = {"torch": torch, "current_platform": platform}
exec(compile(ast.parse(func_src), "<test>", "exec"), ns)
fn = ns["initialize_single_dummy_weight"]

# int32 tensor — should not crash (should return gracefully)
p = torch.ones(4, 4, dtype=torch.int32) * 42
try:
    fn(p)
    print("PASS: Non-ROCm int params handled without error")
except Exception as e:
    print(f"FAIL: Non-ROCm int param raised: {e}")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then add 0.05; fi

# ── [pr_diff] (0.05): Inductor comparison is not dead code ──
# Behavioral F2P: the inductor section should produce >=1 compare_all_settings call
# with >0 pairs. On the buggy code, the inductor call has 0 envs (dead code).
echo ""
echo "--- [pr_diff] (0.05): Inductor comparison produces pairs ---"
python3 << 'PYEOF'
import ast, sys, os, inspect
from enum import Enum

src = open(os.environ["TEST_FILE"]).read()
tree = ast.parse(src)

func_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "test_compile_correctness":
        func_node = node
        break

if func_node is None:
    print("FAIL: test_compile_correctness not found")
    sys.exit(1)

lines = src.splitlines(keepends=True)
func_src = "".join(lines[func_node.lineno - 1 : func_node.end_lineno])

class CompilationMode(Enum):
    NONE = 0
    STOCK_TORCH_COMPILE = 1
    DYNAMO_TRACE_ONCE = 2
    VLLM_COMPILE = 3

calls = []
def compare_all_settings(model, all_args, all_envs, method="generate"):
    calls.append({"args": len(all_args), "envs": len(all_envs)})

ns = {
    "CompilationMode": CompilationMode,
    "compare_all_settings": compare_all_settings,
    "__builtins__": __builtins__,
}
exec(compile(ast.parse(func_src), "<test>", "exec"), ns)
fn = ns["test_compile_correctness"]

sig = inspect.signature(fn)
mock_values = {
    "model": "mock-model", "tp_size": 1, "pp_size": 1,
    "method": "generate", "fullgraph": True, "model_runner": "ModelRunner",
}
kwargs = {p: mock_values.get(p, "default") for p in sig.parameters}

try:
    fn(**kwargs)
except Exception:
    pass

# Must have >=2 calls (inductor comparisons + final eager)
# If inductor is dead code, only 1 call (the eager one) occurs
assert len(calls) >= 2, \
    f"Expected >=2 compare_all_settings calls (inductor+eager), got {len(calls)} — inductor section may be dead code"
assert calls[0]["args"] > 0 and calls[0]["envs"] > 0, \
    f"First compare_all_settings call has 0 pairs — inductor loop produces nothing"

print(f"PASS: {len(calls)} compare_all_settings calls, inductor section produces {calls[0]['args']} pair(s)")
PYEOF
if [ $? -eq 0 ]; then add 0.05; fi

# ── [agent_config] (0.10): ruff lint passes on changed files — AGENTS.md:53-55 ──
echo ""
echo '--- [agent_config] (0.10): "pre-commit run ruff-check" — AGENTS.md:53-55 ---'
if command -v ruff &>/dev/null; then
    ruff check "$WEIGHT_UTILS" "$TEST_FILE" --select E,F,W --quiet 2>&1
    if [ $? -eq 0 ]; then
        echo "PASS: ruff lint clean"
        add 0.10
    else
        echo "FAIL: ruff lint errors found"
    fi
else
    echo "SKIP: ruff not installed (awarding points)"
    add 0.10
fi

# ── [pr_diff] (0.05): Anti-stub — function body is non-trivial ──
echo ""
echo "--- [pr_diff] (0.05): Anti-stub check ---"
python3 << 'PYEOF'
import ast, sys, os

src = open(os.environ["WEIGHT_UTILS"]).read()
tree = ast.parse(src)

for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "initialize_single_dummy_weight":
        # Count meaningful statements via AST (not string matching)
        meaningful = 0
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.Assign,
                                   ast.AugAssign, ast.Return)):
                meaningful += 1
            elif isinstance(child, ast.Expr):
                # Skip docstrings
                if not isinstance(getattr(child, 'value', None), (ast.Constant,)):
                    meaningful += 1
        assert meaningful >= 5, f"Function has only {meaningful} meaningful statements — likely a stub"
        print(f"PASS: Function has {meaningful} meaningful statements")
        break
else:
    print("FAIL: Function not found")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then add 0.05; fi

# ── Final score ──
echo ""
echo "=== Total: $TOTAL ==="
mkdir -p /logs/verifier
echo "$TOTAL" > /logs/verifier/reward.txt
python3 -c "
import json
t = float('$TOTAL')
d = {'reward': t,
     'behavioral': min(t, 0.85),
     'regression': max(0, min(t - 0.85, 0.05)),
     'config': max(0, min(t - 0.90, 0.10)),
     'structural': max(0, min(t - 0.95, 0.05))}
print(json.dumps(d))
" > /logs/verifier/reward.json

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
