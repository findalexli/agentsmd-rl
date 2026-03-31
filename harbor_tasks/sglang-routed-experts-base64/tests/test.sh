#!/usr/bin/env bash
# Verifier for sglang-routed-experts-base64
# Task: fix encode_image_base64 for torch.Tensor, move base64 encoding
#        from detokenizer to tokenizer manager, reduce numa log noise
# Files: python/sglang/utils.py, detokenizer_manager.py, tokenizer_manager.py, numa_utils.py

set +e

REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

REPO="/workspace/sglang"
UTILS="$REPO/python/sglang/utils.py"
DETOK="$REPO/python/sglang/srt/managers/detokenizer_manager.py"
TOKMGR="$REPO/python/sglang/srt/managers/tokenizer_manager.py"
NUMA="$REPO/python/sglang/srt/utils/numa_utils.py"

echo "=== sglang routed-experts base64 verifier ==="

# ── Helper: create a Python loader that imports sglang.utils directly ────
# sglang/__init__.py pulls in aiohttp, openai, transformers, CUDA, etc.
# We mock only the unavailable module-level deps so encode_image_base64 works.
cat > /tmp/_load_sglang_utils.py << 'LOADEOF'
import sys, types, importlib.util

# Mock heavy deps that utils.py imports at module level
for mod_name in [
    "requests", "IPython", "IPython.display",
    "pydantic", "sglang.srt", "sglang.srt.environ",
]:
    if mod_name not in sys.modules:
        m = types.ModuleType(mod_name)
        sys.modules[mod_name] = m

# IPython.display needs HTML and display attrs
sys.modules["IPython.display"].HTML = lambda *a, **k: None
sys.modules["IPython.display"].display = lambda *a, **k: None

# pydantic needs BaseModel
class _FakeBaseModel:
    def __init_subclass__(cls, **kwargs): pass
sys.modules["pydantic"].BaseModel = _FakeBaseModel

# sglang.srt.environ needs envs
sys.modules["sglang.srt.environ"].envs = types.SimpleNamespace()

# Ensure sglang package exists in sys.modules but with empty __init__
if "sglang" not in sys.modules:
    sys.modules["sglang"] = types.ModuleType("sglang")
    sys.modules["sglang"].__path__ = ["/workspace/sglang/python/sglang"]

# Now load sglang.utils directly from file
spec = importlib.util.spec_from_file_location(
    "sglang.utils", "/workspace/sglang/python/sglang/utils.py"
)
sglang_utils = importlib.util.module_from_spec(spec)
sys.modules["sglang.utils"] = sglang_utils
spec.loader.exec_module(sglang_utils)

encode_image_base64 = sglang_utils.encode_image_base64
LOADEOF

# ── GATE: Python syntax validity ─────────────────────────────────────────
echo ""
echo "GATE: Python syntax validity"
GATE_OK=1
for f in "$UTILS" "$DETOK" "$TOKMGR" "$NUMA"; do
    python3 -c "
import ast, sys
try:
    with open('$f') as fh:
        ast.parse(fh.read())
    print(f'  OK: {\"$f\".split(\"/\")[-1]}')
except SyntaxError as e:
    print(f'  FAIL: {\"$f\".split(\"/\")[-1]}: {e}')
    sys.exit(1)
" || GATE_OK=0
done
if [ "$GATE_OK" -eq 0 ]; then
    echo "GATE FAIL: syntax error — aborting with score 0"
    echo "0.0000" > "$REWARD_FILE"
    exit 0
fi
echo "GATE PASS"

# Weights
W_TENSOR_NOCRASH=0.25
W_TENSOR_VALID_PNG=0.20
W_TENSOR_PIXELS=0.15
W_P2P_BYTES=0.10
W_DETOK_REMOVED=0.10
W_TOKMGR_BASE64=0.10
W_ANTISTUB=0.05
W_NUMA_DEBUG=0.05

SCORE="0.0"

