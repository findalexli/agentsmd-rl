#!/usr/bin/env bash
# Grading: prime-rl-qwen35-vlm-text-dispatch
# Bug: single is_vlm flag conflates architecture detection with training config
# Fix: add is_vlm_architecture() to vlm.py, split flag in model.py
set +e

TASK_DIR="$(cd "$(dirname "$0")/.." && pwd)"
REPO_ROOT="${REPO_ROOT:-/repo}"
cd "$REPO_ROOT" || { echo "0.0" > "/logs/verifier/reward.txt"; exit 0; }

MODEL_PY="src/prime_rl/trainer/model.py"
VLM_PY="src/prime_rl/utils/vlm.py"
REWARD=0

add_score() {
    REWARD=$(python3 -c "print(round($REWARD + $1, 4))")
}

########################################
# GATE: Syntax check
########################################
echo "=== GATE: Syntax check ==="
for f in "$VLM_PY" "$MODEL_PY"; do
    python3 -c "compile(open('$f').read(), '$f', 'exec')" 2>/dev/null
    if [ $? -ne 0 ]; then
        echo "FAIL: $f has syntax errors"
        echo "0.0" > "/logs/verifier/reward.txt"
        exit 0
    fi
done
echo "PASS: syntax OK"

########################################
# [pr_diff] (0.35): F2P — is_vlm_architecture classifies VLM vs non-VLM configs
# Behavioral: calls the function directly with mock configs.
# Fails on buggy code because is_vlm_architecture does not exist.
########################################
echo "=== TEST 1: is_vlm_architecture behavior ==="
python3 << 'PYEOF'
import importlib.util, sys

spec = importlib.util.spec_from_file_location("vlm", "src/prime_rl/utils/vlm.py")
vlm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vlm)

assert hasattr(vlm, "is_vlm_architecture"), "is_vlm_architecture not found in vlm.py"
fn = vlm.is_vlm_architecture

class MC:
    def __init__(self, mt):
        self.model_type = mt

# VLM architectures registered in VLM_REGISTRY must return True
for mt in ["qwen3_5_moe", "qwen3_5", "qwen3_vl"]:
    result = fn(MC(mt))
    assert result is True, f"{mt} should be detected as VLM, got {result}"

# Non-VLM model types must return False
for mt in ["llama", "gpt2", "mistral", "gemma", "phi"]:
    result = fn(MC(mt))
    assert result is False, f"{mt} should NOT be detected as VLM, got {result}"

# Edge cases: None, empty string, unknown
assert fn(MC(None)) is False, "None model_type should return False"
assert fn(MC("")) is False, "empty model_type should return False"
assert fn(MC("nonexistent_model_999")) is False, "unknown type should return False"

# Return type must be bool
assert isinstance(fn(MC("qwen3_5_moe")), bool), "should return bool"
assert isinstance(fn(MC("llama")), bool), "should return bool"

print("PASS: is_vlm_architecture correctly classifies VLM vs non-VLM configs")
PYEOF
if [ $? -eq 0 ]; then add_score 0.35; else echo "FAIL: is_vlm_architecture behavior"; fi

########################################
# [pr_diff] (0.15): P2P — _get_model_info_from_config works correctly
# Behavioral: calls the existing internal function to verify VLM registry
# lookups still work after the change. This function exists in buggy code.
########################################
echo "=== TEST 2: _get_model_info_from_config behavior ==="
python3 << 'PYEOF'
import importlib.util, sys

spec = importlib.util.spec_from_file_location("vlm", "src/prime_rl/utils/vlm.py")
vlm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vlm)

assert hasattr(vlm, "_get_model_info_from_config"), \
    "_get_model_info_from_config not found"
fn = vlm._get_model_info_from_config

class MC:
    def __init__(self, mt):
        self.model_type = mt

# VLM types should return a non-None ModelInfo
for mt in ["qwen3_5_moe", "qwen3_5", "qwen3_vl"]:
    info = fn(MC(mt))
    assert info is not None, f"{mt} should have model info, got None"
    assert hasattr(info, "vision_encoder_attr"), f"{mt} info missing vision_encoder_attr"
    assert hasattr(info, "language_model_attr"), f"{mt} info missing language_model_attr"

