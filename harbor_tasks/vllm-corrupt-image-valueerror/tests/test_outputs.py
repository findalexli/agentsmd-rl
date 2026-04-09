"""
Task: vllm-corrupt-image-valueerror
Repo: vllm-project/vllm @ 3683fe6c0651fe54a0201552ae7dfb7acb1e0cea
PR:   #38253

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import sys
import tempfile
from io import BytesIO
from pathlib import Path
from unittest.mock import MagicMock

from PIL import Image

REPO = "/testbed"
SOURCE = f"{REPO}/vllm/multimodal/media/image.py"


# ---------------------------------------------------------------------------
# Helpers — load the module under test with mocked heavy deps
# ---------------------------------------------------------------------------

def _load_image_media_io():
    """Exec image.py with heavy deps mocked, return ImageMediaIO class."""
    heavy_mods = [
        "torch", "torch.sparse", "torch.nn", "torch.nn.functional",
        "numpy", "numpy.core",
        "vllm", "vllm.utils", "vllm.utils.serial_utils",
        "vllm.multimodal", "vllm.multimodal.media",
    ]
    for mod in heavy_mods:
        sys.modules.setdefault(mod, MagicMock())

    import pybase64
    sys.modules["pybase64"] = pybase64

    class _MediaIO:
        def __init__(self): pass
        def __class_getitem__(cls, item): return cls

    class _MediaWithBytes:
        def __init__(self, media, data):
            self.media = media
            self.data = data
        def __class_getitem__(cls, item): return cls

    def _convert_image_mode_fn(image, mode):
        return image.convert(mode)

    def _rgba_to_rgb(image, bg):
        bg_img = Image.new("RGB", image.size, bg)
        bg_img.paste(image, mask=image.split()[3])
        return bg_img

    try:
        from PIL import UnidentifiedImageError
    except ImportError:
        UnidentifiedImageError = Exception

    source = Path(SOURCE).read_text()
    lines = source.split("\n")
    skip_prefixes = (
        "import torch", "from torch",
        "import numpy", "from numpy",
        "import vllm", "from vllm",
        "import pybase64", "from pybase64",
        "from ..", "from .",
    )
    filtered = [l for l in lines if not any(l.strip().startswith(p) for p in skip_prefixes)]

    ns = {
        "__builtins__": __builtins__,
        "BytesIO": BytesIO,
        "Path": Path,
        "Image": Image,
        "UnidentifiedImageError": UnidentifiedImageError,
        "pybase64": pybase64,
        "np": MagicMock(),
        "torch": MagicMock(),
        "convert_image_mode": _convert_image_mode_fn,
        "rgba_to_rgb": _rgba_to_rgb,
        "MediaIO": _MediaIO,
        "MediaWithBytes": _MediaWithBytes,
        "tensor2base64": lambda x: "",
        "MAGIC_NUMPY_PREFIX": b"\x93NUMPY",
    }
    exec("\n".join(filtered), ns)
    return ns["ImageMediaIO"]()


# Module-level fixture (shared across tests, but stateless)
_io = _load_image_media_io()

# --- Test image data ---
_valid_img = Image.new("RGB", (8, 8), (100, 150, 200))
_buf_png = BytesIO(); _valid_img.save(_buf_png, format="PNG"); VALID_PNG = _buf_png.getvalue()
_buf_jpg = BytesIO(); _valid_img.save(_buf_jpg, format="JPEG"); VALID_JPEG = _buf_jpg.getvalue()

TRUNCATED_PNG = VALID_PNG[: len(VALID_PNG) // 2]
TRUNCATED_JPEG = VALID_JPEG[: len(VALID_JPEG) // 2]
GARBAGE_BYTES = b"not an image at all \x00\xff\xfe"
EMPTY_BYTES = b""


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified source file must be valid Python."""
    import py_compile
    py_compile.compile(SOURCE, doraise=True)


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — Repo CI checks must pass on base commit
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_ruff_check():
    """Modified file passes ruff linting (pass_to_pass)."""
    r = subprocess.run(
        ["python", "-m", "ruff", "check", SOURCE],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_ruff_format():
    """Modified file passes ruff format check (pass_to_pass)."""
    r = subprocess.run(
        ["python", "-m", "ruff", "format", "--check", SOURCE],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stdout}\n{r.stderr}"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — valid images still load correctly
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_load_bytes_valid_png():
    """load_bytes returns a correctly-sized image for valid PNG data."""
    result = _io.load_bytes(VALID_PNG)
    assert hasattr(result, "media"), "Expected MediaWithBytes with .media attribute"
    assert result.media.size == (8, 8), f"Expected (8,8), got {result.media.size}"


# [pr_diff] pass_to_pass
def test_load_bytes_valid_jpeg():
    """load_bytes returns a correctly-sized image for valid JPEG data."""
    result = _io.load_bytes(VALID_JPEG)
    assert hasattr(result, "media"), "Expected MediaWithBytes with .media attribute"
    assert result.media.size == (8, 8), f"Expected (8,8), got {result.media.size}"


# [pr_diff] pass_to_pass
def test_load_file_valid():
    """load_file returns a correctly-sized image for a valid PNG file."""
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        f.write(VALID_PNG)
        f.flush()
        result = _io.load_file(Path(f.name))
    assert hasattr(result, "media"), "Expected MediaWithBytes with .media attribute"
    assert result.media.size == (8, 8), f"Expected (8,8), got {result.media.size}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — corrupt inputs must raise ValueError
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_load_bytes_garbage_raises_valueerror():
    """load_bytes raises ValueError for random non-image bytes."""
    import pytest
    with pytest.raises(ValueError):
        _io.load_bytes(GARBAGE_BYTES)


# [pr_diff] fail_to_pass
def test_load_bytes_truncated_png_raises_valueerror():
    """load_bytes raises ValueError for a truncated PNG."""
    import pytest
    with pytest.raises(ValueError):
        _io.load_bytes(TRUNCATED_PNG)


# [pr_diff] fail_to_pass
def test_load_bytes_truncated_jpeg_raises_valueerror():
    """load_bytes raises ValueError for a truncated JPEG."""
    import pytest
    with pytest.raises(ValueError):
        _io.load_bytes(TRUNCATED_JPEG)


# [pr_diff] fail_to_pass
def test_load_bytes_empty_raises_valueerror():
    """load_bytes raises ValueError for empty bytes."""
    import pytest
    with pytest.raises(ValueError):
        _io.load_bytes(EMPTY_BYTES)


# [pr_diff] fail_to_pass
def test_load_file_garbage_raises_valueerror():
    """load_file raises ValueError for a file containing garbage data."""
    import pytest
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        f.write(GARBAGE_BYTES)
        f.flush()
        with pytest.raises(ValueError):
            _io.load_file(Path(f.name))


# [pr_diff] fail_to_pass
def test_load_file_truncated_raises_valueerror():
    """load_file raises ValueError for a file containing truncated image data."""
    import pytest
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        f.write(TRUNCATED_PNG)
        f.flush()
        with pytest.raises(ValueError):
            _io.load_file(Path(f.name))
