#!/usr/bin/env python3
"""Tests for TanStack Router release script fix.

This test suite verifies the changes made to create-github-release.mjs:
1. Git commit range uses array-based release log parsing
2. Non-conventional commit parsing uses split() instead of indexOf
3. --latest flag is only applied to non-prerelease releases
"""

import subprocess
import sys
from pathlib import Path

REPO = Path("/workspace/router")
SCRIPT_PATH = REPO / "scripts" / "create-github-release.mjs"


def read_script():
    """Read the script file content."""
    if not SCRIPT_PATH.exists():
        raise FileNotFoundError(f"Script not found: {SCRIPT_PATH}")
    return SCRIPT_PATH.read_text()


def test_release_logs_uses_array_parsing():
    """Verify releaseLogs is parsed as an array with split and filter.

    The old code used a single command with HEAD~1, the new code:
    1. Gets all release commits
    2. Splits into array and filters
    3. Uses releaseLogs[0] and releaseLogs[1]
    """
    content = read_script()

    # Check for the new array-based parsing
    assert ".split('\\n')" in content, "releaseLogs should use split('\\n')"
    assert ".filter(Boolean)" in content, "releaseLogs should filter empty strings"

    # Check for array indexing
    assert "releaseLogs[0]" in content, "Should use releaseLogs[0] for current release"
    assert "releaseLogs[1]" in content, "Should use releaseLogs[1] for previous release"

    # Verify the old fragile pattern is gone
    old_pattern = 'git log --oneline --grep="ci: changeset release" -n 1 --format=%H HEAD~1'
    assert old_pattern not in content, "Old HEAD~1 pattern should be removed"


def test_range_from_logic():
    """Verify rangeFrom uses proper current/previous release logic."""
    content = read_script()

    # Check for currentRelease and previousRelease variables
    assert "const currentRelease" in content, "Should have currentRelease variable"
    assert "const previousRelease" in content, "Should have previousRelease variable"

    # Check the rangeFrom logic uses previousRelease first
    assert "rangeFrom = previousRelease ||" in content, "rangeFrom should use previousRelease first"


def test_commit_range_uses_current_release():
    """Verify git log range uses currentRelease instead of HEAD~1."""
    content = read_script()

    # The new code should use currentRelease in the range
    assert "${rangeFrom}..${currentRelease}" in content, \
        "Git log range should use currentRelease variable"

    # Old pattern should be gone
    assert "${rangeFrom}..HEAD~1" not in content, \
        "Old HEAD~1 range pattern should be removed"


def test_non_conventional_commit_uses_split():
    """Verify non-conventional commits use split() instead of indexOf.

    The old code used double indexOf which was brittle.
    The new code uses split(' ') for cleaner parsing.
    """
    content = read_script()

    # Check for the new split-based parsing
    assert "const parts = line.split(' ')" in content, \
        "Non-conventional commits should use split(' ')"
    assert "const hash = parts[0]" in content, \
        "Should extract hash from parts[0]"
    assert "const email = parts[1]" in content, \
        "Should extract email from parts[1]"
    assert "parts.slice(2).join(' ')" in content, \
        "Should extract subject from remaining parts"

    # Verify old brittle pattern is gone
    assert "line.indexOf(' ')" not in content, \
        "Old indexOf pattern should be removed"


def test_latest_flag_conditional():
    """Verify --latest flag is only set for non-prereleases."""
    content = read_script()

    # Check for latestFlag variable
    assert "const latestFlag = isPrerelease ? '' : ' --latest'" in content, \
        "Should have latestFlag that is empty for prereleases, ' --latest' otherwise"

    # Check it's used in the gh release create command
    assert "${latestFlag}" in content, \
        "latestFlag should be used in gh release create command"

    # Verify old unconditional --latest is gone
    assert '--notes-file ${tmpFile} --latest' not in content, \
        "Old unconditional --latest should be removed"