# Non-VLM types should return None
for mt in ["llama", "gpt2", "mistral"]:
    info = fn(MC(mt))
    assert info is None, f"{mt} should return None, got {info}"

print("PASS: _get_model_info_from_config works correctly")
PYEOF
if [ $? -eq 0 ]; then add_score 0.15; else echo "FAIL: _get_model_info_from_config"; fi

########################################
# [pr_diff] (0.10): P2P — VLM_REGISTRY has expected entries with correct attrs
# Behavioral: loads module and inspects the registry dict.
########################################
echo "=== TEST 3: VLM_REGISTRY intact ==="
python3 << 'PYEOF'
import importlib.util

spec = importlib.util.spec_from_file_location("vlm", "src/prime_rl/utils/vlm.py")
vlm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vlm)

reg = vlm.VLM_REGISTRY
required = ["qwen3_vl", "qwen3_5", "qwen3_5_moe"]
for key in required:
    assert key in reg, f"{key} missing from VLM_REGISTRY"
    info = reg[key]
    assert hasattr(info, "vision_encoder_attr"), f"{key} missing vision_encoder_attr"
    assert hasattr(info, "language_model_attr"), f"{key} missing language_model_attr"
    # Attrs should be non-empty strings
    assert isinstance(info.vision_encoder_attr, str) and info.vision_encoder_attr, \
        f"{key} vision_encoder_attr invalid"
    assert isinstance(info.language_model_attr, str) and info.language_model_attr, \
        f"{key} language_model_attr invalid"

print("PASS: VLM_REGISTRY has all expected entries")
PYEOF
if [ $? -eq 0 ]; then add_score 0.10; else echo "FAIL: VLM_REGISTRY"; fi

########################################
# [pr_diff] (0.15): F2P — get_model calls is_vlm_architecture
# AST check. Justification: get_model() requires GPU, model weights, FSDP,
# and full prime_rl training stack — cannot be called on CPU.
# Non-narrow: checks for Call node, not specific variable names.
########################################
echo "=== TEST 4: get_model calls is_vlm_architecture ==="
python3 << 'PYEOF'
import ast, sys

source = open("src/prime_rl/trainer/model.py").read()
tree = ast.parse(source)

# Find get_model function
get_model = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "get_model":
        get_model = node
        break

assert get_model is not None, "get_model function not found in model.py"

# Check that is_vlm_architecture is CALLED (not just referenced) inside get_model
# Accept: is_vlm_architecture(x), vlm.is_vlm_architecture(x), etc.
calls_fn = False
for node in ast.walk(get_model):
    if isinstance(node, ast.Call):
        func = node.func
        name = None
        if isinstance(func, ast.Name):
            name = func.id
        elif isinstance(func, ast.Attribute):
            name = func.attr
        if name == "is_vlm_architecture":
            calls_fn = True
            break

assert calls_fn, "get_model does not call is_vlm_architecture — arch detection missing"

# The function body should be substantive (not a stub get_model)
body_stmts = [n for n in ast.walk(get_model) if isinstance(n, ast.stmt)]
assert len(body_stmts) > 10, "get_model looks too short to be real"

print("PASS: get_model calls is_vlm_architecture for arch detection")
PYEOF
if [ $? -eq 0 ]; then add_score 0.15; else echo "FAIL: get_model arch detection"; fi

########################################
# [pr_diff] (0.10): F2P — model.py imports is_vlm_architecture
# AST check: looks for ImportFrom node with is_vlm_architecture.
# Accepts any import path (from prime_rl.utils.vlm, from .utils.vlm, etc.)
########################################
echo "=== TEST 5: model.py imports is_vlm_architecture ==="
python3 << 'PYEOF'
import ast

source = open("src/prime_rl/trainer/model.py").read()
tree = ast.parse(source)

# Check all ImportFrom nodes for is_vlm_architecture
found = False
for node in ast.walk(tree):
    if isinstance(node, (ast.ImportFrom, ast.Import)):
        if isinstance(node, ast.ImportFrom):
            for alias in node.names:
                if alias.name == "is_vlm_architecture":
                    found = True
                    break

