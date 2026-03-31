#!/usr/bin/env bash
set +e

TARGET="/workspace/AReaL/areal/experimental/models/archon/moe/router.py"
REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

# Weight definitions
declare -A WEIGHTS
WEIGHTS[gate]=0.00
WEIGHTS[f2p_hook_fire]=0.35
WEIGHTS[f2p_state_dict]=0.20
WEIGHTS[f2p_forward_call]=0.20
WEIGHTS[p2p_compute]=0.15
WEIGHTS[regression]=0.10

for key in gate f2p_hook_fire f2p_state_dict f2p_forward_call p2p_compute regression; do
    eval "${key}_PASS=0"
done

echo "=== Test Suite: areal-router-gate-dtensor-hook ==="
echo ""

# ============ GATE: Python syntax validity ============
echo "[GATE] Checking Python syntax..."
python3 -c "
import ast, sys
try:
    with open('$TARGET') as f:
        ast.parse(f.read())
    sys.exit(0)
except SyntaxError as e:
    print(f'Syntax error: {e}')
    sys.exit(1)
"
if [ $? -ne 0 ]; then
    echo "GATE FAIL: syntax errors"
    echo "0.0" > "$REWARD_FILE"
    exit 0
fi
echo "GATE PASS: syntax valid"
gate_PASS=1

# ============ FAIL-TO-PASS 1 (35%): Verify gate module call enables hook firing ============
# [pr_diff] (0.35): DTensor hooks fire when calling self.gate(x) instead of router_gating_linear(x, weight)
echo ""
echo "[F2P-1] Verifying DTensor hook firing capability..."
python3 << 'PYEOF'
import ast
import sys
import os

TARGET = "/workspace/AReaL/areal/experimental/models/archon/moe/router.py"

# Parse the source
with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)

# Find TokenChoiceTopKRouter.forward and analyze its code
forward_calls_gate = False
buggy_pattern_present = False

for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "TokenChoiceTopKRouter":
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name == "forward":
                # Get the forward method source
                forward_node = item
                lines = source.splitlines()
                forward_lines = lines[forward_node.lineno:forward_node.end_lineno]
                forward_src = "\n".join(forward_lines)

                # Check for the BUGGY pattern: router_gating_linear(x, self.gate.weight, ...)
                # This bypasses DTensor hooks
                if "router_gating_linear" in forward_src and "self.gate.weight" in forward_src:
                    buggy_pattern_present = True

                # Check for the FIXED pattern: calling self.gate(x) as a module
                # This allows DTensor hooks registered on the module to fire
                for stmt in ast.walk(forward_node):
                    if isinstance(stmt, ast.Call):
                        # Check for self.gate(x) call
                        if isinstance(stmt.func, ast.Attribute):
                            if isinstance(stmt.func.value, ast.Name) and stmt.func.value.id == "self" and stmt.func.attr == "gate":
                                forward_calls_gate = True
                                break
                break
        break

if buggy_pattern_present:
    print("FAIL: forward() still bypasses self.gate with router_gating_linear(x, self.gate.weight, ...)")
    sys.exit(1)

if not forward_calls_gate:
    print("FAIL: forward() does not call self.gate(x) as a module")
    sys.exit(1)

# Also verify that a proper nn.Module subclass is created and used
has_gate_subclass = False
gate_class_name = None

for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef):
        for base in node.bases:
            base_name = None
            if isinstance(base, ast.Name):
                base_name = base.id
            elif isinstance(base, ast.Attribute):
                base_name = base.attr

            if base_name == "Linear":
                # Check this class has forward calling router_gating_linear
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name == "forward":
                        item_src = ast.dump(item)
                        if "router_gating_linear" in item_src or "router_gating_linear" in source:
                            has_gate_subclass = True
                            gate_class_name = node.name
                            break
                break

if not has_gate_subclass:
    print("FAIL: No nn.Linear subclass found that wraps router_gating_linear")
    sys.exit(1)

print(f"PASS: forward() calls self.gate(x), enabling DTensor hooks; {gate_class_name} wraps router_gating_linear")
PYEOF
if [ $? -eq 0 ]; then
    f2p_hook_fire_PASS=1
    echo "RESULT: PASS"
else
    echo "RESULT: FAIL"
fi

# ============ FAIL-TO-PASS 2 (20%): Verify state dict compatibility with nn.Linear ============
# [pr_diff] (0.20): RouterGateLinear state dict matches nn.Linear(bias=False) for checkpoint compatibility
echo ""
echo "[F2P-2] Verifying state dict compatibility..."
python3 << 'PYEOF'
import sys
import os

# Suppress warnings
os.environ['PYTHONWARNINGS'] = 'ignore'

TARGET = "/workspace/AReaL/areal/experimental/models/archon/moe/router.py"

# Need to mock CUDA-specific imports that may fail on CPU-only environment
import unittest.mock

# First, parse to find the RouterGateLinear class
import ast
with open(TARGET) as f:
    source = f.read()