# ── TEST 1 (PRIMARY): behavioral — encode_image_base64 handles torch.Tensor ──
# [pr_diff] (0.25): GPU-decoded image tensor must not crash encode_image_base64
echo ""
echo "TEST 1: behavioral — encode_image_base64 accepts torch.Tensor (weight=$W_TENSOR_NOCRASH)"
T1=$(python3 << 'PYEOF'
import sys
exec(open("/tmp/_load_sglang_utils.py").read())

import torch

# Create a small RGB image tensor in CHW format (3, 8, 8), uint8
tensor = torch.randint(0, 256, (3, 8, 8), dtype=torch.uint8)

try:
    result = encode_image_base64(tensor)
except Exception as e:
    print(f"FAIL: encode_image_base64(torch.Tensor) raised {type(e).__name__}: {e}")
    sys.exit(1)

if not isinstance(result, str):
    print(f"FAIL: expected str, got {type(result)}")
    sys.exit(1)

if len(result) < 10:
    print(f"FAIL: result too short ({len(result)} chars) — likely empty/broken")
    sys.exit(1)

print("PASS: encode_image_base64 accepts torch.Tensor without crashing")
sys.exit(0)
PYEOF
)
echo "$T1"
if echo "$T1" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_TENSOR_NOCRASH)")
fi

# ── TEST 2 (PRIMARY): behavioral — tensor result is valid base64-encoded PNG ──
# [pr_diff] (0.20): base64 output must decode to a valid PNG image
echo ""
echo "TEST 2: behavioral — tensor encodes to valid PNG via base64 (weight=$W_TENSOR_VALID_PNG)"
T2=$(python3 << 'PYEOF'
import sys, base64, io
exec(open("/tmp/_load_sglang_utils.py").read())

import torch
from PIL import Image

# 3-channel, 16x16 image
tensor = torch.randint(0, 256, (3, 16, 16), dtype=torch.uint8)
result = encode_image_base64(tensor)

try:
    raw = base64.b64decode(result)
except Exception as e:
    print(f"FAIL: base64 decode error: {e}")
    sys.exit(1)

# Check PNG magic bytes
if raw[:4] != b'\x89PNG':
    print(f"FAIL: decoded bytes are not PNG (magic: {raw[:4]!r})")
    sys.exit(1)

# Verify PIL can open it and dimensions are correct
try:
    img = Image.open(io.BytesIO(raw))
    img.load()
except Exception as e:
    print(f"FAIL: PIL cannot open decoded PNG: {e}")
    sys.exit(1)

if img.size != (16, 16):
    print(f"FAIL: expected 16x16 image, got {img.size}")
    sys.exit(1)

print("PASS: tensor produces valid 16x16 PNG via base64")
sys.exit(0)
PYEOF
)
echo "$T2"
if echo "$T2" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_TENSOR_VALID_PNG)")
fi

# ── TEST 3 (PRIMARY): behavioral — tensor pixel values are preserved ──
# [pr_diff] (0.15): CHW tensor pixels must round-trip correctly through encoding
echo ""
echo "TEST 3: behavioral — tensor pixel values preserved in round-trip (weight=$W_TENSOR_PIXELS)"
T3=$(python3 << 'PYEOF'
import sys, base64, io
exec(open("/tmp/_load_sglang_utils.py").read())

import torch
import numpy as np
from PIL import Image

# Create a known-value tensor: solid red 4x4 image (CHW format)
tensor = torch.zeros(3, 4, 4, dtype=torch.uint8)
tensor[0, :, :] = 255  # R channel = 255

result = encode_image_base64(tensor)
raw = base64.b64decode(result)
img = Image.open(io.BytesIO(raw)).convert("RGB")
arr = np.array(img)

# Check the top-left pixel is red
r, g, b = arr[0, 0]
if r != 255 or g != 0 or b != 0:
    print(f"FAIL: expected (255, 0, 0), got ({r}, {g}, {b})")
    sys.exit(1)

# Check all pixels are red
if not (arr[:, :, 0] == 255).all():
    print("FAIL: not all R channel values are 255")
    sys.exit(1)
if not (arr[:, :, 1] == 0).all() or not (arr[:, :, 2] == 0).all():
    print("FAIL: G or B channels are not 0")
    sys.exit(1)

print("PASS: tensor pixel values correctly preserved through encoding")
sys.exit(0)
PYEOF
)
echo "$T3"
if echo "$T3" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_TENSOR_PIXELS)")
fi

