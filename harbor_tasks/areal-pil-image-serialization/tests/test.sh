#!/usr/bin/env bash
# Verifier for areal-pil-image-serialization
# Task: add PIL image and processor serialization for VLM RPC
# File: areal/infra/rpc/serialization.py

set +e

REWARD_FILE="/logs/verifier/reward.txt"
REWARD_JSON="/logs/verifier/reward.json"
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
    echo '{"reward": 0.0, "gate": 0}' > "$REWARD_JSON"
    exit 0
fi
echo "GATE PASS"

# Weights (behavioral >= 65%, structural <= 30%, config <= 10%)
W_F2P_PIL_SERIALIZE=0.35      # Fail-to-pass: PIL image round-trip
W_F2P_PROCESSOR_SERIALIZE=0.25 # Fail-to-pass: processor round-trip with mock
W_P2P_ORIGINAL=0.10           # Pass-to-pass: original functionality preserved
W_ANTISTUB_DEPTH=0.10         # Anti-stub: substantial implementation (gated)
W_STRUCTURAL_WIRING=0.10      # Structural: handlers correctly wired (gated)
W_CONFIG_NO_WILDCARD=0.05     # Config: no wildcard imports
W_CONFIG_LOGGING=0.05         # Config: proper logging, no bare print

SCORE="0.0"
BEHAVIORAL="0.0"
STRUCTURAL="0.0"
CONFIG="0.0"

BEHAVIORAL_PASS=false

tally() {
    local weight=$1
    local category=$2
    SCORE=$(python3 -c "print($SCORE + $weight)")
    if [ "$category" = "behavioral" ]; then
        BEHAVIORAL=$(python3 -c "print($BEHAVIORAL + $weight)")
    elif [ "$category" = "structural" ]; then
        STRUCTURAL=$(python3 -c "print($STRUCTURAL + $weight)")
    elif [ "$category" = "config" ]; then
        CONFIG=$(python3 -c "print($CONFIG + $weight)")
    fi
}

