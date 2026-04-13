"""
Task: transformers-use-docbuilder-runnable-example-for
Repo: huggingface/transformers @ bb8031052cbd88f8b30c75df84b9703eee80200f
PR:   44277

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/transformers"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified Python files must parse without errors."""
    for rel in [
        "setup.py",
        "src/transformers/dependency_versions_table.py",
    ]:
        r = subprocess.run(
            ["python3", "-m", "py_compile", str(Path(REPO) / rel)],
            capture_output=True,
            timeout=30,
        )
        assert r.returncode == 0, f"{rel} has syntax errors:\n{r.stderr.decode()}"


# [repo_tests] pass_to_pass
def test_ruff_check():
    """Repo's ruff linting passes on modified files (pass_to_pass)."""
    r = subprocess.run(
        [
            "ruff",
            "check",
            "setup.py",
            "src/transformers/dependency_versions_table.py",
        ],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stderr or r.stdout}"


# [repo_tests] pass_to_pass
def test_ruff_format():
    """Repo's ruff formatting passes on modified files (pass_to_pass)."""
    r = subprocess.run(
        [
            "ruff",
            "format",
            "--check",
            "setup.py",
            "src/transformers/dependency_versions_table.py",
        ],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stderr or r.stdout}"


# [repo_tests] pass_to_pass
def test_check_inits():
    """Repo's __init__.py files are valid (pass_to_pass)."""
    r = subprocess.run(
        ["python", "utils/check_inits.py"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"check_inits failed:\n{r.stderr or r.stdout}"


# [repo_tests] pass_to_pass
def test_check_doctest_list():
    """Repo's doctest list is valid (pass_to_pass)."""
    r = subprocess.run(
        ["python", "utils/check_doctest_list.py"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"check_doctest_list failed:\n{r.stderr or r.stdout}"


# [repo_tests] pass_to_pass
def test_check_dummies():
    """Repo's dummy objects are valid (pass_to_pass)."""
    r = subprocess.run(
        ["python", "utils/check_dummies.py"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"check_dummies failed:\n{r.stderr or r.stdout}"


# [repo_tests] pass_to_pass
def test_check_doc_toc():
    """Repo's documentation TOC is valid (pass_to_pass)."""
    r = subprocess.run(
        ["python", "utils/check_doc_toc.py"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"check_doc_toc failed:\n{r.stderr or r.stdout}"


# [repo_tests] pass_to_pass
def test_deps_table():
    """Repo's dependency versions table is valid (pass_to_pass)."""
    r = subprocess.run(
        ["python", "utils/checkers.py", "deps_table"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"deps_table check failed:\n{r.stderr or r.stdout}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests: setup.py / dependency
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_docs_extra_defined():
    """setup.py must define an extras["docs"] entry."""
    setup_src = (Path(REPO) / "setup.py").read_text()
    assert 'extras["docs"]' in setup_src, (
        'setup.py should define extras["docs"] for doc-builder'
    )


# [pr_diff] fail_to_pass
def test_docs_extra_in_testing():
    """The testing extras must include the docs extra."""
    setup_src = (Path(REPO) / "setup.py").read_text()
    # Find the extras["testing"] definition block and check it references docs
    # The block may span multiple lines with concatenation operators
    testing_match = re.search(
        r'extras\["testing"\]\s*=\s*\((.*?)\)\s*\+\s*extras\["docs"\]',
        setup_src,
        re.DOTALL,
    )
    assert testing_match is not None, (
        'extras["testing"] should include + extras["docs"]'
    )


# [pr_diff] fail_to_pass
def test_dependency_table_uses_git_doc_builder():
    """dependency_versions_table.py must reference doc-builder via git+."""
    dep_table = (
        Path(REPO) / "src/transformers/dependency_versions_table.py"
    ).read_text()
    assert "git+https://github.com/huggingface/doc-builder" in dep_table, (
        "hf-doc-builder should use a git+ URL in the dependency table"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — doc example fixes in glmasr.md
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass


# [pr_diff] fail_to_pass


# ---------------------------------------------------------------------------
# Fail-to-pass (config_edit) — CONTRIBUTING.md and testing.md updates
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — doc install command updated
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