assert found, "model.py does not import is_vlm_architecture"
print("PASS: model.py imports is_vlm_architecture")
PYEOF
if [ $? -eq 0 ]; then add_score 0.10; else echo "FAIL: model.py import"; fi

########################################
# [pr_diff] (0.05): Anti-stub: is_vlm_architecture has real implementation
# AST check: body must reference VLM_REGISTRY or _get_model_info_from_config
########################################
echo "=== TEST 6: Anti-stub check ==="
python3 << 'PYEOF'
import ast

source = open("src/prime_rl/utils/vlm.py").read()
tree = ast.parse(source)

found = False
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "is_vlm_architecture":
        found = True
        # Filter out docstrings
        stmts = [n for n in node.body
                 if not (isinstance(n, ast.Expr) and isinstance(n.value, (ast.Constant, ast.Str)))]
        assert len(stmts) >= 1, "is_vlm_architecture is a stub (only docstring/pass)"
        # Should use registry-based lookup, not hardcoded list
        func_src = "\n".join(source.splitlines()[node.lineno - 1:node.end_lineno])
        assert "_get_model_info_from_config" in func_src or "VLM_REGISTRY" in func_src, \
            "is_vlm_architecture should use registry lookup, not hardcoded values"
        break

assert found, "is_vlm_architecture function not found"
print("PASS: is_vlm_architecture has real implementation")
PYEOF
if [ $? -eq 0 ]; then add_score 0.05; else echo "FAIL: anti-stub"; fi

########################################
# [agent_config] (0.05): No bare except — AGENTS.md:5 @ ecd08092
########################################
echo "=== TEST 7: No bare except blocks ==="
python3 << 'PYEOF'
import ast

for filepath in ["src/prime_rl/utils/vlm.py", "src/prime_rl/trainer/model.py"]:
    source = open(filepath).read()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Try):
            for handler in node.handlers:
                if handler.type is None:
                    raise AssertionError(
                        f"{filepath}: bare except at line {node.lineno} violates AGENTS.md:5"
                    )

print("PASS: no bare except blocks")
PYEOF
if [ $? -eq 0 ]; then add_score 0.05; else echo "FAIL: bare except"; fi

########################################
# [pr_diff] (0.05): freeze_vision_encoder not guarded by architecture detection
# AST check. Justification: setup_fsdp/get_model require GPU to call.
# Non-narrow: checks that is_vlm_architecture is NOT called in the
# freeze context, rather than requiring specific variable names.
########################################
echo "=== TEST 8: freeze_vision_encoder not tied to arch detection ==="
python3 << 'PYEOF'
import ast

source = open("src/prime_rl/trainer/model.py").read()
lines = source.splitlines()

# Find all calls to freeze_vision_encoder
for node in ast.walk(ast.parse(source)):
    if isinstance(node, ast.Call):
        call_name = None
        if isinstance(node.func, ast.Name):
            call_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            call_name = node.func.attr
        if call_name == "freeze_vision_encoder":
            # Check the 5 lines before the call for the guard condition
            ctx_start = max(0, node.lineno - 6)
            ctx_end = node.lineno
            context = "\n".join(lines[ctx_start:ctx_end])
            # The guard should NOT directly call is_vlm_architecture
            # (that would mean freeze is tied to architecture, not training config)
            if "is_vlm_architecture" in context:
                raise AssertionError(
                    "freeze_vision_encoder is guarded by architecture detection — "
                    "should be guarded by training config (config.vlm)"
                )

print("PASS: freeze_vision_encoder not tied to architecture detection")
PYEOF
if [ $? -eq 0 ]; then add_score 0.05; else echo "FAIL: freeze guard"; fi

########################################
# Final score
########################################
echo ""
echo "=== FINAL SCORE: $REWARD ==="
echo "$REWARD" > "/logs/verifier/reward.txt"

python3 -c "
import json
score = float('$REWARD')
json.dump({
    'reward': score,
    'behavioral': 0.60,
    'regression': 0.25,
    'config': 0.05,
    'style_rubric': 0.10,
    'max_score': 1.0,
}, open('/logs/verifier/reward.json', 'w'), indent=2)
"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
