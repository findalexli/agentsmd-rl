"""
Task: sglang-routed-experts-base64
Repo: sgl-project/sglang @ 2acdda1d850122129c6ff21b6d07b2a4c9eb31bd

Fix encode_image_base64 for torch.Tensor, move base64 encoding from
detokenizer to tokenizer manager, reduce NUMA log noise.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import base64
import importlib.util
import io
import sys
import types
from pathlib import Path

REPO = "/workspace/sglang"
UTILS = f"{REPO}/python/sglang/utils.py"
DETOK = f"{REPO}/python/sglang/srt/managers/detokenizer_manager.py"
TOKMGR = f"{REPO}/python/sglang/srt/managers/tokenizer_manager.py"
NUMA = f"{REPO}/python/sglang/srt/utils/numa_utils.py"


def _load_encode_image_base64():
    """Load encode_image_base64 by mocking heavy sglang deps."""
    for mod_name in [
        "requests", "IPython", "IPython.display",
        "pydantic", "sglang.srt", "sglang.srt.environ",
    ]:
        if mod_name not in sys.modules:
            sys.modules[mod_name] = types.ModuleType(mod_name)

    sys.modules["IPython.display"].HTML = lambda *a, **k: None
    sys.modules["IPython.display"].display = lambda *a, **k: None

    class _FakeBaseModel:
        def __init_subclass__(cls, **kwargs):
            pass

    sys.modules["pydantic"].BaseModel = _FakeBaseModel
    sys.modules["sglang.srt.environ"].envs = types.SimpleNamespace()

    if "sglang" not in sys.modules:
        sys.modules["sglang"] = types.ModuleType("sglang")
        sys.modules["sglang"].__path__ = [f"{REPO}/python/sglang"]

    spec = importlib.util.spec_from_file_location("sglang.utils", UTILS)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["sglang.utils"] = mod
    spec.loader.exec_module(mod)
    return mod.encode_image_base64


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) -- syntax checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """All four modified files must parse without syntax errors."""
    for path in [UTILS, DETOK, TOKMGR, NUMA]:
        source = Path(path).read_text()
        ast.parse(source)  # raises SyntaxError on failure


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) -- encode_image_base64 torch.Tensor support
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_tensor_no_crash():
    """encode_image_base64 must accept a torch.Tensor without crashing."""
    import torch

    encode = _load_encode_image_base64()

    # Test multiple tensor sizes
    for h, w in [(8, 8), (1, 1), (32, 64)]:
        tensor = torch.randint(0, 256, (3, h, w), dtype=torch.uint8)
        result = encode(tensor)
        assert isinstance(result, str), f"Expected str, got {type(result)}"
        assert len(result) > 10, f"Result too short for {h}x{w} tensor"


# [pr_diff] fail_to_pass
def test_tensor_valid_png():
    """Tensor encoding must produce valid base64-encoded PNG data."""
    import torch
    from PIL import Image

    encode = _load_encode_image_base64()

    for size in [(16, 16), (4, 8), (50, 30)]:
        tensor = torch.randint(0, 256, (3, *size), dtype=torch.uint8)
        result = encode(tensor)

        raw = base64.b64decode(result)
        assert raw[:4] == b"\x89PNG", f"Not PNG for {size}: magic={raw[:4]!r}"

        img = Image.open(io.BytesIO(raw))
        img.load()
        assert img.size == (size[1], size[0]), (
            f"Expected {(size[1], size[0])}, got {img.size}"
        )


# [pr_diff] fail_to_pass
def test_tensor_pixel_roundtrip():
    """CHW tensor pixel values must survive the encode/decode round-trip."""
    import numpy as np
    import torch
    from PIL import Image

    encode = _load_encode_image_base64()

    # Solid red 4x4
    tensor = torch.zeros(3, 4, 4, dtype=torch.uint8)
    tensor[0, :, :] = 255

    raw = base64.b64decode(encode(tensor))
    arr = np.array(Image.open(io.BytesIO(raw)).convert("RGB"))

    assert (arr[:, :, 0] == 255).all(), "Red channel not preserved"
    assert (arr[:, :, 1] == 0).all(), "Green channel not zero"
    assert (arr[:, :, 2] == 0).all(), "Blue channel not zero"

    # Solid blue 8x8
    tensor2 = torch.zeros(3, 8, 8, dtype=torch.uint8)
    tensor2[2, :, :] = 128

    raw2 = base64.b64decode(encode(tensor2))
    arr2 = np.array(Image.open(io.BytesIO(raw2)).convert("RGB"))

    assert (arr2[:, :, 0] == 0).all(), "Red should be 0 for blue image"
    assert (arr2[:, :, 2] == 128).all(), "Blue channel not preserved"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) -- existing functionality preserved
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_bytes_input_unchanged():
    """encode_image_base64 must still handle bytes input correctly."""
    encode = _load_encode_image_base64()

    test_bytes = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
    result = encode(test_bytes)
    decoded = base64.b64decode(result)
    assert decoded == test_bytes, "Bytes round-trip failed"

    # Also test with arbitrary binary data
    arbitrary = bytes(range(256))
    result2 = encode(arbitrary)
    assert base64.b64decode(result2) == arbitrary, "Arbitrary bytes round-trip failed"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) -- detokenizer cleanup
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_detokenizer_no_extract_method():
    # AST-only because: detokenizer_manager imports zmq, psutil, sglang internals — cannot import
    """_extract_routed_experts must be removed from detokenizer_manager."""
    source = Path(DETOK).read_text()
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            assert node.name != "_extract_routed_experts", (
                "_extract_routed_experts method still exists in detokenizer"
            )


# [pr_diff] fail_to_pass
def test_detokenizer_no_pybase64_import():
    # AST-only because: detokenizer_manager imports zmq, psutil, sglang internals — cannot import
    """Detokenizer must not import pybase64 at module level."""
    source = Path(DETOK).read_text()
    tree = ast.parse(source)

    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert alias.name != "pybase64", (
                    "Detokenizer still imports pybase64 at module level"
                )
        elif isinstance(node, ast.ImportFrom):
            assert not (node.module and "pybase64" in node.module), (
                "Detokenizer still imports from pybase64"
            )


# [pr_diff] fail_to_pass
def test_tokenizer_manager_has_base64():
    # AST-only because: tokenizer_manager imports zmq, fastapi, sglang internals — cannot import
    """Tokenizer manager must import pybase64 and call b64encode."""
    source = Path(TOKMGR).read_text()
    tree = ast.parse(source)

    # Check pybase64 import
    has_pybase64 = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "pybase64":
                    has_pybase64 = True
        elif isinstance(node, ast.ImportFrom):
            if node.module and "pybase64" in node.module:
                has_pybase64 = True
    assert has_pybase64, "tokenizer_manager does not import pybase64"

    # Check b64encode call exists
    has_b64encode = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id == "b64encode":
                has_b64encode = True
            elif isinstance(node.func, ast.Attribute) and node.func.attr == "b64encode":
                has_b64encode = True
    assert has_b64encode, "tokenizer_manager has no b64encode() call"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) -- NUMA log level
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_numa_debug_not_warning():
    # AST-only because: numa_utils imports sglang.srt internals and subprocess/shutil — cannot import
    """numactl-not-found message must use logger.debug, not logger.warning."""
    source = Path(NUMA).read_text()
    tree = ast.parse(source)

    # Fail if any logger.warning mentions numactl
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if (node.func.attr == "warning"
                    and isinstance(node.func.value, ast.Name)
                    and node.func.value.id == "logger"):
                for arg in node.args:
                    if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                        assert "numactl" not in arg.value.lower(), (
                            "logger.warning still used for numactl message"
                        )

    # Positive: logger.debug must mention numactl
    found_debug = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if (node.func.attr == "debug"
                    and isinstance(node.func.value, ast.Name)
                    and node.func.value.id == "logger"):
                for arg in node.args:
                    if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                        if "numactl" in arg.value.lower():
                            found_debug = True
    assert found_debug, "No logger.debug call found mentioning numactl"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) -- anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub():
    """Modified files must retain expected symbols and not be stubbed out."""
    checks = [
        (UTILS, ["encode_image_base64", "pybase64", "BytesIO"], 150),
        (DETOK, ["DetokenizerManager", "handle_batch_token_id_out",
                  "BatchStrOutput", "BatchTokenIDOutput"], 250),
        (TOKMGR, ["TokenizerManager", "_handle_batch_output", "meta_info"], 500),
        (NUMA, ["numactl", "_is_numa_available", "logger"], 50),
    ]
    for path, symbols, min_lines in checks:
        source = Path(path).read_text()
        lines = len(source.splitlines())
        assert lines >= min_lines, (
            f"{Path(path).name} has {lines} lines (min {min_lines}) -- stubbed?"
        )
        missing = [s for s in symbols if s not in source]
        assert not missing, f"{Path(path).name} missing symbols: {missing}"
