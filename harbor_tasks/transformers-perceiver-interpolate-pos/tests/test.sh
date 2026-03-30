#!/usr/bin/env bash
# Verifier for transformers-perceiver-interpolate-pos
# Bug: interpolate_pos_encoding passes source dims instead of target dims to nn.functional.interpolate
# File: src/transformers/models/perceiver/modeling_perceiver.py

set +e

REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

TARGET="/workspace/transformers/src/transformers/models/perceiver/modeling_perceiver.py"

echo "=== transformers-perceiver-interpolate-pos verifier ==="

# ── GATE: Python syntax validity ─────────────────────────────────────────
echo ""
echo "GATE: Python syntax validity"
python3 << 'PYEOF'
import ast, sys
try:
    with open("/workspace/transformers/src/transformers/models/perceiver/modeling_perceiver.py") as f:
        ast.parse(f.read())
    print("  OK: file parses successfully")
    sys.exit(0)
except SyntaxError as e:
    print(f"  FAIL: SyntaxError: {e}")
    sys.exit(1)
PYEOF
if [ $? -ne 0 ]; then
    echo "GATE FAIL: syntax error — aborting with score 0"
    echo "0.0000" > "$REWARD_FILE"
    exit 0
fi
echo "GATE PASS"

# Weights
W_BEHAV_INTERPOLATE_TARGET=0.29
W_BEHAV_EXEC_MOCK=0.24
W_BEHAV_AST_CHECK=0.14
W_PASSTOPASS=0.14
W_ANTISTUB=0.14
W_CONFIG_RUFF=0.05

SCORE="0.0"

# ── TEST 1 (PRIMARY): behavioral — interpolate uses target (height, width) not source ──
echo ""
echo "TEST 1: behavioral — interpolate uses target dimensions (weight=$W_BEHAV_INTERPOLATE_TARGET)"
T1=$(python3 << 'PYEOF'
import ast, sys

with open("/workspace/transformers/src/transformers/models/perceiver/modeling_perceiver.py") as f:
    source = f.read()

tree = ast.parse(source)

# Find PerceiverTrainablePositionEncoding class and its interpolate_pos_encoding method
found = False
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "PerceiverTrainablePositionEncoding":
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == "interpolate_pos_encoding":
                found = True
                lines = source.splitlines()
                func_lines = lines[item.lineno - 1:item.end_lineno]
                func_src = "\n".join(func_lines)

                # The buggy code has: size=(new_height, new_width)
                # The fix should have: size=(height, width)
                if "size=(new_height, new_width)" in func_src:
                    print("FAIL: still using source dimensions (new_height, new_width) — the bug")
                    sys.exit(1)

                if "size=(height, width)" in func_src:
                    print("PASS: interpolate uses target dimensions (height, width)")
                    sys.exit(0)

                # Check for alternative forms
                if "height, width" in func_src and "interpolate" in func_src:
                    print("PASS: interpolate appears to use target height/width")
                    sys.exit(0)

                print("FAIL: cannot determine interpolation target dimensions")
                sys.exit(1)
        break

if not found:
    print("FAIL: interpolate_pos_encoding method not found in PerceiverTrainablePositionEncoding")
    sys.exit(1)
PYEOF
)
echo "$T1"
if echo "$T1" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_BEHAV_INTERPOLATE_TARGET)")
fi

