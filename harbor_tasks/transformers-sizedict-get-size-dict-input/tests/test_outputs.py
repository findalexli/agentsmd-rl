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
