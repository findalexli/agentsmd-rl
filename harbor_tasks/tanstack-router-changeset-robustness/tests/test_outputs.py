"""
Test suite for TanStack Router changeset publishing robustness fix.

This tests the logic in scripts/create-github-release.mjs for:
1. Git log parsing for release commits
2. Commit range calculation
3. Conventional and non-conventional commit parsing
4. Commit grouping logic
5. Release flag generation (--prerelease vs --latest)
"""

import subprocess
import os
import re
import sys
from pathlib import Path

REPO = Path("/workspace/router")
SCRIPT_PATH = REPO / "scripts" / "create-github-release.mjs"


def test_script_exists():
    """Verify the release script exists."""
    assert SCRIPT_PATH.exists(), f"Script not found at {SCRIPT_PATH}"


def test_release_logs_parsing():
    """Test that the script uses proper array-based release commit parsing.

    The fix changes from 'HEAD~1' assumption to extracting release commits
    into an array and using indices [0] and [1].
    """
    content = SCRIPT_PATH.read_text()

    # Check for the new parsing approach using split/filter
    assert ".split('\\n')" in content or '.split("\\n")' in content, \
        "Script should split release logs by newline"
    assert ".filter(Boolean)" in content, \
        "Script should filter empty lines from release logs"

    # Check for array-based access
    assert "releaseLogs[0]" in content, \
        "Script should access current release as releaseLogs[0]"
    assert "releaseLogs[1]" in content, \
        "Script should access previous release as releaseLogs[1]"


def test_commit_range_calculation():
    """Test that commit range excludes both release commits properly.

    Before: Used HEAD~1 which was fragile
    After: Uses explicit previousRelease and currentRelease range
    """
    content = SCRIPT_PATH.read_text()

    # Should use the range variables properly
    assert "previousRelease ||" in content, \
        "Script should have fallback for previousRelease"
    assert "currentRelease}" in content or "${currentRelease}" in content, \
        "Script should use currentRelease in git log range"

    # Should NOT use the old fragile pattern
    assert "HEAD~1 --format=%H" not in content, \
        "Script should not use fragile HEAD~1 pattern for getting last release"


def test_non_conventional_commit_parsing():
    """Test that non-conventional commits use split() instead of indexOf.

    Before: Used brittle double indexOf approach
    After: Uses cleaner split(' ') approach
    """
    content = SCRIPT_PATH.read_text()

    # Check for new cleaner parsing
    assert "parts = line.split(' ')" in content, \
        "Script should use split(' ') for parsing non-conventional commits"
    assert "parts.slice(2).join(' ')" in content, \
        "Script should use slice/join for subject extraction"

    # Should NOT use the old brittle approach
    old_pattern = "rest.slice(spaceIdx2 + 1)"
    assert old_pattern not in content, \
        "Script should not use brittle double indexOf approach"


def test_prerelease_vs_latest_flag():
    """Test that prereleases don't get --latest flag.

    Before: All releases used --latest
    After: Prereleases omit --latest, normal releases include it
    """
    content = SCRIPT_PATH.read_text()

    # Check for the new conditional logic
    assert "const latestFlag" in content, \
        "Script should define latestFlag variable"
    assert "isPrerelease ? '' : ' --latest'" in content or \
           'isPrerelease ? "" : " --latest"' in content, \
        "Script should conditionally set latestFlag based on prerelease status"

    # The gh release command should use latestFlag
    assert "${latestFlag}" in content or "${prereleaseFlag}" in content, \
        "Script should use flags in gh release create command"


def test_comments_added():
    """Test that explanatory comments were added for clarity."""
    content = SCRIPT_PATH.read_text()

    # Check for explanatory comments
    # Note: content.lower() makes variable names lowercase too
    assert "so HEAD is the release commit" in content.lower() or \
           "current release commit is releaselogs[0]" in content.lower(), \
        "Script should explain the git log range logic"

    assert "non-conventional commits" in content.lower() or \
           "non conventional commits" in content.lower(), \
        "Script should document non-conventional commit handling"


def test_node_syntax_valid():
    """Repo's Node.js syntax check passes (pass_to_pass).

    Runs node --check on the modified script to validate syntax.
    """
    result = subprocess.run(
        ["node", "--check", str(SCRIPT_PATH)],
        capture_output=True,
        text=True, cwd=REPO,
    )
    assert result.returncode == 0, \
        f"Script has syntax errors: {result.stderr}"


def test_repo_prettier_check():
    """Repo's Prettier formatting check passes on the modified file (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "prettier", "--check", str(SCRIPT_PATH)],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier check failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


def test_repo_eslint():
    """Repo's ESLint check passes on the modified file (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "eslint", str(SCRIPT_PATH)],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"ESLint failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