# -- TEST 1 (PRIMARY): Fail-to-pass -- Full PIL image round-trip --
echo ""
echo "TEST 1: fail-to-pass -- Full PIL image round-trip (weight=$W_F2P_PIL_SERIALIZE)"
T1=$(python3 << 'PYEOF'
import sys
import os
sys.path.insert(0, '/workspace/AReaL')

try:
    from PIL import Image
    from areal.infra.rpc.serialization import serialize_value, deserialize_value
except ImportError as e:
    print(f"SKIP: Cannot import required modules: {e}")
    sys.exit(1)

# Create test images with different modes and sizes
test_cases = [
    ("RGB", (64, 48), (255, 128, 64)),
    ("RGBA", (32, 24), (128, 64, 32, 200)),
    ("L", (16, 12), 128),
    ("P", (8, 8), 128),  # Palette mode
]

for mode, size, color in test_cases:
    try:
        # Create original image
        original = Image.new(mode, size, color=color)

        # Serialize - this should work with the fix
        serialized = serialize_value(original)

        # Verify serialized structure
        if not isinstance(serialized, dict):
            print(f"FAIL ({mode}): serialize_value returned {type(serialized)}, expected dict")
            sys.exit(1)

        if serialized.get("type") != "pil_image":
            print(f"FAIL ({mode}): serialized type marker is '{serialized.get('type')}', expected 'pil_image'")
            sys.exit(1)

        if "data" not in serialized:
            print(f"FAIL ({mode}): serialized dict missing 'data' field")
            sys.exit(1)

        # Verify data is base64-encoded PNG bytes
        import base64
        try:
            decoded = base64.b64decode(serialized["data"])
        except Exception:
            print(f"FAIL ({mode}): data field is not valid base64")
            sys.exit(1)

        # Verify it's a valid PNG (magic bytes)
        if not decoded.startswith(b'\x89PNG\r\n\x1a\n'):
            print(f"FAIL ({mode}): data is not a valid PNG (wrong magic bytes)")
            sys.exit(1)

        # Deserialize - this should work with the fix
        deserialized = deserialize_value(serialized)

        # Verify deserialized image
        if not isinstance(deserialized, Image.Image):
            print(f"FAIL ({mode}): deserialize_value returned {type(deserialized)}, expected PIL.Image")
            sys.exit(1)

        if deserialized.size != original.size:
            print(f"FAIL ({mode}): size mismatch: {deserialized.size} vs {original.size}")
            sys.exit(1)

        if deserialized.mode != original.mode:
            print(f"FAIL ({mode}): mode mismatch: {deserialized.mode} vs {original.mode}")
            sys.exit(1)

        # Compare pixel data
        orig_bytes = list(original.getdata())
        deser_bytes = list(deserialized.getdata())
        if orig_bytes != deser_bytes:
            print(f"FAIL ({mode}): pixel data mismatch")
            sys.exit(1)

    except Exception as e:
        print(f"FAIL ({mode}): {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

print("PASS: Full PIL image round-trip works correctly (RGB, RGBA, L, P modes)")
sys.exit(0)
PYEOF
)
echo "$T1"
if echo "$T1" | grep -q "^PASS"; then
    tally $W_F2P_PIL_SERIALIZE "behavioral"
    PIL_PASS=true
elif echo "$T1" | grep -q "^SKIP"; then
    echo "  -> SKIPPED (dependencies missing)"
    PIL_PASS=false
else
    echo "  -> FAILED"
    PIL_PASS=false
fi

# -- TEST 2 (PRIMARY): Fail-to-pass -- Processor round-trip with mock --
# NO AST fallback - this must execute actual serialization logic
echo ""
echo "TEST 2: fail-to-pass -- Processor round-trip via serialize_value (weight=$W_F2P_PROCESSOR_SERIALIZE)"
T2=$(python3 << 'PYEOF'
import sys
import os
import tempfile
import zipfile
import base64
sys.path.insert(0, '/workspace/AReaL')

try:
    from areal.infra.rpc.serialization import serialize_value, deserialize_value
except ImportError as e:
    print(f"SKIP: Cannot import serialization module: {e}")
    sys.exit(1)

# Create a mock processor that has save_pretrained behavior
class MockProcessor:
    """Mock processor that mimics HF ProcessorMixin behavior."""
    def __init__(self, processor_data):
        self._data = processor_data

    def save_pretrained(self, save_directory, **kwargs):
        """Save processor config to directory (mimics HF transformers)."""
        import json
        import os
        os.makedirs(save_directory, exist_ok=True)
        config_path = os.path.join(save_directory, "preprocessor_config.json")
        with open(config_path, "w") as f:
            json.dump(self._data, f)
        # Also create a tokenizer_config.json to be more realistic
        tokenizer_path = os.path.join(save_directory, "tokenizer_config.json")
        with open(tokenizer_path, "w") as f:
            json.dump({"name": "mock_tokenizer"}, f)

    def __eq__(self, other):
        """Check equality for verification."""
        if not isinstance(other, MockProcessor):
            return False
        return self._data == other._data

    @classmethod
    def from_pretrained(cls, pretrained_model_name_or_path, **kwargs):
        """Load processor from directory (mimics AutoProcessor)."""
        import json
        import os
        config_path = os.path.join(pretrained_model_name_or_path, "preprocessor_config.json")
        with open(config_path, "r") as f:
            data = json.load(f)
        return cls(data)

# Test the round-trip
try:
    # Create a mock processor with test data
    test_data = {"image_size": 224, "patch_size": 14, "model_type": "test_vlm"}
    original = MockProcessor(test_data)

    # Serialize the processor
    serialized = serialize_value(original)

    # Verify serialized structure
    if not isinstance(serialized, dict):
        print(f"FAIL: serialize_value returned {type(serialized)}, expected dict")
        sys.exit(1)

    if serialized.get("type") != "processor":
        print(f"FAIL: serialized type marker is '{serialized.get('type')}', expected 'processor'")
        sys.exit(1)

    if "data" not in serialized:
        print(f"FAIL: serialized dict missing 'data' field")
        sys.exit(1)

    # Verify data is base64-encoded
    try:
        decoded = base64.b64decode(serialized["data"])
    except Exception:
        print(f"FAIL: data field is not valid base64")
        sys.exit(1)

    # Verify it's a valid ZIP file
    try:
        with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp:
            tmp.write(decoded)
            tmp_path = tmp.name

        with zipfile.ZipFile(tmp_path, 'r') as zf:
            file_list = zf.namelist()
            if "preprocessor_config.json" not in file_list:
                print(f"FAIL: ZIP does not contain preprocessor_config.json, got: {file_list}")
                os.unlink(tmp_path)
                sys.exit(1)
            # Read and verify the config
            with zf.open("preprocessor_config.json") as f:
                import json
                loaded_data = json.load(f)
                if loaded_data != test_data:
                    print(f"FAIL: Config data mismatch in ZIP: {loaded_data} != {test_data}")
                    os.unlink(tmp_path)
                    sys.exit(1)

        os.unlink(tmp_path)
    except zipfile.BadZipFile:
        print(f"FAIL: data is not a valid ZIP file")
        sys.exit(1)

    # Deserialize the processor
    # NOTE: The fix should use AutoProcessor.from_pretrained, but we verify
    # it can be deserialized to a usable form. Since we don't have real HF,
    # we check that the data structure is correct for AutoProcessor to use.

    deserialized = deserialize_value(serialized)

    # Verify we got something back (deserialize should not crash)
    if deserialized is None:
        print(f"FAIL: deserialize_value returned None")
        sys.exit(1)

    # The deserialized value should either be a processor-like object or
    # we should be able to extract the archive and use it

    print("PASS: Processor serialization round-trip works correctly")
    sys.exit(0)

except Exception as e:
    print(f"FAIL: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
PYEOF
)
echo "$T2"
if echo "$T2" | grep -q "^PASS"; then
    tally $W_F2P_PROCESSOR_SERIALIZE "behavioral"
    PROC_PASS=true
elif echo "$T2" | grep -q "^SKIP"; then
    echo "  -> SKIPPED (dependencies missing)"
    PROC_PASS=false
else
    echo "  -> FAILED"
    PROC_PASS=false
fi

# Determine if core behavioral tests passed
if [ "$PIL_PASS" = true ] && [ "$PROC_PASS" = true ]; then
    BEHAVIORAL_PASS=true
fi

# -- TEST 3 (SUPPLEMENTARY): Pass-to-pass -- Original functionality still works --
echo ""
echo "TEST 3: pass-to-pass -- Original serialization still works (weight=$W_P2P_ORIGINAL)"
T3=$(python3 << 'PYEOF'
import sys
sys.path.insert(0, '/workspace/AReaL')

try:
    from areal.infra.rpc.serialization import serialize_value, deserialize_value
    import numpy as np
except ImportError as e:
    print(f"SKIP: Cannot import: {e}")
    sys.exit(1)

# Test that basic types still serialize correctly
test_cases = [
    (42, 42, "int"),
    (3.14, 3.14, "float"),
    ("hello", "hello", "str"),
    ([1, 2, 3], [1, 2, 3], "list"),
    ({"a": 1}, {"a": 1}, "dict"),
]

for original, expected, name in test_cases:
    result = serialize_value(original)
    if isinstance(expected, float):
        if abs(result - expected) > 0.001:
            print(f"FAIL: {name} serialization failed: {result} != {expected}")
            sys.exit(1)
    elif result != expected:
        print(f"FAIL: {name} serialization failed: {result} != {expected}")
        sys.exit(1)

# Test numpy array serialization
try:
    arr = np.array([1.0, 2.0, 3.0])
    serialized = serialize_value(arr)
    if not isinstance(serialized, dict) or serialized.get("type") != "ndarray":
        print(f"FAIL: ndarray serialization failed: {serialized}")
        sys.exit(1)

    deserialized = deserialize_value(serialized)
    if not np.array_equal(deserialized, arr):
        print(f"FAIL: ndarray round-trip failed")
        sys.exit(1)
except Exception as e:
    print(f"FAIL: ndarray test failed: {e}")
    sys.exit(1)

print("PASS: Original serialization functionality preserved")
sys.exit(0)
PYEOF
)
echo "$T3"
if echo "$T3" | grep -q "^PASS"; then
    tally $W_P2P_ORIGINAL "behavioral"
elif echo "$T3" | grep -q "^SKIP"; then
    echo "  -> SKIPPED"
else
    echo "  -> FAILED"
fi

# -- TEST 4: Anti-stub check (GATED: only if behavioral passed) --
echo ""
echo "TEST 4: anti-stub -- Implementation has depth (weight=$W_ANTISTUB_DEPTH)"
if [ "$BEHAVIORAL_PASS" = true ]; then
    T4=$(python3 << 'PYEOF'
import ast
import sys

with open("/workspace/AReaL/areal/infra/rpc/serialization.py") as f:
    source = f.read()

tree = ast.parse(source)

# Find SerializedPILImage class
pil_class = None
proc_class = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef):
        if node.name == "SerializedPILImage":
            pil_class = node
        elif node.name == "SerializedProcessor":
            proc_class = node

if pil_class is None:
    print("FAIL: SerializedPILImage class not found")
    sys.exit(1)

if proc_class is None:
    print("FAIL: SerializedProcessor class not found")
    sys.exit(1)

# Check SerializedPILImage has substantial from_image/to_image methods
def count_meanful_statements(func_node):
    """Count non-docstring, non-pass statements in function body."""
    count = 0
    for stmt in func_node.body:
        if isinstance(stmt, ast.Expr) and isinstance(stmt.value, (ast.Constant, ast.Str)):
            continue  # docstring
        if isinstance(stmt, ast.Pass):
            continue
        count += 1
    return count

# Check SerializedPILImage methods
pil_methods = {item.name: item for item in pil_class.body if isinstance(item, ast.FunctionDef)}
if "from_image" not in pil_methods:
    print("FAIL: SerializedPILImage missing from_image method")
    sys.exit(1)
if "to_image" not in pil_methods:
    print("FAIL: SerializedPILImage missing to_image method")
    sys.exit(1)

pil_from_count = count_meanful_statements(pil_methods["from_image"])
pil_to_count = count_meanful_statements(pil_methods["to_image"])

if pil_from_count < 3:
    print(f"FAIL: SerializedPILImage.from_image looks like a stub ({pil_from_count} meaningful statements)")
    sys.exit(1)
if pil_to_count < 3:
    print(f"FAIL: SerializedPILImage.to_image looks like a stub ({pil_to_count} meaningful statements)")
    sys.exit(1)

# Check SerializedProcessor has substantial from_processor/to_processor methods
proc_methods = {item.name: item for item in proc_class.body if isinstance(item, ast.FunctionDef)}
if "from_processor" not in proc_methods:
    print("FAIL: SerializedProcessor missing from_processor method")
    sys.exit(1)
if "to_processor" not in proc_methods:
    print("FAIL: SerializedProcessor missing to_processor method")
    sys.exit(1)

proc_from_count = count_meanful_statements(proc_methods["from_processor"])
proc_to_count = count_meanful_statements(proc_methods["to_processor"])

if proc_from_count < 5:  # Processor needs more: save_pretrained, zip, base64
    print(f"FAIL: SerializedProcessor.from_processor looks like a stub ({proc_from_count} meaningful statements)")
    sys.exit(1)
if proc_to_count < 3:
    print(f"FAIL: SerializedProcessor.to_processor looks like a stub ({proc_to_count} meaningful statements)")
    sys.exit(1)

# Check that serialize_value actually calls these methods
serialize_func = None
deserialize_func = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef):
        if node.name == "serialize_value":
            serialize_func = node
        elif node.name == "deserialize_value":
            deserialize_func = node

if serialize_func is None or deserialize_func is None:
    print("FAIL: serialize_value or deserialize_value not found")
    sys.exit(1)

# Check for actual method calls, not just string presence
has_from_image_call = False
has_from_processor_call = False

for node in ast.walk(serialize_func):
    if isinstance(node, ast.Call):
        if isinstance(node.func, ast.Attribute):
            if node.func.attr == "from_image":
                has_from_image_call = True
            elif node.func.attr == "from_processor":
                has_from_processor_call = True

if not has_from_image_call:
    print("FAIL: serialize_value does not call from_image method")
    sys.exit(1)

if not has_from_processor_call:
    print("FAIL: serialize_value does not call from_processor method")
    sys.exit(1)

print(f"PASS: Implementation has depth (PIL: {pil_from_count}/{pil_to_count}, Proc: {proc_from_count}/{proc_to_count} statements)")
sys.exit(0)
PYEOF
)
    echo "$T4"
    if echo "$T4" | grep -q "^PASS"; then
        tally $W_ANTISTUB_DEPTH "structural"
    else
        echo "  -> FAILED (implementation too shallow)"
    fi
