"""
Tests for TanStack/router#6909: Semantic commit changelog generation.

This PR refactors the GitHub release changelog script to:
1. Parse conventional commits from git log instead of reading CHANGELOG.md files
2. Group commits by type (feat, fix, perf, refactor, docs, chore, test, ci)
3. Sort types by priority order
4. Generate markdown with ### Type headings instead of #### Package headings
"""

import os
import re
import subprocess

REPO = "/workspace/router"
SCRIPT_PATH = os.path.join(REPO, "scripts", "create-github-release.mjs")


def read_script():
    """Read the release script content."""
    with open(SCRIPT_PATH, "r") as f:
        return f.read()


# =============================================================================
# Fail-to-Pass Tests (must fail on base commit, pass after fix)
# =============================================================================


def test_typeorder_array_exists():
    """Script defines typeOrder array for conventional commit type priority (fail_to_pass)."""
    content = read_script()
    # Check that typeOrder is defined as an array with conventional commit types
    assert "typeOrder" in content, "typeOrder array should be defined"
    assert re.search(r"typeOrder\s*=\s*\[", content), "typeOrder should be an array"
    # Verify key types are in the order
    for commit_type in ["feat", "fix", "perf", "refactor"]:
        assert f"'{commit_type}'" in content or f'"{commit_type}"' in content, \
            f"typeOrder should include '{commit_type}'"


def test_typelabels_object_exists():
    """Script defines typeLabels object for human-readable type names (fail_to_pass)."""
    content = read_script()
    # Check that typeLabels is defined with mappings
    assert "typeLabels" in content, "typeLabels object should be defined"
    assert re.search(r"typeLabels\s*=\s*\{", content), "typeLabels should be an object"
    # Verify key mappings exist
    assert "'Features'" in content or '"Features"' in content, "typeLabels should map feat to Features"
    assert "'Fix'" in content or '"Fix"' in content, "typeLabels should map fix to Fix"


def test_conventional_commit_parsing():
    """Script parses conventional commits with type(scope): message format (fail_to_pass)."""
    content = read_script()
    # The script should have a regex to parse conventional commit format
    # Pattern: type(scope)?: message
    assert "conventionalMatch" in content, \
        "Script should have conventionalMatch for parsing"
    # Check for conventional commit regex pattern components
    # The pattern is: /^(\w+)(?:\(([^)]*)\))?:\s*(.*)$/
    assert r"(\w+)" in content or "\\w+" in content, \
        "Script should parse type from conventional commits"
    assert "scope" in content.lower() or "[^)]*" in content, \
        "Script should parse scope from conventional commits"


def test_groups_by_commit_type():
    """Script groups commits by their conventional commit type (fail_to_pass)."""
    content = read_script()
    # Check that there's a groups object being populated
    assert re.search(r"groups\s*=\s*\{\}", content) or re.search(r"const\s+groups", content), \
        "Script should have a groups object"
    # Check that groups are being populated by type
    assert re.search(r"groups\[type\]", content) or re.search(r"groups\[.*type", content), \
        "Script should group commits by type"


def test_markdown_type_headings():
    """Script generates ### Type headings instead of #### Package headings (fail_to_pass)."""
    content = read_script()
    # The new format uses ### for type headings
    # Check for pattern that generates ### headings with type labels
    assert re.search(r"###\s*\$\{label\}", content) or re.search(r"`###\s*\$\{", content), \
        "Script should generate ### headings for commit types"
    # Should NOT have #### for package headings (old format)
    old_package_pattern = re.search(r"`####\s*\$\{pkg\.name\}`", content)
    assert old_package_pattern is None, "Script should not use #### package headings"


def test_no_changelog_md_reading():
    """Script no longer reads CHANGELOG.md files for changelog content (fail_to_pass)."""
    content = read_script()
    # The old implementation read from CHANGELOG.md files
    # New implementation uses git log instead
    changelog_read_pattern = re.search(r"fs\.readFileSync\(changelogPath", content)
    assert changelog_read_pattern is None, \
        "Script should not read CHANGELOG.md files for changelog content"


def test_git_log_with_format():
    """Script uses git log with pretty format for commit parsing (fail_to_pass)."""
    content = read_script()
    # Check for git log command with format specifier
    assert re.search(r"git log.*--pretty=format", content), \
        "Script should use git log with --pretty=format"
    # Check that format includes hash, email, and subject
    assert re.search(r"%h.*%ae.*%s", content) or re.search(r"%h.*%s", content), \
        "Git log format should include hash and subject"