# ── TEST 4: pass-to-pass — encode_image_base64 still works with bytes ──
# [pr_diff] (0.10): Existing bytes input path must not regress
echo ""
echo "TEST 4: pass-to-pass — encode_image_base64 with bytes input (weight=$W_P2P_BYTES)"
T4=$(python3 << 'PYEOF'
import sys, base64
exec(open("/tmp/_load_sglang_utils.py").read())

# Test with raw bytes (the original supported path)
test_bytes = b'\x89PNG\r\n\x1a\n' + b'\x00' * 100
result = encode_image_base64(test_bytes)

# Verify round-trip
decoded = base64.b64decode(result)
if decoded != test_bytes:
    print("FAIL: bytes round-trip failed")
    sys.exit(1)

print("PASS: encode_image_base64 with bytes input still works")
sys.exit(0)
PYEOF
)
echo "$T4"
if echo "$T4" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_P2P_BYTES)")
fi

# ── TEST 5: structural — _extract_routed_experts removed from detokenizer ──
# [pr_diff] (0.10): Detokenizer must no longer base64-encode routed experts
# WHY AST: detokenizer_manager imports the full sglang serving stack (zmq, fastapi,
# uvloop, sglang.srt internals) and cannot be imported without the complete runtime.
echo ""
echo "TEST 5: structural — detokenizer no longer has _extract_routed_experts (weight=$W_DETOK_REMOVED)"
T5=$(python3 << 'PYEOF'
import ast, sys

with open("/workspace/sglang/python/sglang/srt/managers/detokenizer_manager.py") as f:
    source = f.read()

tree = ast.parse(source)

# Sub-check A: _extract_routed_experts must be removed
for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        if node.name == "_extract_routed_experts":
            print("FAIL: _extract_routed_experts method still exists in detokenizer")
            sys.exit(1)

# Sub-check B: pybase64 must not be imported at module level
for node in ast.iter_child_nodes(tree):
    if isinstance(node, ast.Import):
        for alias in node.names:
            if alias.name == "pybase64":
                print("FAIL: detokenizer still imports pybase64 at module level")
                sys.exit(1)
    elif isinstance(node, ast.ImportFrom):
        if node.module and "pybase64" in node.module:
            print("FAIL: detokenizer still imports from pybase64")
            sys.exit(1)

# Sub-check C: routed_experts must be passed through in BatchStrOutput construction
# Accept ANY form: direct attr, local var, dict unpacking, etc.
# Just verify that BatchStrOutput is called with a routed_experts keyword somewhere.
found_routed_kw = False
for node in ast.walk(tree):
    if isinstance(node, ast.Call):
        # Check if this is a call to BatchStrOutput (Name or Attribute)
        is_batch_str = False
        if isinstance(node.func, ast.Name) and node.func.id == "BatchStrOutput":
            is_batch_str = True
        elif isinstance(node.func, ast.Attribute) and node.func.attr == "BatchStrOutput":
            is_batch_str = True
        if is_batch_str:
            for kw in node.keywords:
                if kw.arg == "routed_experts":
                    found_routed_kw = True

if not found_routed_kw:
    print("FAIL: BatchStrOutput not constructed with routed_experts keyword")
    sys.exit(1)

print("PASS: _extract_routed_experts removed, pybase64 removed, routed_experts passed through")
sys.exit(0)
PYEOF
)
echo "$T5"
if echo "$T5" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_DETOK_REMOVED)")
fi

