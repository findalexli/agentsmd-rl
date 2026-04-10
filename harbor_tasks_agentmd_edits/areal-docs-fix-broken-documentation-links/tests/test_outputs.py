"""
Task: areal-docs-fix-broken-documentation-links
Repo: inclusionAI/AReaL @ 036ab1692854c327ab817aa231c1b1ec19063c72
PR:   986

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/AReaL"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_alloc_mode_error_hint_url():
    """Error hint in alloc_mode.py parser references correct /en/ URL."""
    r = subprocess.run(
        ["python3", "-c", """
source = open('areal/api/alloc_mode.py').read()
# The error hint in AllocationModeParser.parse() should reference
# the megatron tutorial with the /en/ language prefix
assert 'inclusionai.github.io/AReaL/en/tutorial/megatron.html' in source, (
    "alloc_mode.py error hint missing /en/ prefix in megatron tutorial URL"
)
# Verify the old broken URL is gone
old_url = 'inclusionai.github.io/AReaL/tutorial/megatron.html'
remaining = source.replace('/en/tutorial/megatron.html', '')
assert old_url not in remaining, (
    "alloc_mode.py still contains old URL without /en/ prefix"
)
print("PASS")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_readme_no_broken_deep_links():
    """README.md deep links to docs site all include /en/ or /zh/ language prefix."""
    r = subprocess.run(
        ["python3", "-c", """
import re
content = open('README.md').read()
# Find deep links to the docs site that lack /en/ or /zh/ prefix.
# Matches: inclusionai.github.io/AReaL/<path> where <path> does NOT start
# with en/ or zh/ and IS a real path segment (starts with a lowercase letter).
# Excludes: root URL ending at /AReaL/ or /AReaL/") which auto-redirects.
broken = re.findall(
    r'inclusionai\\.github\\.io/AReaL/(?!en/|zh/)[a-z][^"\\s)>]*',
    content
)
assert len(broken) == 0, (
    f"Found {len(broken)} broken deep link(s) missing language prefix: "
    + ", ".join(broken[:5])
)
print("PASS")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_pyproject_docs_url():
    """pyproject.toml Documentation URL includes /en/ language prefix."""
    r = subprocess.run(
        ["python3", "-c", """
content = open('pyproject.toml').read()
assert '/en/intro.html' in content, (
    "pyproject.toml Documentation URL missing /en/ prefix"
)
# Verify the old broken URL is gone
remaining = content.replace('/en/intro.html', '')
assert 'AReaL/intro.html' not in remaining, (
    "pyproject.toml still contains old Documentation URL without /en/ prefix"
)
print("PASS")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — syntax / sanity checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_alloc_mode_compiles():
    """areal/api/alloc_mode.py parses without syntax errors."""
    r = subprocess.run(
        ["python3", "-c",
         "import py_compile; py_compile.compile('areal/api/alloc_mode.py', doraise=True)"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Syntax error: {r.stderr}"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — actual CI commands
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_ruff_check_alloc_mode():
    """Repo's ruff linter passes on modified alloc_mode.py (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "-q", "ruff==0.14.9"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    r = subprocess.run(
        ["ruff", "check", "areal/api/alloc_mode.py"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_ruff_format_check_alloc_mode():
    """Repo's ruff format check passes on modified alloc_mode.py (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "-q", "ruff==0.14.9"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    r = subprocess.run(
        ["ruff", "format", "--check", "areal/api/alloc_mode.py"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_pyproject_toml_valid():
    """pyproject.toml is valid TOML (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", """
import tomllib
with open('pyproject.toml', 'rb') as f:
    tomllib.load(f)
print('pyproject.toml valid')
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"pyproject.toml validation failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_alloc_mode_ast_parse():
    """areal/api/alloc_mode.py has valid Python AST (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", """
import ast
with open('areal/api/alloc_mode.py') as f:
    ast.parse(f.read())
print('alloc_mode.py AST valid')
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"AST parsing failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_mdformat_readme():
    """README.md formatting passes mdformat check (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "-q", "mdformat==0.7.17", "mdformat-gfm", "mdformat-tables", "mdformat-frontmatter"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    r = subprocess.run(
        ["mdformat", "--check", "README.md"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"mdformat check failed for README.md:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_mdformat_contributing():
    """CONTRIBUTING.md formatting passes mdformat check (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "-q", "mdformat==0.7.17", "mdformat-gfm", "mdformat-tables", "mdformat-frontmatter"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    r = subprocess.run(
        ["mdformat", "--check", "CONTRIBUTING.md"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"mdformat check failed for CONTRIBUTING.md:\n{r.stderr[-500:]}"
