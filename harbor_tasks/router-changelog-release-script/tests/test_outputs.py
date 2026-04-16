"""
Tests for PR #6897: Improve GitHub Release Changelog Generation

The PR refactors scripts/create-github-release.mjs to:
1. Extract changelog entries from changeset-generated CHANGELOG.md files
2. Add GitHub author attribution to each changelog entry
3. Only list packages that were actually bumped (version changed)
"""

import subprocess
import os
import json
import re

REPO = "/workspace/router"
SCRIPT_PATH = os.path.join(REPO, "scripts/create-github-release.mjs")

def test_resolveAuthorForCommit_function_exists():
    """F2P: resolveAuthorForCommit function should exist (new in PR)."""
    with open(SCRIPT_PATH, 'r') as f:
        content = f.read()
    assert 'async function resolveAuthorForCommit(hash)' in content, \
        "resolveAuthorForCommit function not found - should extract authors from commit hashes"


def test_appendAuthors_function_exists():
    """F2P: appendAuthors function should exist (new in PR)."""
    with open(SCRIPT_PATH, 'r') as f:
        content = f.read()
    assert 'async function appendAuthors(content)' in content, \
        "appendAuthors function not found - should append author info to changelog lines"


def test_bumpedPackages_logic_exists():
    """F2P: bumpedPackages logic should exist (new in PR)."""
    with open(SCRIPT_PATH, 'r') as f:
        content = f.read()
    # Check for the bumpedPackages array and comparison logic
    assert 'const bumpedPackages = []' in content, \
        "bumpedPackages array initialization not found"
    assert 'if (prevPkg.version !== currentPkg.version)' in content, \
        "Version comparison logic not found - should detect bumped packages"


def test_changelog_extraction_from_files():
    """F2P: Should extract changelog from CHANGELOG.md files instead of git commits."""
    with open(SCRIPT_PATH, 'r') as f:
        content = f.read()

    # Should NOT have the old git log parsing for conventional commits
    assert 'const rawLog = execSync(' not in content, \
        "Old git log parsing for conventional commits should be removed"
    assert '--pretty=format:"%h %ae %s"' not in content, \
        "Old commit format parsing should be removed"

    # SHOULD have the new CHANGELOG.md extraction logic
    assert "const changelogPath = path.join(packagesDir, pkg.dir, 'CHANGELOG.md')" in content, \
        "Should read from CHANGELOG.md files"
    assert 'changelog.indexOf(versionHeader)' in content, \
        "Should search for version header in changelog"


def test_author_appended_to_entries():
    """F2P: Changelog entries should have author attribution appended."""
    with open(SCRIPT_PATH, 'r') as f:
        content = f.read()

    # Check for the appendAuthors call
    assert 'const withAuthors = await appendAuthors(content)' in content, \
        "Should call appendAuthors to add author info"
    # Check for author string in output
    assert 'changelogMd += `#### ${pkg.name}' in content, \
        "Should output package name with authors"


def test_no_conventional_commit_grouping():
    """F2P: Should NOT group commits by conventional commit type (old behavior removed)."""
    with open(SCRIPT_PATH, 'r') as f:
        content = f.read()

    old_patterns = [
        "const groups = {}",
        "const typeOrder = [",
        "'Feat',",
        "'Fix',",
        "'Refactor',",
        "typeIndex",
        "sortedTypes",
        "for (const type of sortedTypes)"
    ]

    for pattern in old_patterns:
        assert pattern not in content, \
            f"Old conventional commit grouping pattern '{pattern}' should be removed"


def test_script_syntax_valid():
    """P2P: Script should have valid JavaScript syntax."""
    result = subprocess.run(
        ["node", "--check", SCRIPT_PATH],
        capture_output=True,
        text=True,
        cwd=REPO
    )
    assert result.returncode == 0, \
        f"Script has syntax errors:\n{result.stderr}"


def test_bumpedPackages_sorted():
    """F2P: bumpedPackages should be sorted alphabetically by name."""
    with open(SCRIPT_PATH, 'r') as f:
        content = f.read()
    assert 'bumpedPackages.sort((a, b) => a.name.localeCompare(b.name))' in content, \
        "bumpedPackages should be sorted by name"


def test_new_package_handling():
    """F2P: Should handle new packages that don't exist in previous release."""
    with open(SCRIPT_PATH, 'r') as f:
        content = f.read()
    # Check for catch block that handles new packages
    assert "// Package didn't exist in previous release" in content, \
        "Should handle new packages with comment"
    # Check that new packages are added to bumpedPackages
    pattern = r"prevVersion: null,\s+dir: path\.dirname\(relPath\),"
    assert re.search(pattern, content), \
        "New packages should be added with prevVersion: null"
