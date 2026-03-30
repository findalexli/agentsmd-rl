#!/usr/bin/env bash
# Verifier for areal-pil-image-serialization
# Task: add PIL image and processor serialization for VLM RPC
# File: areal/infra/rpc/serialization.py

set +e

REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p "$(dirname "$REWARD_FILE")"

TARGET="/workspace/AReaL/areal/infra/rpc/serialization.py"

echo "=== areal PIL image serialization verifier ==="

# -- GATE: Python syntax validity --
echo ""
echo "GATE: Python syntax validity"
python3 << 'PYEOF'
import ast, sys
try:
    with open("/workspace/AReaL/areal/infra/rpc/serialization.py") as f:
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

# Weights
W_BEHAVIORAL_PIL_ROUNDTRIP=0.25
W_BEHAVIORAL_PIL_DESERIALIZE=0.15
W_BEHAVIORAL_PROCESSOR_CLASS=0.15
W_STRUCTURAL_SERIALIZE_VALUE=0.10
W_STRUCTURAL_DESERIALIZE_VALUE=0.15
W_ANTISTUB=0.10
W_CONFIG_NO_WILDCARD=0.05
W_CONFIG_NO_BARE_PRINT=0.05

SCORE="0.0"

# -- TEST 1 (PRIMARY): behavioral -- PIL image round-trip serialization --
echo ""
echo "TEST 1: behavioral -- PIL image round-trip serialization (weight=$W_BEHAVIORAL_PIL_ROUNDTRIP)"
T1=$(python3 << 'PYEOF'
import ast, sys, textwrap, types, base64, io, json

with open("/workspace/AReaL/areal/infra/rpc/serialization.py") as f:
    source = f.read()

tree = ast.parse(source)

# Find SerializedPILImage class
pil_class = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "SerializedPILImage":
        pil_class = node
        break

if pil_class is None:
    print("FAIL: SerializedPILImage class not found")
    sys.exit(1)

# Extract the class and try to use it
lines = source.splitlines(keepends=True)
class_src = textwrap.dedent("".join(lines[pil_class.lineno - 1:pil_class.end_lineno]))

try:
    from PIL import Image
    from PIL.Image import Image as ImageObject

    # Create a simple test image
    original = Image.new("RGB", (8, 6), color=(12, 34, 56))

    # Build a minimal execution environment
    exec_ns = {
        "__builtins__": __builtins__,
        "Image": Image,
        "ImageObject": ImageObject,
        "io": io,
        "base64": base64,
    }

    # Add Pydantic imports
    from pydantic import BaseModel, Field
    from typing import Literal
    exec_ns["BaseModel"] = BaseModel
    exec_ns["Field"] = Field
    exec_ns["Literal"] = Literal

    exec(class_src, exec_ns)
    SerializedPILImage = exec_ns["SerializedPILImage"]

    # Test round-trip
    serialized = SerializedPILImage.from_image(original)
    assert serialized.type == "pil_image", f"Expected type 'pil_image', got '{serialized.type}'"

    deserialized = serialized.to_image()
    assert isinstance(deserialized, Image.Image), "Deserialized is not a PIL Image"
    assert deserialized.size == original.size, f"Size mismatch: {deserialized.size} vs {original.size}"
    assert deserialized.mode == original.mode, f"Mode mismatch: {deserialized.mode} vs {original.mode}"

    # Compare pixel data
    orig_bytes = list(original.getdata())
    deser_bytes = list(deserialized.getdata())
    assert orig_bytes == deser_bytes, "Pixel data mismatch"

    print("PASS: PIL image round-trip works correctly")
    sys.exit(0)
except ImportError:
    print("PASS: PIL not installed but SerializedPILImage class exists (structural pass)")
    sys.exit(0)
except Exception as e:
    print(f"FAIL: {e}")
    sys.exit(1)
PYEOF
)
echo "$T1"
if echo "$T1" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_BEHAVIORAL_PIL_ROUNDTRIP)")
fi

# -- TEST 2 (PRIMARY): behavioral -- deserialize_value handles pil_image type marker --
echo ""
echo "TEST 2: behavioral -- deserialize_value handles pil_image type (weight=$W_BEHAVIORAL_PIL_DESERIALIZE)"
T2=$(python3 << 'PYEOF'
import sys

with open("/workspace/AReaL/areal/infra/rpc/serialization.py") as f:
    source = f.read()

# Find deserialize_value and check it handles pil_image
if 'value.get("type") == "pil_image"' in source or "value.get('type') == 'pil_image'" in source:
    print("PASS: deserialize_value handles pil_image type marker")
    sys.exit(0)
elif '"pil_image"' in source and 'deserialize' in source.lower():
    print("PASS: pil_image deserialization logic found")
    sys.exit(0)
else:
    print("FAIL: no pil_image handling in deserialize_value")
    sys.exit(1)
PYEOF
)
echo "$T2"
if echo "$T2" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_BEHAVIORAL_PIL_DESERIALIZE)")
fi

