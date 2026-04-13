"""
Task: transformers-sizedict-get-size-dict-input
Repo: huggingface/transformers @ a8683756653094e3fc3016df8abcdeaaec758f9a
PR:   44903

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/repo"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """image_processing_utils.py must parse without syntax errors."""
    r = subprocess.run(
        ["python3", "-c", "import py_compile; py_compile.compile('src/transformers/image_processing_utils.py', doraise=True)"],
        cwd=REPO, capture_output=True, text=True,
    )
    assert r.returncode == 0, f"Syntax error:\n{r.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_sizedict_height_width():
    """get_size_dict accepts SizeDict with height/width and returns a plain dict."""
    r = subprocess.run(
        ["python3", "-c", """
from transformers.image_utils import SizeDict
from transformers.image_processing_utils import get_size_dict

sd = SizeDict(height=224, width=224)
result = get_size_dict(sd)
assert isinstance(result, dict), f'Expected dict, got {type(result)}'
assert not isinstance(result, SizeDict), 'Should be plain dict, not SizeDict'
assert result == {'height': 224, 'width': 224}, f'Wrong value: {result}'

# Vary input: different dimensions
sd2 = SizeDict(height=512, width=768)
result2 = get_size_dict(sd2)
assert isinstance(result2, dict) and not isinstance(result2, SizeDict)
assert result2 == {'height': 512, 'width': 768}, f'Wrong value: {result2}'
"""],
        cwd=REPO, capture_output=True, text=True,
    )
    assert r.returncode == 0, f"Failed:\n{r.stdout}\n{r.stderr}"


# [pr_diff] fail_to_pass
def test_sizedict_shortest_edge():
    """get_size_dict accepts SizeDict with shortest_edge key."""
    r = subprocess.run(
        ["python3", "-c", """
from transformers.image_utils import SizeDict
from transformers.image_processing_utils import get_size_dict

sd = SizeDict(shortest_edge=256)
result = get_size_dict(sd, default_to_square=False)
assert isinstance(result, dict), f'Expected dict, got {type(result)}'
assert result == {'shortest_edge': 256}, f'Wrong value: {result}'

# Vary: different value
sd2 = SizeDict(shortest_edge=384)
result2 = get_size_dict(sd2, default_to_square=False)
assert result2 == {'shortest_edge': 384}, f'Wrong value: {result2}'
"""],
        cwd=REPO, capture_output=True, text=True,
    )
    assert r.returncode == 0, f"Failed:\n{r.stdout}\n{r.stderr}"


# [pr_diff] fail_to_pass
def test_sizedict_shortest_longest_edge():
    """get_size_dict accepts SizeDict with shortest_edge + longest_edge."""
    r = subprocess.run(
        ["python3", "-c", """
from transformers.image_utils import SizeDict
from transformers.image_processing_utils import get_size_dict

sd = SizeDict(shortest_edge=800, longest_edge=1333)
result = get_size_dict(sd, default_to_square=False)
assert isinstance(result, dict), f'Expected dict, got {type(result)}'
assert result == {'shortest_edge': 800, 'longest_edge': 1333}, f'Wrong value: {result}'

# Vary: different values
sd2 = SizeDict(shortest_edge=600, longest_edge=1000)
result2 = get_size_dict(sd2, default_to_square=False)
assert result2 == {'shortest_edge': 600, 'longest_edge': 1000}, f'Wrong value: {result2}'
"""],
        cwd=REPO, capture_output=True, text=True,
    )
    assert r.returncode == 0, f"Failed:\n{r.stdout}\n{r.stderr}"


# [pr_diff] pass_to_pass
def test_sizedict_no_convert_fallthrough():
    """SizeDict input must not fall through to convert_to_size_dict path."""
    r = subprocess.run(
        ["python3", "-c", """
import logging, io
from transformers.image_utils import SizeDict
from transformers.image_processing_utils import get_size_dict

logger = logging.getLogger('transformers.image_processing_utils')
stream = io.StringIO()
sh = logging.StreamHandler(stream)
sh.setLevel(logging.DEBUG)
logger.addHandler(sh)
logger.setLevel(logging.DEBUG)

sd = SizeDict(height=224, width=224)
result = get_size_dict(sd)

log_output = stream.getvalue()
assert 'should be a dictionary' not in log_output, f'SizeDict fell through to convert path: {log_output}'
"""],
        cwd=REPO, capture_output=True, text=True,
    )
    assert r.returncode == 0, f"Failed:\n{r.stdout}\n{r.stderr}"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — regression tests
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_plain_dict_input():
    """get_size_dict still works with plain dict input."""
    r = subprocess.run(
        ["python3", "-c", """
from transformers.image_processing_utils import get_size_dict

result = get_size_dict({'height': 224, 'width': 224})
assert result == {'height': 224, 'width': 224}, f'Wrong: {result}'

result2 = get_size_dict({'shortest_edge': 256}, default_to_square=False)
assert result2 == {'shortest_edge': 256}, f'Wrong: {result2}'
"""],
        cwd=REPO, capture_output=True, text=True,
    )
    assert r.returncode == 0, f"Failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_int_input():
    """get_size_dict still works with int input."""
    r = subprocess.run(
        ["python3", "-c", """
from transformers.image_processing_utils import get_size_dict

result = get_size_dict(224)
assert result == {'height': 224, 'width': 224}, f'Wrong: {result}'

