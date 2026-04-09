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
# Verify the old broken URL without /en/ is gone
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