# ── TEST 6: structural — tokenizer_manager has base64 encoding for routed_experts ──
# [pr_diff] (0.10): Tokenizer manager must now base64-encode routed_experts tensors
# WHY AST: tokenizer_manager imports fastapi, uvloop, zmq.asyncio and the full
# sglang runtime — cannot be imported in a test container without the serving stack.
echo ""
echo "TEST 6: structural — tokenizer_manager does base64 encoding (weight=$W_TOKMGR_BASE64)"
T6=$(python3 << 'PYEOF'
import ast, sys

with open("/workspace/sglang/python/sglang/srt/managers/tokenizer_manager.py") as f:
    source = f.read()

tree = ast.parse(source)

# Sub-check A: pybase64 is imported (import pybase64 or from pybase64 import ...)
has_pybase64 = False
for node in ast.walk(tree):
    if isinstance(node, ast.Import):
        for alias in node.names:
            if alias.name == "pybase64":
                has_pybase64 = True
    elif isinstance(node, ast.ImportFrom):
        if node.module and "pybase64" in node.module:
            has_pybase64 = True

if not has_pybase64:
    print("FAIL: tokenizer_manager does not import pybase64")
    sys.exit(1)

# Sub-check B: b64encode is called as a function/method (AST Call node, not string search)
has_b64encode_call = False
for node in ast.walk(tree):
    if isinstance(node, ast.Call):
        # Direct call: b64encode(...)
        if isinstance(node.func, ast.Name) and node.func.id == "b64encode":
            has_b64encode_call = True
        # Attribute call: pybase64.b64encode(...) or similar
        elif isinstance(node.func, ast.Attribute) and node.func.attr == "b64encode":
            has_b64encode_call = True

if not has_b64encode_call:
    print("FAIL: tokenizer_manager has no b64encode() call in AST")
    sys.exit(1)

# Sub-check C: routed_experts None guard exists (any comparison with None involving
# a name containing 'routed' or 'expert', or an if-statement guarding routed_experts)
has_none_guard = False
for node in ast.walk(tree):
    if isinstance(node, ast.Compare):
        # Check for: <something> is not None / <something> is None
        all_names = []
        if isinstance(node.left, ast.Name):
            all_names.append(node.left.id)
        elif isinstance(node.left, ast.Attribute):
            all_names.append(node.left.attr)
        for comp in node.comparators:
            if isinstance(comp, ast.Constant) and comp.value is None:
                for name in all_names:
                    if "routed" in name.lower() or "expert" in name.lower():
                        has_none_guard = True

    # Also accept: if routed_experts_var: (truthy check)
    if isinstance(node, ast.If):
        test = node.test
        if isinstance(test, ast.Name) and ("routed" in test.id.lower() or "expert" in test.id.lower()):
            has_none_guard = True

if not has_none_guard:
    print("FAIL: tokenizer_manager has no None guard for routed_experts")
    sys.exit(1)

print("PASS: tokenizer_manager imports pybase64, calls b64encode(), and guards routed_experts for None")
sys.exit(0)
PYEOF
)
echo "$T6"
if echo "$T6" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_TOKMGR_BASE64)")
fi