# ── TEST 2 (PRIMARY): behavioral — exec with mock verifies actual interpolation happens ──
echo ""
echo "TEST 2: behavioral — mock exec verifies interpolation changes shape (weight=$W_BEHAV_EXEC_MOCK)"
T2=$(python3 << 'PYEOF'
import ast, sys, textwrap, types

with open("/workspace/transformers/src/transformers/models/perceiver/modeling_perceiver.py") as f:
    source = f.read()

tree = ast.parse(source)

# Find interpolate_pos_encoding method
method_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "PerceiverTrainablePositionEncoding":
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == "interpolate_pos_encoding":
                method_node = item
                break
        break

if method_node is None:
    print("FAIL: interpolate_pos_encoding not found")
    sys.exit(1)

lines = source.splitlines()
func_lines = lines[method_node.lineno - 1:method_node.end_lineno]
func_src = textwrap.dedent("\n".join(func_lines))

# Remove 'self' parameter and replace self._num_channels references
# We'll simulate the function standalone
func_src = func_src.replace("self, ", "")
func_src = func_src.replace("self._num_channels", "_num_channels")

# Mock torch and nn
import numpy as np

class MockTensor:
    def __init__(self, data):
        self.data = np.array(data, dtype=np.float32)
        self._shape = self.data.shape

    @property
    def shape(self):
        return self._shape

    def reshape(self, *args):
        new_shape = args[0] if len(args) == 1 and isinstance(args[0], (list, tuple)) else args
        result = MockTensor.__new__(MockTensor)
        result.data = self.data.reshape(new_shape)
        result._shape = result.data.shape
        return result

    def permute(self, *args):
        axes = args[0] if len(args) == 1 and isinstance(args[0], (list, tuple)) else args
        result = MockTensor.__new__(MockTensor)
        result.data = np.transpose(self.data, axes)
        result._shape = result.data.shape
        return result

    def squeeze(self, dim):
        result = MockTensor.__new__(MockTensor)
        result.data = np.squeeze(self.data, axis=dim)
        result._shape = result.data.shape
        return result

# Track what size is passed to interpolate
interpolate_sizes = []

def mock_interpolate(x, size=None, mode=None, align_corners=None):
    interpolate_sizes.append(size)
    # Simulate interpolation: resize spatial dims
    if size is not None:
        h, w = size
        result = MockTensor.__new__(MockTensor)
        # x shape: (1, C, old_h, old_w) -> (1, C, h, w)
        result.data = np.ones((x.shape[0], x.shape[1], h, w), dtype=np.float32)
        result._shape = result.data.shape
        return result
    return x

def mock_torch_int(x):
    return int(x)

# Create mock nn module
nn_mock = types.ModuleType("nn")
nn_mock.functional = types.SimpleNamespace(interpolate=mock_interpolate)

# Create mock torch module
torch_mock = types.ModuleType("torch")
torch_mock.Tensor = MockTensor
jit_mock = types.SimpleNamespace(is_tracing=lambda: False)
torch_mock.jit = jit_mock

# Build exec namespace
exec_globals = {
    "torch": torch_mock,
    "nn": nn_mock,
    "torch_int": mock_torch_int,
    "_num_channels": 64,
    "__builtins__": __builtins__,
}

exec(func_src, exec_globals)

# Test: original grid is 4x4 (16 positions), target is 8x8
# position_embeddings shape: (16, 64) -- 4*4=16 positions, 64 channels
pos_emb = MockTensor(np.random.randn(16, 64).astype(np.float32))

try:
    result = exec_globals["interpolate_pos_encoding"](pos_emb, 8, 8)
except Exception as e:
    print(f"FAIL: interpolate_pos_encoding raised: {e}")
    sys.exit(1)

if not interpolate_sizes:
    print("FAIL: nn.functional.interpolate was never called")
    sys.exit(1)

actual_size = interpolate_sizes[0]
if actual_size == (8, 8):
    print("PASS: interpolate called with target dims (8, 8)")
    sys.exit(0)
elif actual_size == (4, 4):
    print("FAIL: interpolate called with source dims (4, 4) — the bug")
    sys.exit(1)
else:
    print(f"FAIL: interpolate called with unexpected size {actual_size}")
    sys.exit(1)
PYEOF
)
echo "$T2"
if echo "$T2" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_BEHAV_EXEC_MOCK)")
fi

# ── TEST 3: AST structural — interpolate call uses height/width params ──
echo ""
echo "TEST 3: AST structural — interpolate size= uses function params (weight=$W_BEHAV_AST_CHECK)"
T3=$(python3 << 'PYEOF'
import ast, sys

with open("/workspace/transformers/src/transformers/models/perceiver/modeling_perceiver.py") as f:
    source = f.read()

tree = ast.parse(source)

for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "PerceiverTrainablePositionEncoding":
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == "interpolate_pos_encoding":
                # Find nn.functional.interpolate call
                for subnode in ast.walk(item):
                    if isinstance(subnode, ast.Call):
                        # Check for keyword size=
                        for kw in subnode.keywords:
                            if kw.arg == "size":
                                # The value should be a tuple containing height and width (the params)
                                val = kw.value
                                if isinstance(val, ast.Tuple):
                                    names = []
                                    for elt in val.elts:
                                        if isinstance(elt, ast.Name):
                                            names.append(elt.id)
                                    if "height" in names and "width" in names:
                                        print("PASS: size= uses (height, width) parameters")
                                        sys.exit(0)
                                    elif "new_height" in names and "new_width" in names:
                                        print("FAIL: size= still uses (new_height, new_width) — the bug")
                                        sys.exit(1)

print("FAIL: could not find interpolate call with size= keyword")
sys.exit(1)
PYEOF
)
echo "$T3"
if echo "$T3" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_BEHAV_AST_CHECK)")
fi

