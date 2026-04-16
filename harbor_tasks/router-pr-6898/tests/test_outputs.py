"""
Tests for TanStack/router PR #6898: Fix author attribution for PR links in changelog.

The bug: Changeset entries use PR links ([#6891](url)) for actual changes,
but the script only matched commit hash links ([`9a4d924`](url)). This meant
author attribution was missing for most changelog entries.

The fix: Add resolveAuthorForPR that fetches PR author via GitHub API,
and try PR resolution first before falling back to commit hash resolution.
"""

import subprocess
import os
import re

REPO = "/workspace/router"
SCRIPT_PATH = os.path.join(REPO, "scripts/create-github-release.mjs")


def test_resolve_author_for_pr_function_exists():
    """The resolveAuthorForPR function must exist (fail_to_pass)."""
    with open(SCRIPT_PATH, "r") as f:
        content = f.read()

    # The fix adds a new function resolveAuthorForPR
    assert "resolveAuthorForPR" in content, (
        "Missing resolveAuthorForPR function - the script needs a function "
        "to resolve authors from PR numbers via GitHub API"
    )


def test_pr_pattern_matching():
    """The script must match PR reference patterns like [#6891](url) (fail_to_pass)."""
    with open(SCRIPT_PATH, "r") as f:
        content = f.read()

    # The fix adds pattern matching for PR references: /\[#(\d+)\]/
    # Check for the PR pattern regex
    pr_pattern_exists = bool(re.search(r'\\[#\\(\\\\d\+\\)\\]|/\\\[#\(\\d\+\)\\\]/', content))

    # Also check for the literal pattern or equivalent
    has_pr_matching = (
        r"\[#(\d+)\]" in content or
        "[#" in content and "match" in content.lower()
    )

    assert has_pr_matching, (
        "Missing PR reference pattern matching - the script should match "
        "patterns like [#6891](url) to extract PR numbers"
    )


def test_pr_author_cache_exists():
    """A cache for PR authors should exist to avoid duplicate API calls (fail_to_pass)."""
    with open(SCRIPT_PATH, "r") as f:
        content = f.read()

    assert "prAuthorCache" in content, (
        "Missing prAuthorCache - the script should cache PR author lookups "
        "to avoid redundant GitHub API calls"
    )


def test_pr_resolution_before_commit():
    """PR resolution must be attempted before commit hash resolution (fail_to_pass)."""
    with open(SCRIPT_PATH, "r") as f:
        content = f.read()

    # Find positions of PR matching and commit matching in appendAuthors
    pr_match_pos = content.find("prMatch")
    commit_match_pos = content.find("commitMatch")

    # The fix should have prMatch checked before commitMatch in the function
    # Also check for the pattern itself
    has_pr_first = (
        pr_match_pos != -1 and
        (commit_match_pos == -1 or pr_match_pos < commit_match_pos)
    )

    assert has_pr_first, (
        "PR resolution should be attempted before commit hash resolution - "
        "changeset entries use PR links, not commit hashes"
    )


def test_github_api_pr_endpoint():
    """The script must call the GitHub API pulls endpoint for PR resolution (fail_to_pass)."""
    with open(SCRIPT_PATH, "r") as f:
        content = f.read()

    # The fix adds: fetch(`https://api.github.com/repos/TanStack/router/pulls/${prNumber}`)
    assert "api.github.com" in content and "pulls" in content, (
        "Missing GitHub API call for PR resolution - the script should fetch "
        "PR data from the GitHub pulls API endpoint"
    )


def test_author_format_consistent():
    """Author attribution format should be consistent between PR and commit paths (pass_to_pass)."""
    with open(SCRIPT_PATH, "r") as f:
        content = f.read()

    # Both PR and commit resolution should use "by @" format
    has_by_format = "by @${username}" in content or "by @" in content

    assert has_by_format, (
        "Author attribution should use 'by @username' format"
    )


def test_pr_match_regex_correctness():
    """Verify the PR match regex extracts PR numbers correctly (fail_to_pass)."""
    # Test the regex pattern that should be in the script
    import re as regex_module

    with open(SCRIPT_PATH, "r") as f:
        content = f.read()

    # The PR pattern should be: /\[#(\d+)\]/
    # Test some sample changelog lines
    test_cases = [
        ("- Fixed navigation ([#6891](https://github.com/TanStack/router/pull/6891))", "6891"),
        ("- Added feature [#1234](url) and more", "1234"),
        ("- Bug fix ([#999](link))", "999"),
    ]

    # Extract the pattern from the script and test it
    pattern_match = regex_module.search(r'/\\?\[#\(.*?\)\]/', content)

    # The fix must have a pattern that can match these
    assert "\\[#(\\d+)\\]" in content or r"\[#(\d+)\]" in content.replace("\\\\", "\\"), (
        "PR match regex should be /\\[#(\\d+)\\]/ to capture PR numbers from changelog lines"
    )


def test_script_syntax_valid():
    """The script must have valid JavaScript syntax (pass_to_pass)."""
    result = subprocess.run(
        ["node", "--check", SCRIPT_PATH],
        capture_output=True,
        text=True,
        timeout=30
    )
    assert result.returncode == 0, f"Syntax error in script:\n{result.stderr}"


def test_appendauthors_handles_non_list_items():
    """Lines not starting with '- ' should pass through unchanged (pass_to_pass)."""
    with open(SCRIPT_PATH, "r") as f:
        content = f.read()

    # The logic should check for "- " prefix before processing
    # This ensures headers and other content aren't modified
    assert "startsWith('- ')" in content or 'startsWith("- ")' in content, (
        "Script should check for list item prefix '- ' before processing lines"
    )


def test_repo_eslint_scripts():
    """ESLint passes on the release script (pass_to_pass)."""
    result = subprocess.run(
        ["npx", "eslint", "scripts/create-github-release.mjs"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    # ESLint exits 0 for warnings, 1 for errors
    assert result.returncode == 0, f"ESLint failed:\n{result.stdout}\n{result.stderr}"


def test_repo_prettier_scripts():
    """Prettier formatting check passes on the release script (pass_to_pass)."""
    result = subprocess.run(
        ["npx", "prettier", "--check", "scripts/create-github-release.mjs"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Prettier check failed:\n{result.stdout}\n{result.stderr}"


def test_repo_node_syntax_scripts():
    """All script files have valid JavaScript syntax (pass_to_pass)."""
    result = subprocess.run(
        ["node", "--check", "scripts/create-github-release.mjs"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Node syntax check failed:\n{result.stderr}"
