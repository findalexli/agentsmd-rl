"""
Task: transformers-sizedict-or-operator
Repo: huggingface/transformers @ b7164eca8675e5223cf73fb430a6aaf6ceafc9cc
PR:   44884

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import os
import subprocess

REPO = "/repo"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """image_utils.py must parse without syntax errors."""
    r = subprocess.run(
        ["python3", "-c", "import py_compile; py_compile.compile('src/transformers/image_utils.py', doraise=True)"],
        cwd=REPO, capture_output=True, timeout=30,
    )
    assert r.returncode == 0, f"Syntax error in image_utils.py:\n{r.stderr.decode()}"


# [repo_tests] pass_to_pass — repo CI syntax validation
def test_repo_import_check():
    """Transformers module can be imported without syntax errors (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", "from transformers.image_utils import SizeDict; print('Import OK')"],
        capture_output=True, text=True, timeout=30, cwd=REPO, env={**os.environ, "PYTHONPATH": f"{REPO}/src"},
    )
    assert r.returncode == 0, f"Import failed:\n{r.stderr}"


# [repo_tests] pass_to_pass — basic SizeDict functionality
def test_repo_sizedict_basic():
    """SizeDict basic operations work (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", """
import sys
sys.path.insert(0, 'src')
from transformers.image_utils import SizeDict

# Test basic instantiation
sd = SizeDict(height=10, width=20)
assert sd.height == 10 and sd.width == 20

# Test dict conversion
d = dict(sd)
assert d == {'height': 10, 'width': 20}

# Test equality with dict
assert sd == {'height': 10, 'width': 20}

# Test __getitem__ and __contains__
assert sd['height'] == 10
assert 'height' in sd
assert 'longest_edge' not in sd

print('SizeDict basic operations OK')
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"SizeDict basic test failed:\n{r.stderr}\n{r.stdout}"


