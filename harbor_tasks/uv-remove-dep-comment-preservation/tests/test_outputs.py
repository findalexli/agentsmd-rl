"""
Task: uv-remove-dep-comment-preservation
Repo: astral-sh/uv @ 46c9bac182d64359cef45d51fd796b81b3736f8b
PR:   18557

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
import tempfile
from pathlib import Path

REPO = "/repo"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_uv_bin_cache = None

def _build_uv():
    """Build the uv binary once, return its path."""
    global _uv_bin_cache
    if _uv_bin_cache and Path(_uv_bin_cache).exists():
        return _uv_bin_cache
    uv_bin = Path(REPO) / "target" / "debug" / "uv"
    if not uv_bin.exists():
        r = subprocess.run(
            ["cargo", "build", "-p", "uv"],
            cwd=REPO, capture_output=True, timeout=600,
        )
        assert r.returncode == 0, f"cargo build failed:\n{r.stderr.decode()[-2000:]}"
    _uv_bin_cache = str(uv_bin)
    return _uv_bin_cache


def _run_uv_remove(uv_bin: str, pyproject_content: str, dep_name: str) -> str:
    """Create a temp project, run `uv remove <dep> --no-sync`, return resulting pyproject.toml."""
    with tempfile.TemporaryDirectory() as tmp:
        pf = Path(tmp) / "pyproject.toml"
        pf.write_text(pyproject_content)
        r = subprocess.run(
            [uv_bin, "remove", dep_name, "--no-sync"],
            cwd=tmp, capture_output=True, timeout=60,
        )
        assert r.returncode == 0, (
            f"uv remove failed:\n{r.stderr.decode()[-1000:]}"
        )
        return pf.read_text()


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_cargo_check():
    """Modified crate must compile without errors."""
    r = subprocess.run(
        ["cargo", "check", "-p", "uv-workspace"],
        cwd=REPO, capture_output=True, timeout=300,
    )
    assert r.returncode == 0, f"cargo check failed:\n{r.stderr.decode()[-2000:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_remove_last_dep_preserves_prev_comment():
    """Removing the last dep preserves end-of-line comment on the previous entry."""
    uv = _build_uv()

    # Case 1: two deps, remove last
    result1 = _run_uv_remove(uv, """\
[project]
name = "t1"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "iniconfig>=2.0.0", # keep this note
    "typing-extensions>=4.0.0",
]
""", "typing-extensions")
    assert "# keep this note" in result1, f"Comment lost (case 1):\n{result1}"
    assert "typing-extensions" not in result1.lower()

    # Case 2: three deps, remove last, comment on second-to-last
    result2 = _run_uv_remove(uv, """\
[project]
name = "t2"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "iniconfig>=2.0.0",
    "sniffio>=1.3.0", # sniffio is important
    "typing-extensions>=4.0.0",
]
""", "typing-extensions")
    assert "# sniffio is important" in result2, f"Comment lost (case 2):\n{result2}"
    assert "typing-extensions" not in result2.lower()

    # Case 3: two deps, remove last, different comment text
    result3 = _run_uv_remove(uv, """\
[project]
name = "t3"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "anyio>=4.0.0", # pinned for compat
    "requests>=2.32.0",
]
""", "requests")
    assert "# pinned for compat" in result3, f"Comment lost (case 3):\n{result3}"
    assert "requests" not in result3.lower()


# [pr_diff] fail_to_pass
def test_remove_middle_dep_preserves_prev_comment():
    """Removing a middle dep preserves end-of-line comment on the previous entry."""
    uv = _build_uv()

    # Case 1: remove middle of 3
    result1 = _run_uv_remove(uv, """\
[project]
name = "t4"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "iniconfig>=2.0.0", # iniconfig note
    "typing-extensions>=4.0.0",
    "sniffio>=1.3.0",
]
""", "typing-extensions")
    assert "# iniconfig note" in result1, f"Comment lost:\n{result1}"
    assert "typing-extensions" not in result1.lower()
    assert "sniffio" in result1

    # Case 2: remove middle of 4, comments on surrounding entries
    result2 = _run_uv_remove(uv, """\
[project]
name = "t5"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "iniconfig>=2.0.0", # first note
    "typing-extensions>=4.0.0",
    "sniffio>=1.3.0", # third note
    "anyio>=4.0.0",
]
""", "typing-extensions")
    assert "# first note" in result2, f"First comment lost:\n{result2}"
    assert "# third note" in result2, f"Third comment lost:\n{result2}"


# [pr_diff] fail_to_pass
def test_remove_adjacent_duplicates_preserves_comment():
    """Removing multiple adjacent matching deps preserves comment on preceding entry."""
    uv = _build_uv()

    # Case 1: two typing-extensions with markers, comment on iniconfig
    result1 = _run_uv_remove(uv, """\
