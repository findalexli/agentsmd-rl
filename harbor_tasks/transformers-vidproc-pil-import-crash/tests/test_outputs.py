"""
Task: transformers-vidproc-pil-import-crash
Repo: huggingface/transformers @ ed003b4482aabdf8377250f22826dd31f378269c
PR:   44941

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import sys
from pathlib import Path

REPO = "/repo"
TARGET = f"{REPO}/src/transformers/video_processing_utils.py"


def _run(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Run Python code in a subprocess (avoids import caching across tests)."""
    return subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True, text=True, timeout=timeout,
        cwd=REPO, env={"PYTHONPATH": f"{REPO}/src", "PATH": "/usr/bin:/bin:/usr/local/bin"},
    )


def _ensure_no_pil():
    subprocess.run(
        [sys.executable, "-m", "pip", "uninstall", "-y", "Pillow", "pillow"],
        capture_output=True, timeout=30,
    )


def _ensure_pil():
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "-q", "Pillow"],
        capture_output=True, timeout=60,
    )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax check
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """video_processing_utils.py must be valid Python."""
    r = subprocess.run(
        [sys.executable, "-c", f"import py_compile; py_compile.compile({TARGET!r}, doraise=True)"],
        capture_output=True, text=True, timeout=15,
    )
    assert r.returncode == 0, f"Syntax error:\n{r.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests (no PIL)
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_import_without_pil():
    """Module imports without PIL; BaseVideoProcessor has correct class attributes."""
    _ensure_no_pil()
    r = _run("""
import sys
# Confirm PIL is absent
try:
    import PIL
    sys.exit(1)
except ImportError:
    pass

from transformers.video_processing_utils import BaseVideoProcessor

# Anti-stub: verify real class attributes
assert BaseVideoProcessor.rescale_factor == 1/255, f'wrong rescale_factor: {BaseVideoProcessor.rescale_factor}'
assert BaseVideoProcessor.model_input_names == ['pixel_values_videos'], f'wrong model_input_names'
assert BaseVideoProcessor.default_to_square is True, 'wrong default_to_square'
assert BaseVideoProcessor.return_metadata is False, 'wrong return_metadata'
""")
    assert r.returncode == 0, f"Import without PIL failed:\n{r.stdout}\n{r.stderr}"


# [pr_diff] fail_to_pass
def test_docstring_constant_without_pil():
    """BASE_VIDEO_PROCESSOR_DOCSTRING accessible and non-trivial without PIL."""
    _ensure_no_pil()
    r = _run("""
from transformers.video_processing_utils import BASE_VIDEO_PROCESSOR_DOCSTRING
assert isinstance(BASE_VIDEO_PROCESSOR_DOCSTRING, str), 'not a string'
assert 'do_resize' in BASE_VIDEO_PROCESSOR_DOCSTRING, 'missing do_resize'
assert 'do_normalize' in BASE_VIDEO_PROCESSOR_DOCSTRING, 'missing do_normalize'
assert 'resample' in BASE_VIDEO_PROCESSOR_DOCSTRING, 'missing resample'
assert len(BASE_VIDEO_PROCESSOR_DOCSTRING) > 500, f'too short: {len(BASE_VIDEO_PROCESSOR_DOCSTRING)}'
""")
    assert r.returncode == 0, f"Docstring constant failed:\n{r.stdout}\n{r.stderr}"


# [pr_diff] fail_to_pass
def test_methods_exist_without_pil():
    """Key methods on BaseVideoProcessor present; __call__ delegates to preprocess."""
    _ensure_no_pil()
    r = _run("""
import inspect
from transformers.video_processing_utils import BaseVideoProcessor

required = ['preprocess', '_preprocess', 'sample_frames', 'to_dict', 'from_dict',
            'from_pretrained', 'save_pretrained', 'to_json_string']
for m in required:
    assert hasattr(BaseVideoProcessor, m), f'Missing method: {m}'

src = inspect.getsource(BaseVideoProcessor.__call__)
assert 'preprocess' in src, '__call__ does not delegate to preprocess'
""")
    assert r.returncode == 0, f"Method check failed:\n{r.stdout}\n{r.stderr}"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_pil_resampling_with_pil():
    """PILImageResampling available in module namespace when PIL IS installed."""
    _ensure_pil()
    r = _run("""
import transformers.video_processing_utils as vpu
assert hasattr(vpu, 'PILImageResampling'), 'PILImageResampling not in module namespace with PIL'
from transformers.image_utils import PILImageResampling
assert vpu.PILImageResampling is PILImageResampling, 'PILImageResampling mismatch'
""")
    assert r.returncode == 0, f"PILImageResampling with PIL failed:\n{r.stdout}\n{r.stderr}"


# [pr_diff] pass_to_pass
def test_other_image_utils_imports():
    """Other image_utils imports (ChannelDimension, SizeDict) unaffected."""
    _ensure_pil()
    r = _run("""
from transformers.video_processing_utils import BaseVideoProcessor
from transformers.image_utils import ChannelDimension, SizeDict
assert ChannelDimension is not None
assert SizeDict is not None
""")
    assert r.returncode == 0, f"Other imports failed:\n{r.stdout}\n{r.stderr}"


# [static] pass_to_pass
def test_not_stub():
    """File not emptied/stubbed — retains substantial content and key definitions."""
    content = Path(TARGET).read_text()
    assert len(content) > 8000, f"File too short ({len(content)} chars), likely stubbed"
    assert "class BaseVideoProcessor" in content, "BaseVideoProcessor class missing"
    assert "def preprocess" in content, "preprocess method missing"
    assert "def _preprocess" in content, "_preprocess method missing"
    assert "def sample_frames" in content, "sample_frames method missing"
    assert "BASE_VIDEO_PROCESSOR_DOCSTRING" in content, "docstring constant missing"


# ---------------------------------------------------------------------------
# Repo CI/CD pass-to-pass gates
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass — ruff linting
def test_repo_ruff_check():
    """Repo's ruff linting passes on the target file (pass_to_pass)."""
    r = subprocess.run(
        [sys.executable, "-m", "pip", "install", "-q", "ruff"],
        capture_output=True, timeout=30,
    )
    r = subprocess.run(
        [sys.executable, "-m", "ruff", "check", TARGET],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass — ruff formatting
def test_repo_ruff_format():
    """Repo's ruff formatting passes on the target file (pass_to_pass)."""
    r = subprocess.run(
        [sys.executable, "-m", "pip", "install", "-q", "ruff"],
        capture_output=True, timeout=30,
    )
    r = subprocess.run(
        [sys.executable, "-m", "ruff", "format", "--check", TARGET],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass — modeling structure check
def test_repo_modeling_structure():
    """Repo's modeling structure check passes (pass_to_pass)."""
    r = subprocess.run(
        [sys.executable, "utils/check_modeling_structure.py"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Modeling structure check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — inits check
def test_repo_inits():
    """Repo's __init__ structure check passes (pass_to_pass)."""
    r = subprocess.run(
        [sys.executable, "utils/check_inits.py"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Init check failed:\n{r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — CLAUDE.md rules
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — CLAUDE.md:66 @ ed003b4482aabdf8377250f22826dd31f378269c
def test_copied_from_annotations_intact():
    """'# Copied from' annotations must not be broken or removed."""
    import re
    content = Path(TARGET).read_text()
    for line in content.splitlines():
        if "# Copied from" in line:
            assert re.search(r"# Copied from transformers\.", line), f"Broken annotation: {line}"