result2 = get_size_dict(256, default_to_square=False)
assert result2 == {'shortest_edge': 256}, f'Wrong: {result2}'
"""],
        cwd=REPO, capture_output=True, text=True,
    )
    assert r.returncode == 0, f"Failed:\n{r.stdout}\n{r.stderr}"


# [agent_config] pass_to_pass — AGENTS.md:2 @ a8683756653094e3fc3016df8abcdeaaec758f9a
def test_ruff_style_check():
    """image_processing_utils.py passes ruff linter (make style requirement)."""
    # Install ruff if not already present
    subprocess.run(
        ["pip", "install", "--quiet", "ruff"],
        cwd=REPO, capture_output=True,
    )
    r = subprocess.run(
        ["python3", "-m", "ruff", "check", "src/transformers/image_processing_utils.py"],
        cwd=REPO, capture_output=True, text=True,
    )
    assert r.returncode == 0, f"ruff style violations:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_tuple_input():
    """get_size_dict still works with tuple input."""
    r = subprocess.run(
        ["python3", "-c", """
from transformers.image_processing_utils import get_size_dict

result = get_size_dict((384, 512))
assert result == {'height': 384, 'width': 512}, f'Wrong: {result}'

result2 = get_size_dict((224, 224))
assert result2 == {'height': 224, 'width': 224}, f'Wrong: {result2}'
"""],
        cwd=REPO, capture_output=True, text=True,
    )
    assert r.returncode == 0, f"Failed:\n{r.stdout}\n{r.stderr}"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD checks from the repo's Makefile
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass — Repo unittest for image_processing_utils
def test_repo_unittest_image_processing_utils():
    """Repo's unittest for image_processing_utils passes (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-m", "unittest", "tests.utils.test_image_processing_utils.ImageProcessingUtilsTester.test_get_size_dict", "-v"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Repo unittest failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — Makefile style check: ruff
def test_repo_ruff_check():
    """Repo ruff linter check passes on image_processing_utils.py (pass_to_pass)."""
    # Install ruff if not already present
    subprocess.run(
        ["pip", "install", "--quiet", "ruff"],
        cwd=REPO, capture_output=True,
    )
    r = subprocess.run(
        ["python3", "-m", "ruff", "check", "src/transformers/image_processing_utils.py"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"ruff check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass — Check that image_processing_utils.py has valid Python syntax
def test_repo_python_syntax():
    """Repo image_processing_utils.py has valid Python syntax (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-m", "py_compile", "src/transformers/image_processing_utils.py"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Syntax check failed:\n{r.stderr}"


# [repo_tests] pass_to_pass — Check that image_utils can be imported and SizeDict works
def test_repo_sizedict_import():
    """Repo SizeDict can be imported from image_utils (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", "from transformers.image_utils import SizeDict; print('SizeDict imported successfully')"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"SizeDict import failed:\n{r.stderr}"


# [repo_tests] pass_to_pass — Type checker (ty) from Makefile: make typing
def test_repo_typing_check():
    """Repo type checker passes on image_processing_utils.py (pass_to_pass)."""
    # Install ty if not already present
    subprocess.run(
        ["pip", "install", "--quiet", "ty"],
        cwd=REPO, capture_output=True,
    )
    r = subprocess.run(
        ["python3", "utils/check_types.py", "src/transformers/image_processing_utils.py"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Type check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass — Check convert_to_size_dict function
def test_repo_convert_to_size_dict():
    """Repo convert_to_size_dict function works with various inputs (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", """
from transformers.image_processing_utils import convert_to_size_dict

# Test int with default_to_square=True
result = convert_to_size_dict(224, default_to_square=True)
assert result == {'height': 224, 'width': 224}, f'Failed: {result}'

# Test int with default_to_square=False
result = convert_to_size_dict(256, default_to_square=False)
assert result == {'shortest_edge': 256}, f'Failed: {result}'

# Test tuple input
result = convert_to_size_dict((300, 400), height_width_order=True)
assert result == {'height': 300, 'width': 400}, f'Failed: {result}'

# Test None input
result = convert_to_size_dict(None, max_size=512, default_to_square=False)
assert result == {'longest_edge': 512}, f'Failed: {result}'

print('convert_to_size_dict tests passed')
"""],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"convert_to_size_dict test failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass — Run all ImageProcessingUtilsTester tests via unittest
def test_repo_image_processing_utils_all():
    """Repo's ImageProcessingUtilsTester passes (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-m", "unittest", "tests.utils.test_image_processing_utils.ImageProcessingUtilsTester", "-v"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"ImageProcessingUtilsTester failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — Check get_size_dict with max_size parameter
def test_repo_get_size_dict_max_size():
    """Repo get_size_dict handles max_size parameter correctly (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", """
from transformers.image_processing_utils import get_size_dict

# Test int with max_size and default_to_square=False
result = get_size_dict(224, max_size=256, default_to_square=False)
assert result == {'shortest_edge': 224, 'longest_edge': 256}, f'Failed: {result}'

# Test None with max_size and default_to_square=False
result = get_size_dict(None, max_size=512, default_to_square=False)
assert result == {'longest_edge': 512}, f'Failed: {result}'

print('get_size_dict max_size tests passed')
"""],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"get_size_dict max_size test failed:\n{r.stdout}\n{r.stderr}"