tree = ast.parse(source)

# Find RouterGateLinear or equivalent class
gate_class_name = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef):
        for base in node.bases:
            base_name = None
            if isinstance(base, ast.Name):
                base_name = base.id
            elif isinstance(base, ast.Attribute):
                base_name = base.attr
            if base_name == "Linear":
                gate_class_name = node.name
                break
        if gate_class_name:
            break

if not gate_class_name:
    print("FAIL: Gate class not found")
    sys.exit(1)

# Now try to import and instantiate
sys.path.insert(0, '/workspace/AReaL')

try:
    # Try direct import first
    from areal.experimental.models.archon.moe.router import TokenChoiceTopKRouter
    import torch.nn as nn
    import torch

    # Find the gate class by inspection
    router_module = sys.modules['areal.experimental.models.archon.moe.router']
    GateClass = None
    for name in dir(router_module):
        obj = getattr(router_module, name)
        if isinstance(obj, type) and issubclass(obj, nn.Linear) and name != 'Linear':
            if hasattr(obj, 'forward'):
                GateClass = obj
                break

    if GateClass is None:
        print("FAIL: Could not find Gate class in module")
        sys.exit(1)

    # Test state dict compatibility
    gate = GateClass(16, 8)
    linear = nn.Linear(16, 8, bias=False)

    gate_keys = set(gate.state_dict().keys())
    linear_keys = set(linear.state_dict().keys())

    if gate_keys != linear_keys:
        print(f"FAIL: State dict keys mismatch: {gate_keys} vs {linear_keys}")
        sys.exit(1)

    print(f"PASS: {GateClass.__name__}.state_dict() matches nn.Linear(bias=False)")
except ImportError as e:
    # If import fails due to missing dependencies, check AST instead
    print(f"Note: Import failed ({e}), falling back to AST check for bias=False")

    # Verify the gate class __init__ calls super().__init__ with bias=False
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == gate_class_name:
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name == "__init__":
                    init_src = ast.dump(item)
                    if "bias" in init_src and ("bias=False" in ast.unparse(item) if hasattr(ast, 'unparse') else True):
                        print(f"PASS: {gate_class_name}.__init__ configures bias=False for checkpoint compatibility")
                        sys.exit(0)
            break

    print("FAIL: Gate class does not set bias=False")
    sys.exit(1)
except Exception as e:
    print(f"FAIL: Unexpected error: {e}")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
    f2p_state_dict_PASS=1
    echo "RESULT: PASS"
else
    echo "RESULT: FAIL"
fi

# ============ FAIL-TO-PASS 3 (20%): Verify forward correctly delegates to router_gating_linear ============
# [pr_diff] (0.20): Gate computation works correctly via wrapper class
echo ""
echo "[F2P-3] Verifying gate forward behavior..."
python3 << 'PYEOF'
import sys
import os

os.environ['PYTHONWARNINGS'] = 'ignore'

TARGET_DIR = "/workspace/AReaL"
sys.path.insert(0, TARGET_DIR)

# Parse to find the class
import ast
with open(f"{TARGET_DIR}/areal/experimental/models/archon/moe/router.py") as f:
    source = f.read()

tree = ast.parse(source)

# Find the gate class
gate_class_name = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef):
        for base in node.bases:
            base_name = None
            if isinstance(base, ast.Name):
                base_name = base.id
            elif isinstance(base, ast.Attribute):
                base_name = base.attr
            if base_name == "Linear":
                # Verify it has forward calling router_gating_linear
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name == "forward":
                        item_src = ast.unparse(item) if hasattr(ast, 'unparse') else ast.dump(item)
                        if "router_gating_linear" in item_src or "router_gating_linear" in source:
                            gate_class_name = node.name
                            break
                break
        if gate_class_name:
            break

if not gate_class_name:
    print("FAIL: Gate class not found")
    sys.exit(1)

try:
    import torch
    import torch.nn as nn

    # Import router module
    from areal.experimental.models.archon.moe.router import TokenChoiceTopKRouter

    router_module = sys.modules['areal.experimental.models.archon.moe.router']
    GateClass = None
    for name in dir(router_module):
        obj = getattr(router_module, name)
        if isinstance(obj, type) and issubclass(obj, nn.Linear) and name != 'Linear':
            GateClass = obj
            break

    if GateClass is None:
        print("FAIL: Gate class not found in module")
        sys.exit(1)

    # Test the gate actually computes something
    gate = GateClass(16, 8, router_dtype=None)  # No dtype override

    # Test with simple input
    x = torch.randn(4, 16)
    out = gate(x)

    if out.shape != (4, 8):
        print(f"FAIL: Wrong output shape: {out.shape}, expected (4, 8)")
        sys.exit(1)

    # Test with router_dtype specified
    gate_fp32 = GateClass(16, 8, router_dtype=torch.float32)
    x_bf16 = torch.randn(4, 16, dtype=torch.bfloat16)
    out_fp32 = gate_fp32(x_bf16)

    if out_fp32.dtype != torch.float32:
        print(f"FAIL: With router_dtype=float32, output dtype should be float32, got {out_fp32.dtype}")
        sys.exit(1)

    print(f"PASS: {GateClass.__name__}.forward() correctly computes gate scores")