else
    echo "  -> SKIPPED (behavioral tests must pass first)"
fi

# -- TEST 5: Structural wiring check (GATED: only if behavioral passed) --
echo ""
echo "TEST 5: structural -- Handlers correctly wired (weight=$W_STRUCTURAL_WIRING)"
if [ "$BEHAVIORAL_PASS" = true ]; then
    T5=$(python3 << 'PYEOF'
import ast
import sys

with open("/workspace/AReaL/areal/infra/rpc/serialization.py") as f:
    source = f.read()

tree = ast.parse(source)

# Find serialize_value and deserialize_value
serialize_func = None
deserialize_func = None

for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef):
        if node.name == "serialize_value":
            serialize_func = node
        elif node.name == "deserialize_value":
            deserialize_func = node

if serialize_func is None:
    print("FAIL: serialize_value not found")
    sys.exit(1)

if deserialize_func is None:
    print("FAIL: deserialize_value not found")
    sys.exit(1)

# Extract serialize_value source lines for analysis
lines = source.splitlines(keepends=True)
serc_source = "".join(lines[serialize_func.lineno-1:serialize_func.end_lineno])
deser_source = "".join(lines[deserialize_func.lineno-1:deserialize_func.end_lineno])

# Check serialize_value has PIL isinstance check (for Image.Image)
has_pil_isinstance = False
for node in ast.walk(serialize_func):
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "isinstance":
        has_pil_isinstance = True
        break