[project]
name = "t6"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "iniconfig>=2.0.0", # comment on iniconfig
    "typing-extensions>=4.0.0 ; python_version < '3.11'",
    "typing-extensions>=4.0.0 ; python_version >= '3.11'",
    "sniffio>=1.3.0",
]
""", "typing-extensions")
    assert "typing-extensions" not in result1.lower()
    assert "# comment on iniconfig" in result1, \
        f"Comment on iniconfig lost after removing adjacent duplicates:\n{result1}"
    assert "sniffio" in result1

    # Case 2: two typing-extensions, comment on preceding, no trailing dep
    result2 = _run_uv_remove(uv, """\
[project]
name = "t9"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "anyio>=4.0.0", # anyio is needed
    "typing-extensions>=4.0.0 ; python_version < '3.11'",
    "typing-extensions>=4.0.0 ; python_version >= '3.11'",
]
""", "typing-extensions")
    assert "typing-extensions" not in result2.lower()
    assert "# anyio is needed" in result2, \
        f"Comment on anyio lost after removing adjacent duplicates:\n{result2}"


# [pr_diff] fail_to_pass
def test_comment_preserved_across_sequential_removals():
    """Comments survive when multiple deps are removed in sequence."""
    uv = _build_uv()

    with tempfile.TemporaryDirectory() as tmp:
        pf = Path(tmp) / "pyproject.toml"
        pf.write_text("""\
[project]
name = "t7"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "iniconfig>=2.0.0", # must survive both removals
    "typing-extensions>=4.0.0",
    "sniffio>=1.3.0",
]
""")
        # First removal
        r1 = subprocess.run(
            [uv, "remove", "typing-extensions", "--no-sync"],
            cwd=tmp, capture_output=True, timeout=60,
        )
        after_first = pf.read_text()
        assert "# must survive both removals" in after_first, \
            f"Comment lost after first removal:\n{after_first}"

        # Second removal
        r2 = subprocess.run(
            [uv, "remove", "sniffio", "--no-sync"],
            cwd=tmp, capture_output=True, timeout=60,
        )
        after_second = pf.read_text()
        assert "# must survive both removals" in after_second, \
            f"Comment lost after second removal:\n{after_second}"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_existing_unit_tests_pass():
    """Existing unit tests in uv-workspace must not regress."""
    r = subprocess.run(
        ["cargo", "test", "-p", "uv-workspace", "--",
         "split_specifiers", "reformat_array"],
        cwd=REPO, capture_output=True, timeout=300,
    )
    assert r.returncode == 0, \
        f"Existing tests failed:\n{r.stdout.decode()[-1000:]}\n{r.stderr.decode()[-1000:]}"


# [static] pass_to_pass
def test_remove_only_dep_basic():
    """Removing the sole dependency leaves dependencies key with empty array."""
    uv = _build_uv()
    result = _run_uv_remove(uv, """\
[project]
name = "t8"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "typing-extensions>=4.0.0",
]
""", "typing-extensions")
    assert "typing-extensions" not in result.lower()
    assert "dependencies" in result


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — CLAUDE.md rules
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — CLAUDE.md:7 @ 46c9bac182d64359cef45d51fd796b81b3736f8b
def test_no_panic_unwrap_unreachable():
    """remove_dependency avoids panic!/unreachable!/.unwrap() per CLAUDE.md line 7."""
    # AST-only because: Rust code cannot be imported into Python
    src = Path(f"{REPO}/crates/uv-workspace/src/pyproject_mut.rs").read_text()
    match = re.search(
        r"fn remove_dependency\b.*?\n(.*?)(?=\nfn |\Z)",
        src, re.DOTALL,
    )
    assert match, "remove_dependency function not found"
    fn_body = match.group(0)

    unwrap_count = len(re.findall(r"\.unwrap\(\)", fn_body))
    assert unwrap_count <= 1, (
        f"Too many .unwrap() calls ({unwrap_count}) in remove_dependency — "
        f"CLAUDE.md line 7: AVOID .unwrap()"
    )

    panic_count = len(re.findall(r"\bpanic!\s*\(", fn_body))
    assert panic_count == 0, (
        f"Found panic! in remove_dependency — CLAUDE.md line 7: AVOID panic!"
    )

    unreachable_count = len(re.findall(r"\bunreachable!\s*\(", fn_body))
    assert unreachable_count == 0, (
        f"Found unreachable! in remove_dependency — CLAUDE.md line 7: AVOID unreachable!"
    )
