"""
Task: slime-vision-nonqwen-fallback
Repo: THUDM/slime @ a1ee76cfe1c0fbb4511d5bc2d2fc28622728121c
PR:   (multi-file vision/multimodal robustness fix)

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import base64
import io
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock

from PIL import Image

REPO = "/workspace/slime"
sys.path.insert(0, REPO)


# Files modified by this PR
MODIFIED_FILES = [
    "slime/utils/processing_utils.py",
    "slime/backends/megatron_utils/actor.py",
    "slime/rollout/sglang_rollout.py",
    "slime_plugins/megatron_bridge/glm4v_moe.py",
]


def _make_b64_image(color, size):
    """Helper: create a base64-encoded PNG."""
    img = Image.new("RGB", size, color=color)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


def _make_data_uri(color, size):
    """Helper: create a data:image/png;base64,... URI."""
    return "data:image/png;base64," + _make_b64_image(color, size)


def _mock_processor():
    proc = MagicMock()
    proc.image_processor.patch_size = 14
    return proc


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """All modified files must be valid Python."""
    for f in MODIFIED_FILES:
        p = Path(REPO) / f
        if p.exists():
            source = p.read_text()
            ast.parse(source)  # raises SyntaxError on failure


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI linting and formatting checks
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_ruff_check():
    """Repo's ruff linter passes on modified files (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "ruff", "-q"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    # Install may return 0 even with warnings, continue to check
    files = [f for f in MODIFIED_FILES if (Path(REPO) / f).exists()]
    r = subprocess.run(
        ["ruff", "check"] + files,
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_isort_check():
    """Repo's isort import sorting passes on modified files (pass_to_pass)."""
    subprocess.run(
        ["pip", "install", "isort", "-q"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    files = [f for f in MODIFIED_FILES if (Path(REPO) / f).exists()]
    r = subprocess.run(
        ["isort", "--check-only"] + files,
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"isort check failed:\n{r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — Plugin contract tests
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_plugin_contracts():
    """Repo's plugin contract tests pass (pass_to_pass)."""
    # Install required dependencies for plugin contract tests
    deps = ["pytest", "pybase64", "aiohttp", "pylatexenc", "torch"]
    r = subprocess.run(
        ["pip", "install"] + deps + ["-q"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    # Also install torch CPU version
    subprocess.run(
        ["pip", "install", "torch", "--index-url", "https://download.pytorch.org/whl/cpu", "-q"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    r = subprocess.run(
        ["python", "-m", "pytest", "tests/plugin_contracts/", "-v", "--tb=short"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Plugin contract tests failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_vision_info_base64():
    """process_vision_info returns PIL images from base64 strings without qwen_vl_utils."""
    from slime.utils.processing_utils import process_vision_info

    test_cases = [
        ("red", (8, 8)),
        ("blue", (16, 16)),
        ("green", (4, 12)),
    ]
    for color, size in test_cases:
        messages = [
            {"role": "user", "content": [
                {"type": "image", "image": _make_b64_image(color, size)},
                {"type": "text", "text": "Describe this image."},
            ]}
        ]
        result = process_vision_info(messages, _mock_processor())

        assert isinstance(result, dict)
        assert "images" in result and "videos" in result
        imgs = result["images"]
        assert imgs is not None and len(imgs) >= 1
        assert isinstance(imgs[0], Image.Image)
        assert imgs[0].size == size, f"Expected {size}, got {imgs[0].size}"


# [pr_diff] fail_to_pass
def test_vision_info_data_uri():
    """process_vision_info handles data:image/...;base64,... URIs."""
    from slime.utils.processing_utils import process_vision_info

    test_cases = [
        ("blue", (4, 4)),
        ("red", (10, 10)),
        ("yellow", (3, 7)),
    ]
    for color, size in test_cases:
        messages = [
            {"role": "user", "content": [
                {"type": "image", "image": _make_data_uri(color, size)},
            ]}
        ]
        result = process_vision_info(messages, _mock_processor())

        imgs = result.get("images")
        assert imgs is not None and len(imgs) >= 1
        assert isinstance(imgs[0], Image.Image)
        assert imgs[0].size == size, f"Expected {size}, got {imgs[0].size}"


# [pr_diff] fail_to_pass
def test_vision_info_pil_passthrough():
    """process_vision_info passes through PIL Image objects directly."""
    from slime.utils.processing_utils import process_vision_info

    sizes = [(6, 6), (12, 3), (1, 1)]
    for size in sizes:
        img = Image.new("RGB", size, color="green")
        messages = [
            {"role": "user", "content": [
                {"type": "image", "image": img},
            ]},
            {"role": "user", "content": "text only — should be skipped"},
            {"role": "user", "content": [
                {"type": "text", "text": "no images here"},
            ]},
        ]
        result = process_vision_info(messages, _mock_processor())

        imgs = result.get("images")
        assert imgs is not None and len(imgs) == 1
        assert isinstance(imgs[0], Image.Image)
        assert imgs[0].size == size, f"Expected {size}, got {imgs[0].size}"


# [pr_diff] fail_to_pass
def test_vision_info_multiple_images():
    """process_vision_info extracts multiple images across messages."""
    from slime.utils.processing_utils import process_vision_info

    messages = [
        {"role": "user", "content": [
            {"type": "image", "image": _make_b64_image("red", (4, 4))},
            {"type": "text", "text": "First image."},
        ]},
        {"role": "user", "content": [
            {"type": "image", "image": _make_b64_image("blue", (8, 8))},
            {"type": "image", "image": Image.new("RGB", (2, 2), color="yellow")},
        ]},
    ]
    result = process_vision_info(messages, _mock_processor())

    imgs = result.get("images")
    assert imgs is not None and len(imgs) == 3
    actual_sizes = sorted([im.size for im in imgs])
    assert actual_sizes == [(2, 2), (4, 4), (8, 8)], f"Unexpected sizes: {actual_sizes}"
    for im in imgs:
        assert isinstance(im, Image.Image)


# [pr_diff] fail_to_pass
def test_vision_info_no_images():
    """process_vision_info returns None/empty for messages with no image content."""
    from slime.utils.processing_utils import process_vision_info

    # Case 1: text-only content list
    messages = [
        {"role": "user", "content": [
            {"type": "text", "text": "Just text, no images."},
        ]},
    ]
    result = process_vision_info(messages, _mock_processor())
    assert isinstance(result, dict)
    assert "images" in result and "videos" in result
    assert result["images"] is None or result["images"] == []

    # Case 2: empty content list
    messages2 = [{"role": "user", "content": []}]
    result2 = process_vision_info(messages2, _mock_processor())
    assert result2["images"] is None or result2["images"] == []

    # Case 3: string content (not a list)
    messages3 = [{"role": "user", "content": "plain text message"}]
    result3 = process_vision_info(messages3, _mock_processor())
    assert result3["images"] is None or result3["images"] == []


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression checks
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_build_processor_kwargs():
    """build_processor_kwargs still works with and without multimodal inputs."""
    from slime.utils.processing_utils import build_processor_kwargs

    result = build_processor_kwargs(None)
    assert isinstance(result, dict)

    result2 = build_processor_kwargs({"images": ["fake"]})
    assert "images" in result2
    assert result2["images_kwargs"]["return_tensors"] == "pt"

    result3 = build_processor_kwargs({"images": ["a", "b"], "videos": ["c"]})
    assert "images" in result3 and "videos" in result3


# [pr_diff] pass_to_pass
def test_encode_image():
    """encode_image_for_rollout_engine still produces valid data URIs."""
    from slime.utils.processing_utils import encode_image_for_rollout_engine

    for color, size in [("red", (4, 4)), ("blue", (10, 10)), ("green", (1, 1))]:
        img = Image.new("RGB", size, color=color)
        result = encode_image_for_rollout_engine(img)
        assert result.startswith("data:image/png;base64,")
        # Round-trip: decode and verify size matches
        b64_part = result.split(",", 1)[1]
        decoded = Image.open(io.BytesIO(base64.b64decode(b64_part)))
        assert decoded.size == size, f"Round-trip size mismatch: {decoded.size} != {size}"


# ---------------------------------------------------------------------------
# Structural (pr_diff) — AST checks for files with heavy deps
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_actor_numpy_handling():
    """actor.py must handle numpy arrays in multimodal_train_inputs.

    AST-only because: actor.py requires ray, torch.distributed, megatron — cannot import.
    """
    source = Path(f"{REPO}/slime/backends/megatron_utils/actor.py").read_text()
    tree = ast.parse(source)

    has_numpy_import = False
    has_numpy_conversion = False

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if "numpy" in alias.name:
                    has_numpy_import = True
        if isinstance(node, ast.ImportFrom) and node.module and "numpy" in node.module:
            has_numpy_import = True

        if isinstance(node, ast.Call):
            # isinstance(..., np.ndarray)
            if isinstance(node.func, ast.Name) and node.func.id == "isinstance" and len(node.args) >= 2:
                arg2 = node.args[1]
                if isinstance(arg2, ast.Attribute) and arg2.attr == "ndarray":
                    has_numpy_conversion = True
                if isinstance(arg2, ast.Tuple):
                    for elt in arg2.elts:
                        if isinstance(elt, ast.Attribute) and elt.attr == "ndarray":
                            has_numpy_conversion = True
            # torch.from_numpy() or torch.as_tensor()
            if isinstance(node.func, ast.Attribute) and node.func.attr in ("from_numpy", "as_tensor"):
                has_numpy_conversion = True

    assert has_numpy_import, "No numpy import found in actor.py"
    assert has_numpy_conversion, "No numpy array handling found in actor.py"


# [pr_diff] fail_to_pass
def test_sglang_safe_multimodal_access():
    """sglang_rollout.py must use safe access for multimodal_inputs['images'].

    AST-only because: sglang_rollout.py requires sglang async server internals — cannot import.
    """
    source = Path(f"{REPO}/slime/rollout/sglang_rollout.py").read_text()
    tree = ast.parse(source)

    found_safe = False
    for node in ast.walk(tree):
        # .get("images")
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "get":
            for arg in node.args:
                if isinstance(arg, ast.Constant) and arg.value == "images":
                    found_safe = True
        # "images" in ...
        if isinstance(node, ast.Compare) and isinstance(node.left, ast.Constant) and node.left.value == "images":
            if any(isinstance(op, ast.In) for op in node.ops):
                found_safe = True

    assert found_safe, "No safe access pattern for 'images' key in sglang_rollout.py"