if not has_pil_isinstance:
    print("FAIL: serialize_value missing isinstance check")
    sys.exit(1)

# Check deserialize_value has type marker checks via AST (not string search)
has_pil_type_check = False
has_proc_type_check = False

for node in ast.walk(deserialize_func):
    if isinstance(node, ast.Compare):
        # Look for value.get("type") == "something" pattern
        if isinstance(node.left, ast.Call):
            call = node.left
            if isinstance(call.func, ast.Attribute) and call.func.attr == "get":
                # Check the comparison
                for comparator in node.comparators:
                    if isinstance(comparator, ast.Constant) and comparator.value == "pil_image":
                        has_pil_type_check = True
                    if isinstance(comparator, ast.Constant) and comparator.value == "processor":
                        has_proc_type_check = True

if not has_pil_type_check:
    print("FAIL: deserialize_value missing pil_image type check")
    sys.exit(1)

if not has_proc_type_check:
    print("FAIL: deserialize_value missing processor type check")
    sys.exit(1)

print("PASS: Handlers correctly wired in serialize_value and deserialize_value")
sys.exit(0)
PYEOF
)
    echo "$T5"
    if echo "$T5" | grep -q "^PASS"; then
        tally $W_STRUCTURAL_WIRING "structural"
    else
        echo "  -> FAILED"
    fi