# [repo_tests] pass_to_pass — AST parsing of image_utils.py
def test_repo_image_utils_ast():
    """image_utils.py parses without AST errors (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", "import ast; ast.parse(open('src/transformers/image_utils.py').read()); print('AST OK')"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"AST parsing failed:\n{r.stderr}"


# [repo_tests] pass_to_pass — get_size_dict integration with SizeDict
def test_repo_get_size_dict():
    """get_size_dict works and returns compatible dict (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", """
import sys
sys.path.insert(0, 'src')
from transformers.image_processing_utils import get_size_dict
from transformers.image_utils import SizeDict

# Test get_size_dict returns dict that works with SizeDict
size_dict = get_size_dict((224, 224), default_to_square=True, param_name="size")
sd = SizeDict(**size_dict)
assert sd.height == 224
assert sd.width == 224

# Test get_size_dict with non-square
size_dict2 = get_size_dict((128, 256), default_to_square=False, param_name="size")
sd2 = SizeDict(**size_dict2)
assert sd2.height == 128
assert sd2.width == 256

print('get_size_dict integration OK')
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"get_size_dict test failed:\n{r.stderr}\n{r.stdout}"


# [repo_tests] pass_to_pass — SizeDict attribute access
def test_repo_sizedict_attributes():
    """SizeDict attribute access works for all standard fields (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", """
import sys
sys.path.insert(0, 'src')
from transformers.image_utils import SizeDict

# Test all standard SizeDict fields
sd = SizeDict(height=10, width=20, longest_edge=30, shortest_edge=5, max_height=100, max_width=200)
assert sd.height == 10
assert sd.width == 20
assert sd.longest_edge == 30
assert sd.shortest_edge == 5
assert sd.max_height == 100
assert sd.max_width == 200

# Test setting attributes
sd.height = 50
assert sd.height == 50
sd['width'] = 60
assert sd.width == 60

print('SizeDict attributes OK')
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"SizeDict attributes test failed:\n{r.stderr}\n{r.stdout}"


# [repo_tests] pass_to_pass — ruff lint check
def test_repo_ruff_check():
    """Repo CI: ruff check passes on image_utils.py (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-m", "pip", "install", "ruff", "-q"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    r = subprocess.run(
        ["ruff", "check", "src/transformers/image_utils.py"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"ruff check failed:\n{r.stderr}\n{r.stdout}"




# [repo_tests] pass_to_pass — ruff format check
def test_repo_ruff_format():
    """Repo CI: ruff format check passes on image_utils.py (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-m", "pip", "install", "ruff", "-q"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    r = subprocess.run(
        ["ruff", "format", "--check", "src/transformers/image_utils.py"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"ruff format check failed:\n{r.stderr}\n{r.stdout}"


# [repo_tests] pass_to_pass — ty type check on image_utils
def test_repo_typing_check():
    """Repo CI: ty type checker runs on image_utils.py without errors (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-m", "pip", "install", "ty", "-q"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    r = subprocess.run(
        ["python3", "-m", "ty", "check", "src/transformers/image_utils.py"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    # ty returns 0 or 1 depending on diagnostics, we just check it runs without crashing
    assert r.returncode in [0, 1], f"ty check crashed:\n{r.stderr}"


# [repo_tests] pass_to_pass — SizeDict pickling
def test_repo_sizedict_pickle():
    """SizeDict can be pickled and unpickled (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", """
import sys
import pickle
sys.path.insert(0, 'src')
from transformers.image_utils import SizeDict

sd = SizeDict(height=10, width=20, longest_edge=30)

# Test pickling
pickled = pickle.dumps(sd)
unpickled = pickle.loads(pickled)

assert unpickled.height == 10
assert unpickled.width == 20
assert unpickled.longest_edge == 30
assert isinstance(unpickled, SizeDict)

print('SizeDict pickle OK')
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"SizeDict pickle test failed:\n{r.stderr}\n{r.stdout}"


# [repo_tests] pass_to_pass — SizeDict repr
def test_repo_sizedict_repr():
    """SizeDict repr is valid and can be eval'd back (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", """
import sys
sys.path.insert(0, 'src')
from transformers.image_utils import SizeDict

sd = SizeDict(height=10, width=20)
repr_str = repr(sd)

# Check repr contains expected fields
assert 'SizeDict' in repr_str
assert 'height=10' in repr_str or 'height=10,' in repr_str or 'height=10 ' in repr_str

print('SizeDict repr OK')
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"SizeDict repr test failed:\n{r.stderr}\n{r.stdout}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_sizedict_or_dict():
    """SizeDict | dict returns a SizeDict with all fields merged."""
    from transformers.image_utils import SizeDict

    # Case 1: basic merge
    sd = SizeDict(height=10, width=20)
    result = sd | {"longest_edge": 30}
    assert isinstance(result, SizeDict), f"Expected SizeDict, got {type(result)}"
    assert result.height == 10
    assert result.width == 20
    assert result.longest_edge == 30

    # Case 2: different values
    sd2 = SizeDict(height=100, width=200, longest_edge=300)
    result2 = sd2 | {"shortest_edge": 50}
    assert isinstance(result2, SizeDict)
    assert result2.height == 100
    assert result2.shortest_edge == 50

    # Case 3: empty dict merge preserves original
    sd3 = SizeDict(height=5, width=15)
    result3 = sd3 | {}
    assert isinstance(result3, SizeDict)
    assert result3.height == 5
    assert result3.width == 15


# [pr_diff] fail_to_pass
def test_dict_or_sizedict():
    """dict | SizeDict returns a plain dict with all entries merged."""
    from transformers.image_utils import SizeDict

    # Case 1: basic merge
    sd = SizeDict(height=10, width=20)
    result = {"longest_edge": 30} | sd
    assert isinstance(result, dict), f"Expected dict, got {type(result)}"
    assert not isinstance(result, SizeDict), "Should be plain dict, not SizeDict"
    assert result == {"longest_edge": 30, "height": 10, "width": 20}

    # Case 2: override semantics (right side wins)
    sd2 = SizeDict(height=99, width=88)
    result2 = {"height": 1, "longest_edge": 50} | sd2
    assert isinstance(result2, dict)
    assert result2["height"] == 99, "Right side should override left"
    assert result2["longest_edge"] == 50

    # Case 3: empty dict on left
    sd3 = SizeDict(height=42, width=84)
    result3 = {} | sd3
    assert isinstance(result3, dict)
    assert result3 == {"height": 42, "width": 84}


# [pr_diff] fail_to_pass
def test_sizedict_or_sizedict():
    """SizeDict | SizeDict returns a merged SizeDict."""
    from transformers.image_utils import SizeDict

    # Case 1: non-overlapping fields
    sd1 = SizeDict(height=10, width=20)
    sd2 = SizeDict(longest_edge=30)
    result = sd1 | sd2
    assert isinstance(result, SizeDict), f"Expected SizeDict, got {type(result)}"
    assert result.height == 10
    assert result.width == 20
    assert result.longest_edge == 30

    # Case 2: overlapping fields (right wins)
    sd3 = SizeDict(height=100, width=200)
    sd4 = SizeDict(height=999, shortest_edge=50)
    result2 = sd3 | sd4
    assert isinstance(result2, SizeDict)
    assert result2.height == 999
    assert result2.width == 200
    assert result2.shortest_edge == 50

    # Case 3: identical SizeDicts
    sd5 = SizeDict(height=7, width=14)
    result3 = sd5 | sd5
    assert isinstance(result3, SizeDict)
    assert result3.height == 7
    assert result3.width == 14


# [pr_diff] fail_to_pass
def test_or_override_conflict():
    """Right-side values override left-side on key conflict."""
    from transformers.image_utils import SizeDict

    sd = SizeDict(height=10, width=20)
    result = sd | {"height": 50, "longest_edge": 100}
    assert isinstance(result, SizeDict)
    assert result.height == 50, f"Expected overridden height=50, got {result.height}"
    assert result.width == 20
    assert result.longest_edge == 100

    # SizeDict | SizeDict override
    sd2 = SizeDict(height=999)
    result2 = sd | sd2
    assert result2.height == 999


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — behavior preserved after fix
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_or_unsupported_type():
    """SizeDict | <non-dict> raises TypeError via NotImplemented."""
    from transformers.image_utils import SizeDict
    import pytest

    sd = SizeDict(height=10, width=20)
    with pytest.raises(TypeError):
        sd | 42
    with pytest.raises(TypeError):
        sd | [1, 2, 3]
    with pytest.raises(TypeError):
        sd | "string"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — regression checks
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_equality_with_dict():
    """SizeDict equality comparison with dict still works."""
    from transformers.image_utils import SizeDict

    sd = SizeDict(height=224, width=224)
    assert sd == {"height": 224, "width": 224}
    assert sd != {"height": 224, "width": 999}


# [repo_tests] pass_to_pass
def test_getitem_and_contains():
    """SizeDict __getitem__ and __contains__ still work."""
    from transformers.image_utils import SizeDict

    sd = SizeDict(height=224, width=224)
    assert sd["height"] == 224
    assert "height" in sd
    assert "longest_edge" not in sd


# [repo_tests] pass_to_pass
def test_dict_conversion():
    """SizeDict dict() conversion still works."""
    from transformers.image_utils import SizeDict

    sd = SizeDict(height=10, width=20, longest_edge=30)
    d = dict(sd)
    assert d == {"height": 10, "width": 20, "longest_edge": 30}


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from agent config files
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — .github/copilot-instructions.md:15 @ b7164eca8675e5223cf73fb430a6aaf6ceafc9cc
def test_minimal_diff():
    """Fix should be brief — fewer than 40 lines of non-comment code added."""
    r = subprocess.run(["git", "diff", "HEAD"], capture_output=True, text=True, cwd=REPO)
    diff = r.stdout
    if not diff:
        r = subprocess.run(["git", "diff", "--cached"], capture_output=True, text=True, cwd=REPO)
        diff = r.stdout
    if not diff:
        r = subprocess.run(["git", "diff", "HEAD~1"], capture_output=True, text=True, cwd=REPO)
        diff = r.stdout

    added = [l for l in diff.splitlines() if l.startswith("+") and not l.startswith("+++")]
    code_added = [l for l in added if l.strip("+").strip() and not l.strip("+").strip().startswith("#")]
    assert len(code_added) < 40, f"Too many lines added ({len(code_added)}), fix should be minimal"


# [agent_config] pass_to_pass — .github/copilot-instructions.md:15 @ b7164eca8675e5223cf73fb430a6aaf6ceafc9cc
def test_minimal_files_changed():
    """Only image_utils.py (and optionally one test file) should be modified."""
    r = subprocess.run(["git", "diff", "--name-only", "HEAD"], capture_output=True, text=True, cwd=REPO)
    files = r.stdout.strip()
    if not files:
        r = subprocess.run(["git", "diff", "--name-only", "--cached"], capture_output=True, text=True, cwd=REPO)
        files = r.stdout.strip()
    if not files:
        r = subprocess.run(["git", "diff", "--name-only", "HEAD~1"], capture_output=True, text=True, cwd=REPO)
        files = r.stdout.strip()

    changed = [f for f in files.splitlines() if f.strip()]
    assert len(changed) <= 2, f"Too many files changed ({len(changed)}): {changed}"


# [agent_config] pass_to_pass — .ai/skills/add-or-fix-type-checking/SKILL.md:180-186 @ b7164eca8675e5223cf73fb430a6aaf6ceafc9cc
def test_no_bare_type_ignore():
    """No bare '# type: ignore' without specific error code in added lines."""
    r = subprocess.run(["git", "diff", "HEAD"], capture_output=True, text=True, cwd=REPO)
    diff = r.stdout
    if not diff:
        r = subprocess.run(["git", "diff", "--cached"], capture_output=True, text=True, cwd=REPO)
        diff = r.stdout
    if not diff:
        r = subprocess.run(["git", "diff", "HEAD~1"], capture_output=True, text=True, cwd=REPO)
        diff = r.stdout

    added_lines = [l for l in diff.splitlines() if l.startswith("+") and not l.startswith("+++")]
    for line in added_lines:
        content = line[1:]  # strip leading '+'
        if "# type: ignore" in content and "# type: ignore[" not in content:
            assert False, f"Bare '# type: ignore' found (must specify error code): {content.strip()}"


# [agent_config] pass_to_pass — .github/copilot-instructions.md:16 @ b7164eca8675e5223cf73fb430a6aaf6ceafc9cc
def test_no_new_test_files():
    """Tests must be added to existing test files, not new ones."""
    r = subprocess.run(["git", "diff", "--name-status", "HEAD"], capture_output=True, text=True, cwd=REPO)
    diff_status = r.stdout
    if not diff_status.strip():
        r = subprocess.run(["git", "diff", "--name-status", "--cached"], capture_output=True, text=True, cwd=REPO)
        diff_status = r.stdout
    if not diff_status.strip():
        r = subprocess.run(["git", "diff", "--name-status", "HEAD~1"], capture_output=True, text=True, cwd=REPO)
        diff_status = r.stdout

    new_test_files = []
    for line in diff_status.splitlines():
        parts = line.split("\t", 1)
        if len(parts) == 2 and parts[0].startswith("A") and "test" in parts[1].lower():
            new_test_files.append(parts[1])

    assert not new_test_files, f"New test files created (must add to existing): {new_test_files}"
