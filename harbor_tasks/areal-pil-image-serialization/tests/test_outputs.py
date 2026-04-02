"""
Task: areal-pil-image-serialization
Repo: inclusionAI/AReaL @ 99040b94e43d7e4b26d71c6f37edf7ce6781dc56
PR:   1070

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import base64
import io
import json
import os
import re
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, "/workspace/AReaL")

REPO = "/workspace/AReaL"
TARGET = f"{REPO}/areal/infra/rpc/serialization.py"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """serialization.py must parse without syntax errors."""
    import py_compile

    py_compile.compile(TARGET, doraise=True)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — PIL image serialization
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_pil_roundtrip_rgb():
    """RGB PIL images of varying sizes round-trip through serialize/deserialize."""
    from PIL import Image

    from areal.infra.rpc.serialization import deserialize_value, serialize_value

    cases = [
        ((64, 48), (255, 128, 64)),
        ((1, 1), (0, 0, 0)),
        ((100, 50), (1, 2, 3)),
    ]
    for size, color in cases:
        original = Image.new("RGB", size, color=color)
        # Add a non-uniform pixel to avoid flat-image shortcuts
        original.putpixel((0, 0), (color[2], color[1], color[0]))

        serialized = serialize_value(original)
        assert isinstance(serialized, dict), f"Expected dict, got {type(serialized)}"
        assert serialized["type"] == "pil_image"

        restored = deserialize_value(serialized)
        assert isinstance(restored, Image.Image)
        assert restored.size == size, f"Size mismatch: {restored.size} != {size}"
        assert restored.mode == "RGB"
        assert restored.tobytes() == original.tobytes(), f"Pixel mismatch for {size}"


# [pr_diff] fail_to_pass
def test_pil_roundtrip_varied_modes():
    """RGBA and grayscale (L) images round-trip with correct mode, size, and pixels."""
    from PIL import Image

    from areal.infra.rpc.serialization import deserialize_value, serialize_value

    cases = [
        ("RGBA", (32, 24), (128, 64, 32, 200)),
        ("RGBA", (4, 4), (0, 0, 0, 0)),
        ("L", (16, 12), 128),
        ("L", (1, 1), 0),
    ]
    for mode, size, color in cases:
        original = Image.new(mode, size, color=color)
        serialized = serialize_value(original)
        assert isinstance(serialized, dict), f"{mode}: expected dict"
        assert serialized["type"] == "pil_image", f"{mode}: wrong type marker"
        restored = deserialize_value(serialized)
        assert isinstance(restored, Image.Image), f"{mode}: not an Image"
        assert restored.mode == mode, f"{mode}: mode mismatch {restored.mode}"
        assert restored.size == size, f"{mode}: size mismatch {restored.size}"
        assert restored.tobytes() == original.tobytes(), f"{mode} {size}: pixel mismatch"


# [pr_diff] fail_to_pass
def test_pil_serialized_structure():
    """Serialized PIL image dict contains base64-encoded PNG data with mode."""
    from PIL import Image

    from areal.infra.rpc.serialization import serialize_value

    for mode, size, color in [("RGB", (8, 8), (10, 20, 30)), ("L", (4, 4), 99)]:
        result = serialize_value(Image.new(mode, size, color=color))
        assert result["type"] == "pil_image"
        assert "data" in result
        raw = base64.b64decode(result["data"])
        assert raw[:8] == b"\x89PNG\r\n\x1a\n", "data is not a PNG"
        assert result.get("mode") == mode, f"Expected mode={mode}"


# [pr_diff] fail_to_pass
def test_pil_nested_in_structure():
    """PIL images inside dicts and lists are recursively serialized."""
    from PIL import Image

    from areal.infra.rpc.serialization import deserialize_value, serialize_value

    img_a = Image.new("RGB", (4, 4), color=(10, 20, 30))
    img_b = Image.new("L", (2, 2), color=200)

    payload = {"image": img_a, "batch": [img_b, 42, "text"], "label": "test"}
    serialized = serialize_value(payload)

    # Nested images should be serialized dicts
    assert isinstance(serialized["image"], dict)
    assert serialized["image"]["type"] == "pil_image"
    assert isinstance(serialized["batch"][0], dict)
    assert serialized["batch"][0]["type"] == "pil_image"
    # Primitives pass through
    assert serialized["batch"][1] == 42
    assert serialized["label"] == "test"

    # Round-trip the whole structure
    restored = deserialize_value(serialized)
    assert isinstance(restored["image"], Image.Image)
    assert restored["image"].tobytes() == img_a.tobytes()
    assert isinstance(restored["batch"][0], Image.Image)
    assert restored["batch"][0].tobytes() == img_b.tobytes()


# [pr_diff] fail_to_pass
def test_processor_class_serialize():
    """SerializedProcessor.from_processor creates a ZIP archive with processor files."""
    from areal.infra.rpc.serialization import SerializedProcessor

    class FakeProcessor:
        name_or_path = "test-proc"

        def save_pretrained(self, directory, **kwargs):
            os.makedirs(directory, exist_ok=True)
            with open(os.path.join(directory, "preprocessor_config.json"), "w") as f:
                json.dump({"image_size": 224, "model_type": "test_vlm"}, f)
            with open(os.path.join(directory, "tokenizer_config.json"), "w") as f:
                json.dump({"name": "fake_tok"}, f)

    proc = FakeProcessor()
    serialized = SerializedProcessor.from_processor(proc)

    assert serialized.type == "processor"
    assert serialized.name_or_path == "test-proc"

    # Verify the data is a valid ZIP containing processor files
    raw = base64.b64decode(serialized.data)
    with zipfile.ZipFile(io.BytesIO(raw)) as zf:
        names = zf.namelist()
        assert "preprocessor_config.json" in names
        assert "tokenizer_config.json" in names
        with zf.open("preprocessor_config.json") as f:
            cfg = json.load(f)
            assert cfg["image_size"] == 224

    # Test with a different processor that has no name_or_path attr
    class AnonProcessor:
        def save_pretrained(self, directory, **kwargs):
            os.makedirs(directory, exist_ok=True)
            with open(os.path.join(directory, "config.json"), "w") as f:
                json.dump({"type": "anon"}, f)

    anon = AnonProcessor()
    serialized2 = SerializedProcessor.from_processor(anon)
    assert serialized2.type == "processor"
    assert serialized2.name_or_path == "AnonProcessor"


# ---------------------------------------------------------------------------
# Pass-to-pass — regression
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_original_types_preserved():
    """Primitive types and ndarray serialization still works after the change."""
    import numpy as np

    from areal.infra.rpc.serialization import deserialize_value, serialize_value

    # Primitives pass through unchanged
    for val in [42, 3.14, "hello", True, None, [1, 2], {"a": 1}]:
        roundtripped = deserialize_value(serialize_value(val))
        assert roundtripped == val, f"Primitive {val!r} changed after round-trip"

    # ndarray round-trip with varied shapes
    for shape in [(2, 2), (1,), (3, 4, 2)]:
        arr = np.arange(int(np.prod(shape)), dtype=np.float64).reshape(shape)
        s = serialize_value(arr)
        assert isinstance(s, dict) and s.get("type") == "ndarray"
        restored = deserialize_value(s)
        assert np.array_equal(restored, arr), f"ndarray mismatch for shape {shape}"


# ---------------------------------------------------------------------------
# Config-derived (agent_config)
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:30 @ 99040b94e43d7e4b26d71c6f37edf7ce6781dc56
def test_no_wildcard_imports():
    """No wildcard imports in serialization.py (AGENTS.md rule)."""
    src = Path(TARGET).read_text()
    wildcards = re.findall(r"^\s*from\s+\S+\s+import\s+\*", src, re.MULTILINE)
    assert wildcards == [], f"Wildcard imports found: {wildcards}"


# [agent_config] pass_to_pass — AGENTS.md:89 @ 99040b94e43d7e4b26d71c6f37edf7ce6781dc56
def test_no_print_statements():
    """No bare print() calls in serialization.py — use areal.utils.logging instead."""
    import ast

    src = Path(TARGET).read_text()
    tree = ast.parse(src)
    prints = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name) and func.id == "print":
                prints.append(node.lineno)
    assert prints == [], f"print() calls found at lines: {prints}"
