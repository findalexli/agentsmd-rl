"""
Task: transformers-sizedict-or-operator
Repo: huggingface/transformers @ b7164eca8675e5223cf73fb430a6aaf6ceafc9cc
PR:   44884

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

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