except ImportError as e:
    print(f"FAIL: Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"FAIL: Error during execution: {e}")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
    f2p_forward_call_PASS=1
    echo "RESULT: PASS"
else
    echo "RESULT: FAIL"
fi

# ============ PASS-TO-PASS (15%): Verify normal routing still works ============
# [repo_tests] (0.15): TokenChoiceTopKRouter forward produces correct output shape
echo ""
echo "[P2P] Verifying router forward compatibility..."
python3 << 'PYEOF'
import sys
import os

os.environ['PYTHONWARNINGS'] = 'ignore'

TARGET_DIR = "/workspace/AReaL"
sys.path.insert(0, TARGET_DIR)

try:
    import torch
    from areal.experimental.models.archon.moe.router import TokenChoiceTopKRouter

    # Create router with standard config
    router = TokenChoiceTopKRouter(
        dim=64,
        num_experts=8,
        top_k=2,
        score_func="sigmoid"
    )

    # Test forward pass
    x = torch.randn(16, 64)
    top_scores, selected_indices, token_counts = router(x)

    # Verify outputs
    assert top_scores.shape == (16, 2), f"top_scores shape wrong: {top_scores.shape}"
    assert selected_indices.shape == (16, 2), f"selected_indices shape wrong: {selected_indices.shape}"
    assert token_counts.shape == (8,), f"token_counts shape wrong: {token_counts.shape}"

    # Verify scores are valid (not all zeros, not NaN)
    assert not torch.isnan(top_scores).any(), "top_scores contains NaN"
    assert (top_scores >= 0).all(), "top_scores contains negative values"

    print("PASS: TokenChoiceTopKRouter forward produces valid routing output")
except ImportError as e:
    print(f"FAIL: Import error: {e}")
    sys.exit(1)
except AssertionError as e:
    print(f"FAIL: {e}")
    sys.exit(1)
except Exception as e:
    print(f"FAIL: {e}")
    sys.exit(1)
PYEOF
if [ $? -eq 0 ]; then
    p2p_compute_PASS=1
    echo "RESULT: PASS"
else
    echo "RESULT: FAIL"
fi

# ============ REGRESSION (10%): Verify code quality ============
# [agent_config] (0.05): No wildcard imports - AGENTS.md @ commit
echo ""
echo "[REGRESSION] Code quality checks..."

regression_score=0

# Check no wildcard imports
grep -q "from .* import \*" "$TARGET" 2>/dev/null
if [ $? -ne 0 ]; then
    regression_score=$(python3 -c "print($regression_score + 0.05)")
    echo "  - No wildcard imports: PASS"
else
    echo "  - No wildcard imports: FAIL"
fi

# Check no bare print
grep -qE "^\s*print\(" "$TARGET" 2>/dev/null
if [ $? -ne 0 ]; then
    regression_score=$(python3 -c "print($regression_score + 0.05)")
    echo "  - No bare print(): PASS"
else
    echo "  - No bare print(): FAIL"
fi

if [ "$(python3 -c "print(1 if $regression_score >= 0.05 else 0)")" = "1" ]; then
    regression_PASS=1
fi

# ============ Calculate Final Score ============
echo ""
echo "=== FINAL SCORE ==="

TOTAL=$(python3 -c "
gate = $gate_PASS
f2p1 = $f2p_hook_fire_PASS
f2p2 = $f2p_state_dict_PASS
f2p3 = $f2p_forward_call_PASS
p2p = $p2p_compute_PASS
reg = $regression_PASS

weights = {
    'f2p_hook_fire': 0.35,
    'f2p_state_dict': 0.20,
    'f2p_forward_call': 0.20,
    'p2p_compute': 0.15,
    'regression': 0.10
}

if gate == 0:
    print('0.00')
else:
    score = (
        weights['f2p_hook_fire'] * f2p1 +
        weights['f2p_state_dict'] * f2p2 +
        weights['f2p_forward_call'] * f2p3 +
        weights['p2p_compute'] * p2p +
        weights['regression'] * reg
    )
    print(f'{score:.2f}')
")

echo "  Gate (syntax): $gate_PASS"
echo "  F2P-1 (hook firing): $f2p_hook_fire_PASS (0.35)"
echo "  F2P-2 (state dict): $f2p_state_dict_PASS (0.20)"
echo "  F2P-3 (forward behavior): $f2p_forward_call_PASS (0.20)"
echo "  P2P (compute): $p2p_compute_PASS (0.15)"
echo "  Regression (quality): $regression_PASS (0.10)"
echo "  TOTAL: $TOTAL"

echo "$TOTAL" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