# ── TEST 4: pass-to-pass — method signature and structure intact ──
echo ""
echo "TEST 4: pass-to-pass — method signature and structure intact (weight=$W_PASSTOPASS)"
T4=$(python3 << 'PYEOF'
import ast, sys

with open("/workspace/transformers/src/transformers/models/perceiver/modeling_perceiver.py") as f:
    source = f.read()

tree = ast.parse(source)

for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "PerceiverTrainablePositionEncoding":
        method_names = [m.name for m in node.body if isinstance(m, ast.FunctionDef)]
        if "interpolate_pos_encoding" not in method_names:
            print("FAIL: interpolate_pos_encoding method missing")
            sys.exit(1)
        if "forward" not in method_names:
            print("FAIL: forward method missing")
            sys.exit(1)
        if "__init__" not in method_names:
            print("FAIL: __init__ method missing")
            sys.exit(1)

        # Check interpolate_pos_encoding signature
        for m in node.body:
            if isinstance(m, ast.FunctionDef) and m.name == "interpolate_pos_encoding":
                args = [a.arg for a in m.args.args]
                if args != ["self", "position_embeddings", "height", "width"]:
                    print(f"FAIL: wrong signature: {args}")
                    sys.exit(1)
                break

        print("PASS: class structure and method signatures intact")
        sys.exit(0)

print("FAIL: PerceiverTrainablePositionEncoding class not found")
sys.exit(1)
PYEOF
)
echo "$T4"
if echo "$T4" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_PASSTOPASS)")
fi

# ── TEST 5: anti-stub — file retains original logic ──
echo ""
echo "TEST 5: anti-stub — file retains original logic (weight=$W_ANTISTUB)"
T5=$(python3 << 'PYEOF'
import sys

with open("/workspace/transformers/src/transformers/models/perceiver/modeling_perceiver.py") as f:
    source = f.read()

required = ["PerceiverTrainablePositionEncoding", "interpolate_pos_encoding",
            "nn.functional.interpolate", "bicubic", "position_embeddings",
            "PerceiverForImageClassificationLearned"]
missing = [r for r in required if r not in source]
if missing:
    print(f"FAIL: missing expected content: {missing}")
    sys.exit(1)

line_count = len(source.splitlines())
if line_count < 1000:
    print(f"FAIL: file has only {line_count} lines — looks like a stub")
    sys.exit(1)

print(f"PASS: file has {line_count} lines and contains all expected symbols")
sys.exit(0)
PYEOF
)
echo "$T5"
if echo "$T5" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_ANTISTUB)")
fi


# -- CONFIG-DERIVED: ruff format check on changed files (weight=$W_CONFIG_RUFF) --
# Config-derived test (0.05): "Changed files pass ruff format"
# Source: CLAUDE.md lines 5-10 @ commit c532659b8734b88d2bbaac2542c2a5a8b525f3f7
echo ""
echo "CONFIG: ruff format check (weight=$W_CONFIG_RUFF)"
T_RUFF=$(python3 << 'PYRUFF'
import subprocess, sys
files = ['/workspace/transformers/src/transformers/models/perceiver/modeling_perceiver.py']
all_ok = True
for f in files:
    result = subprocess.run(["ruff", "check", "--select", "I", f], capture_output=True, text=True)
    if result.returncode != 0:
        all_ok = False
        print(f"FAIL: ruff check failed on {f}")
if all_ok:
    print("PASS: all changed files pass ruff import sort check")
    sys.exit(0)
else:
    sys.exit(1)
PYRUFF
)
echo "$T_RUFF"
if echo "$T_RUFF" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_CONFIG_RUFF)")
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