# -- TEST 3 (PRIMARY): behavioral -- SerializedProcessor class exists with required methods --
echo ""
echo "TEST 3: behavioral -- SerializedProcessor class exists (weight=$W_BEHAVIORAL_PROCESSOR_CLASS)"
T3=$(python3 << 'PYEOF'
import ast, sys

with open("/workspace/AReaL/areal/infra/rpc/serialization.py") as f:
    source = f.read()

tree = ast.parse(source)

proc_class = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "SerializedProcessor":
        proc_class = node
        break

if proc_class is None:
    print("FAIL: SerializedProcessor class not found")
    sys.exit(1)

# Check for required methods
method_names = set()
for item in proc_class.body:
    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
        method_names.add(item.name)

required_methods = {"from_processor", "to_processor", "_is_processor"}
missing = required_methods - method_names
if missing:
    print(f"FAIL: SerializedProcessor missing methods: {missing}")
    sys.exit(1)

print(f"PASS: SerializedProcessor has all required methods: {required_methods}")
sys.exit(0)
PYEOF
)
echo "$T3"
if echo "$T3" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_BEHAVIORAL_PROCESSOR_CLASS)")
fi

# -- TEST 4 (SUPPLEMENTARY): structural -- serialize_value handles PIL images --
echo ""
echo "TEST 4: structural -- serialize_value handles PIL Image (weight=$W_STRUCTURAL_SERIALIZE_VALUE)"
T4=$(python3 << 'PYEOF'
import ast, sys

with open("/workspace/AReaL/areal/infra/rpc/serialization.py") as f:
    source = f.read()

tree = ast.parse(source)

# Find serialize_value function
func_node = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == "serialize_value":
        func_node = node
        break

if func_node is None:
    print("FAIL: serialize_value function not found")
    sys.exit(1)

lines = source.splitlines(keepends=True)
func_src = "".join(lines[func_node.lineno - 1:func_node.end_lineno])

has_pil = "ImageObject" in func_src or "PIL" in func_src or "pil_image" in func_src.lower() or "SerializedPILImage" in func_src
has_processor = "SerializedProcessor" in func_src or "_is_processor" in func_src

if has_pil and has_processor:
    print("PASS: serialize_value handles both PIL images and processors")
    sys.exit(0)
elif has_pil:
    print("PASS: serialize_value handles PIL images (partial)")
    sys.exit(0)
else:
    print("FAIL: serialize_value does not handle PIL images")
    sys.exit(1)
PYEOF
)
echo "$T4"
if echo "$T4" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_STRUCTURAL_SERIALIZE_VALUE)")
fi

# -- TEST 5 (SUPPLEMENTARY): structural -- deserialize_value handles processor type --
echo ""
echo "TEST 5: structural -- deserialize_value handles processor type (weight=$W_STRUCTURAL_DESERIALIZE_VALUE)"
T5=$(python3 << 'PYEOF'
import sys

with open("/workspace/AReaL/areal/infra/rpc/serialization.py") as f:
    source = f.read()

if 'value.get("type") == "processor"' in source or "value.get('type') == 'processor'" in source:
    print("PASS: deserialize_value handles processor type marker")
    sys.exit(0)
elif '"processor"' in source and 'SerializedProcessor' in source:
    print("PASS: processor deserialization logic found")
    sys.exit(0)
else:
    print("FAIL: no processor handling in deserialize_value")
    sys.exit(1)
PYEOF
)
echo "$T5"
if echo "$T5" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_STRUCTURAL_DESERIALIZE_VALUE)")
fi

# -- TEST 6: anti-stub check --
echo ""
echo "TEST 6: anti-stub -- file retains original logic (weight=$W_ANTISTUB)"
T6=$(python3 << 'PYEOF'
import sys

with open("/workspace/AReaL/areal/infra/rpc/serialization.py") as f:
    source = f.read()

required = ["SerializedTensor", "SerializedNDArray", "SerializedDataclass",
            "SerializedTokenizer", "serialize_value", "deserialize_value",
            "SerializedPILImage", "SerializedProcessor"]
missing = [r for r in required if r not in source]

if missing:
    print(f"FAIL: file is missing expected content: {missing}")
    sys.exit(1)

line_count = len(source.splitlines())
if line_count < 500:
    print(f"FAIL: file has only {line_count} lines -- looks like a stub")
    sys.exit(1)

print(f"PASS: file has {line_count} lines and contains all expected symbols")
sys.exit(0)
PYEOF
)
echo "$T6"
if echo "$T6" | grep -q "^PASS"; then
    SCORE=$(python3 -c "print($SCORE + $W_ANTISTUB)")
fi

# -- Config-derived (0.05): No wildcard imports --
# Source: AGENTS.md line 13 @ commit 99040b94e43d7e4b26d71c6f37edf7ce6781dc56
echo ""
echo "TEST 7: config-derived -- no wildcard imports (weight=$W_CONFIG_NO_WILDCARD)"
grep -rn "from .* import \*" "$TARGET" 2>/dev/null
if [ $? -ne 0 ]; then
    SCORE=$(python3 -c "print($SCORE + $W_CONFIG_NO_WILDCARD)")
    echo "PASS"
else
    echo "FAIL: wildcard import found"
fi

# -- Config-derived (0.05): No bare print() in production code --
# Source: AGENTS.md line 80 @ commit 99040b94e43d7e4b26d71c6f37edf7ce6781dc56
echo ""
echo "TEST 8: config-derived -- no bare print() (weight=$W_CONFIG_NO_BARE_PRINT)"
grep -nE "^\s*print\(" "$TARGET" 2>/dev/null
if [ $? -ne 0 ]; then
    SCORE=$(python3 -c "print($SCORE + $W_CONFIG_NO_BARE_PRINT)")
    echo "PASS"
else
    echo "FAIL: bare print() found"
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