else
    echo "  -> SKIPPED (behavioral tests must pass first)"
fi

# -- Config check: No wildcard imports --
echo ""
echo "TEST 6: config -- no wildcard imports (weight=$W_CONFIG_NO_WILDCARD)"
grep -rn "from .* import \*" "$TARGET" 2>/dev/null
if [ $? -ne 0 ]; then
    tally $W_CONFIG_NO_WILDCARD "config"
    echo "PASS: no wildcard imports"
else
    echo "FAIL: wildcard import found"
fi

# -- Config check: No bare print() --
echo ""
echo "TEST 7: config -- no bare print() (weight=$W_CONFIG_LOGGING)"
python3 << 'PYEOF'
import ast
import sys

with open("/workspace/AReaL/areal/infra/rpc/serialization.py") as f:
    source = f.read()

tree = ast.parse(source)

print_calls = []
for node in ast.walk(tree):
    if isinstance(node, ast.Call):
        if isinstance(node.func, ast.Name) and node.func.id == "print":
            print_calls.append(node.lineno)

if print_calls:
    print(f"FAIL: bare print() found at lines: {print_calls}")
    sys.exit(1)

print("PASS: no bare print() found")
sys.exit(0)
PYEOF
if [ $? -eq 0 ]; then
    tally $W_CONFIG_LOGGING "config"
fi

# -- Final score --
echo ""
echo "================================"
REWARD=$(python3 -c "print('{:.4f}'.format(min($SCORE, 1.0)))")
echo "Reward: $REWARD"
echo "Behavioral: $BEHAVIORAL | Structural: $STRUCTURAL | Config: $CONFIG"
echo "================================"
echo "$REWARD" > "$REWARD_FILE"

# Write JSON with breakdown
python3 << PYEOF
import json
data = {
    "reward": float("$REWARD"),
    "behavioral": float("$BEHAVIORAL"),
    "structural": float("$STRUCTURAL"),
    "config": float("$CONFIG")
}
with open("$REWARD_JSON", "w") as f:
    json.dump(data, f)
PYEOF

# LLM rubric judge (runs only when LLM_JUDGE=1)
source /tests/judge_hook.sh 2>/dev/null || true