# ── TEST 7: anti-stub — all files retain expected content ──
# (0.05): Files must not be stubbed out
echo ""
echo "TEST 7: anti-stub — files retain expected symbols and size (weight=$W_ANTISTUB)"
T7=$(python3 << 'PYEOF'
import sys

checks = [
    ("/workspace/sglang/python/sglang/utils.py",
     ["encode_image_base64", "pybase64", "BytesIO"],
     150),
    ("/workspace/sglang/python/sglang/srt/managers/detokenizer_manager.py",
     ["DetokenizerManager", "handle_batch_token_id_out", "BatchStrOutput", "BatchTokenIDOutput"],
     250),
    ("/workspace/sglang/python/sglang/srt/managers/tokenizer_manager.py",
     ["TokenizerManager", "_handle_batch_output", "meta_info"],
     500),
    ("/workspace/sglang/python/sglang/srt/utils/numa_utils.py",
     ["numactl", "_is_numa_available", "logger"],
     50),
]

for path, required_symbols, min_lines in checks:
    with open(path) as f:
        source = f.read()
    lines = len(source.splitlines())
    if lines < min_lines:
        print(f"FAIL: {path.split('/')[-1]} has only {lines} lines (min {min_lines}) — stubbed?")
        sys.exit(1)
    missing = [s for s in required_symbols if s not in source]
    if missing:
        print(f"FAIL: {path.split('/')[-1]} missing symbols: {missing}")
        sys.exit(1)

print("PASS: all files retain expected symbols and size")
sys.exit(0)
PYEOF
)
echo "$T7"
if echo "$T7" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_ANTISTUB)")
fi

# ── TEST 8: behavioral — numa_utils uses debug not warning for numactl message ──
# [pr_diff] (0.05): numactl-not-found message should be debug, not warning
# WHY not fully behavioral: _is_numa_available depends on shutil.which + system NUMA
# state, but we CAN check the AST for log level at the numactl message site.
echo ""
echo "TEST 8: structural — numa_utils uses logger.debug for numactl message (weight=$W_NUMA_DEBUG)"
T8=$(python3 << 'PYEOF'
import ast, sys

with open("/workspace/sglang/python/sglang/srt/utils/numa_utils.py") as f:
    source = f.read()

tree = ast.parse(source)

# Walk all Call nodes looking for logger.warning calls that mention numactl
# If ANY logger.warning call has a string arg containing "numactl" → FAIL
for node in ast.walk(tree):
    if isinstance(node, ast.Call):
        if isinstance(node.func, ast.Attribute):
            if node.func.attr == "warning" and isinstance(node.func.value, ast.Name) and node.func.value.id == "logger":
                # Check if any argument mentions numactl
                for arg in node.args:
                    if isinstance(arg, ast.Constant) and isinstance(arg.value, str) and "numactl" in arg.value.lower():
                        print("FAIL: logger.warning still used for numactl message")
                        sys.exit(1)
                    # Also check f-strings
                    if isinstance(arg, ast.JoinedStr):
                        for val in arg.values:
                            if isinstance(val, ast.Constant) and isinstance(val.value, str) and "numactl" in val.value.lower():
                                print("FAIL: logger.warning still used for numactl message (f-string)")
                                sys.exit(1)

# Also verify logger.debug is used for numactl (positive check)
found_debug_numactl = False
for node in ast.walk(tree):
    if isinstance(node, ast.Call):
        if isinstance(node.func, ast.Attribute):
            if node.func.attr == "debug" and isinstance(node.func.value, ast.Name) and node.func.value.id == "logger":
                for arg in node.args:
                    if isinstance(arg, ast.Constant) and isinstance(arg.value, str) and "numactl" in arg.value.lower():
                        found_debug_numactl = True
                    if isinstance(arg, ast.JoinedStr):
                        for val in arg.values:
                            if isinstance(val, ast.Constant) and isinstance(val.value, str) and "numactl" in val.value.lower():
                                found_debug_numactl = True

if not found_debug_numactl:
    print("FAIL: no logger.debug call found mentioning numactl — message may have been removed")
    sys.exit(1)

print("PASS: numactl message uses logger.debug, not logger.warning")
sys.exit(0)
PYEOF
)
echo "$T8"
if echo "$T8" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_NUMA_DEBUG)")
fi

# ── Final score ──────────────────────────────────────────────────────────
echo ""
echo "================================"
REWARD=$(python3 -c "print('{:.4f}'.format(min($SCORE, 1.0)))")
echo "Reward: $REWARD"
echo "================================"
echo "$REWARD" > "$REWARD_FILE"

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