def test_removes_append_authors_function():
    """Script removes the appendAuthors function (fail_to_pass)."""
    content = read_script()
    # The old appendAuthors function should not exist
    assert "async function appendAuthors" not in content, \
        "appendAuthors function should be removed"
    assert "const withAuthors = await appendAuthors" not in content, \
        "Call to appendAuthors should be removed"


def test_removes_resolve_author_for_commit():
    """Script removes resolveAuthorForCommit function (fail_to_pass)."""
    content = read_script()
    # The old resolveAuthorForCommit function should not exist
    assert "async function resolveAuthorForCommit" not in content, \
        "resolveAuthorForCommit function should be removed"
    assert "authorCache" not in content or "prAuthorCache" in content, \
        "authorCache for commit lookup should be removed (prAuthorCache is OK)"


def test_type_sorting_by_priority():
    """Script sorts commit types by priority order (fail_to_pass)."""
    content = read_script()
    # Check for typeIndex function or sorting by type order
    has_type_index = "typeIndex" in content
    has_sort_by_type = re.search(r"sort\s*\(\s*\(a,\s*b\)", content) and "typeIndex" in content
    assert has_type_index or has_sort_by_type, \
        "Script should sort types by priority using typeIndex"


# =============================================================================
# Pass-to-Pass Tests (should pass on both base and fixed commits)
# =============================================================================


def test_script_syntax_valid():
    """Release script has valid JavaScript/ESM syntax (pass_to_pass)."""
    result = subprocess.run(
        ["node", "--check", SCRIPT_PATH],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO
    )
    assert result.returncode == 0, f"Script has syntax errors:\n{result.stderr}"


def test_repo_eslint_scripts():
    """Repo's ESLint passes on scripts directory (pass_to_pass)."""
    result = subprocess.run(
        ["npx", "eslint", "scripts/"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO
    )
    # ESLint exits 0 for warnings, 1 for errors
    assert result.returncode == 0, f"ESLint failed:\n{result.stdout}\n{result.stderr}"


def test_repo_prettier_scripts():
    """Repo's Prettier formatting check passes on scripts (pass_to_pass)."""
    result = subprocess.run(
        ["npx", "prettier", "--check", "scripts/*.mjs", "scripts/*.js", "scripts/*.ts"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO
    )
    assert result.returncode == 0, f"Prettier check failed:\n{result.stdout}\n{result.stderr}"


def test_resolve_username_function_exists():
    """Script still has resolveUsername function for email lookup (pass_to_pass)."""
    content = read_script()
    assert "async function resolveUsername" in content, \
        "resolveUsername function should still exist"


def test_resolve_author_for_pr_exists():
    """Script still has resolveAuthorForPR function (pass_to_pass)."""
    content = read_script()
    assert "async function resolveAuthorForPR" in content, \
        "resolveAuthorForPR function should still exist"
    assert "prAuthorCache" in content, \
        "PR author cache should still exist"


def test_pr_author_lookup_pattern():
    """Script uses PR number to look up author (pass_to_pass)."""
    content = read_script()
    # Check for PR author resolution
    assert re.search(r"resolveAuthorForPR\s*\(", content), \
        "Script should call resolveAuthorForPR"


def test_previous_release_detection():
    """Script detects previous release for git log range (pass_to_pass)."""
    content = read_script()
    assert "previousRelease" in content, \
        "Script should detect previous release"
    assert re.search(r"git\s+tag", content, re.IGNORECASE), \
        "Script should use git tag to find releases"


def test_bumped_packages_collection():
    """Script collects bumped packages from package.json files (pass_to_pass)."""
    content = read_script()
    assert "bumpedPackages" in content, \
        "Script should track bumped packages"
    assert "package.json" in content, \
        "Script should read package.json files"


def test_github_release_creation():
    """Script creates GitHub release with gh CLI (pass_to_pass)."""
    content = read_script()
    assert re.search(r"gh\s+release\s+create", content), \
        "Script should use gh release create"


def test_no_merge_commits_filter():
    """Script filters out merge commits from git log (fail_to_pass)."""
    content = read_script()
    assert "--no-merges" in content, \
        "Script should filter out merge commits"