def test_prerelease_flag_unchanged():
    """Verify prereleaseFlag logic remains intact."""
    content = read_script()

    # The prereleaseFlag should still exist
    assert "const prereleaseFlag = isPrerelease ? '--prerelease' : ''" in content, \
        "prereleaseFlag logic should be preserved"


def test_script_syntax_valid():
    """Verify the script has valid JavaScript/Node.js syntax."""
    result = subprocess.run(
        ["node", "--check", str(SCRIPT_PATH)],
        capture_output=True, text=True
    )
    assert result.returncode == 0, f"Script has syntax errors: {result.stderr}"


def test_comments_explain_changes():
    """Verify comments explain the git range and commit parsing changes."""
    content = read_script()

    # Check for explanatory comment about release commit logic
    assert "runs right after the" in content.lower() or "release commit" in content.lower(), \
        "Should have comment explaining release commit timing"

    # Check for comment about non-conventional commits
    assert "non-conventional commits" in content.lower() or "merge commits" in content.lower(), \
        "Should have comment explaining non-conventional commit handling"


def test_conventional_commit_regex_comment():
    """Verify there's a comment explaining the conventional commit format."""
    content = read_script()

    # Should have comment about the regex pattern format
    assert "format:" in content.lower() or "<hash>" in content or "<type>" in content, \
        "Should have comment explaining conventional commit format"


# ============================================================================
# Pass-to-Pass Tests: Repo CI/CD checks that should pass on both base and fix
# ============================================================================


def test_repo_script_syntax():
    """Repo's release script has valid JavaScript syntax (pass_to_pass)."""
    result = subprocess.run(
        ["node", "--check", str(SCRIPT_PATH)],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert result.returncode == 0, f"Script has syntax errors: {result.stderr}"


def test_repo_script_formatting():
    """Repo's release script follows Prettier formatting (pass_to_pass)."""
    result = subprocess.run(
        ["npx", "prettier", "--check", str(SCRIPT_PATH)],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert result.returncode == 0, f"Script formatting check failed:\n{result.stdout[-500:]}"


def test_repo_all_mjs_scripts_syntax():
    """All .mjs scripts in the repo have valid JavaScript syntax (pass_to_pass)."""
    scripts_dir = REPO / "scripts"
    mjs_files = list(scripts_dir.glob("*.mjs"))
    assert mjs_files, "No .mjs files found in scripts directory"

    for script_file in mjs_files:
        result = subprocess.run(
            ["node", "--check", str(script_file)],
            capture_output=True, text=True, timeout=60, cwd=REPO,
        )
        assert result.returncode == 0, f"Script {script_file.name} has syntax errors: {result.stderr}"


def test_repo_all_scripts_formatting():
    """All scripts in the repo follow Prettier formatting (pass_to_pass)."""
    result = subprocess.run(
        ["npx", "prettier", "--check", "scripts/"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert result.returncode == 0, f"Scripts formatting check failed:\n{result.stdout[-500:]}"


def test_repo_markdown_formatting():
    """Repo's markdown files follow Prettier formatting (pass_to_pass)."""
    result = subprocess.run(
        ["npx", "prettier", "--check", "*.md"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert result.returncode == 0, f"Markdown formatting check failed:\n{result.stdout[-500:]}"


def test_repo_package_json_formatting():
    """Repo's package.json follows Prettier formatting (pass_to_pass)."""
    result = subprocess.run(
        ["npx", "prettier", "--check", "package.json"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert result.returncode == 0, f"package.json formatting check failed:\n{result.stdout[-500:]}"


def test_repo_git_valid():
    """Repo has a valid git repository with commits (pass_to_pass)."""
    result = subprocess.run(
        ["git", "log", "--oneline", "-1"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert result.returncode == 0, f"Git log failed: {result.stderr}"
    assert result.stdout.strip(), "Git log returned empty output"


if __name__ == "__main__":
    # Run all tests
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
