#!/usr/bin/env python3
"""Tests for the TanStack Router breaking changes release script fix."""

import subprocess
import re
import os

REPO = "/workspace/router"
SCRIPT_PATH = os.path.join(REPO, "scripts/create-github-release.mjs")


def test_breaking_change_regex_parsing():
    """
    FAIL-TO-PASS: Breaking change commits with ! marker must be parsed correctly.

    The regex should capture the ! marker as a separate group to identify breaking changes.
    Before the fix: /^(\w+)(?:(([^)]*)))?:\s*(.*)$/ - did not capture !
    After the fix: /^(\w+)(?:(([^)]*)))?(!)?:\s*(.*)$/ - captures ! as group 3
    """
    # Read the script content
    with open(SCRIPT_PATH, 'r') as f:
        content = f.read()

    # Find the regex pattern - the JS regex literal is like /^(\w+)(?:...)?(!)?:\s*(.*)$/
    # We need to capture the full /.../ literal
    regex_match = re.search(r'const conventionalMatch = subject\.match\(/(.+?)/\)', content)
    assert regex_match, "Could not find conventional commit regex in script"

    # Extract the regex pattern (inside the /.../ delimiters)
    pattern = regex_match.group(1)

    # Verify the regex captures the ! marker
    # The new regex should have a (!)? group
    assert "(!)?" in pattern, "Regex does not capture the ! breaking change marker"

    # Test cases for the regex behavior
    test_cases = [
        # (commit message, expected_type, expected_isBreaking, expected_message)
        ("feat!: add new API", "feat", True, "add new API"),
        ("feat(scope)!: add new API", "feat", True, "add new API"),
        ("fix!: fix critical bug", "fix", True, "fix critical bug"),
        ("feat: add feature", "feat", False, "add feature"),
        ("fix(scope): fix bug", "fix", False, "fix bug"),
        ("refactor!: breaking refactor", "refactor", True, "breaking refactor"),
    ]

    # Compile the regex pattern for testing
    js_regex = re.compile(pattern)

    for commit, expected_type, expected_breaking, expected_msg in test_cases:
        match = js_regex.match(commit)
        assert match, f"Regex should match commit: {commit}"

        actual_type = match.group(1)
        actual_breaking = bool(match.group(3))
        actual_msg = match.group(4)

        assert actual_type == expected_type, f"Type mismatch for '{commit}': expected {expected_type}, got {actual_type}"
        assert actual_breaking == expected_breaking, f"Breaking flag mismatch for '{commit}': expected {expected_breaking}, got {actual_breaking}"
        assert actual_msg == expected_msg, f"Message mismatch for '{commit}': expected '{expected_msg}', got '{actual_msg}'"


def test_breaking_in_type_order():
    """
    FAIL-TO-PASS: 'breaking' must be in typeOrder array for proper release note grouping.

    The typeOrder array determines the order of sections in generated release notes.
    Breaking changes should appear first.
    """
    with open(SCRIPT_PATH, 'r') as f:
        content = f.read()

    # Find the typeOrder array
    match = re.search(r'const typeOrder = \[([^\]]+)\]', content, re.DOTALL)
    assert match, "Could not find typeOrder array in script"

    type_order_content = match.group(1)

    # Verify 'breaking' is in typeOrder
    assert "'breaking'" in type_order_content or '"breaking"' in type_order_content, \
        "'breaking' is not in typeOrder array"

    # Verify 'breaking' comes before 'feat'
    breaking_pos = type_order_content.find("breaking")
    feat_pos = type_order_content.find("feat")
    assert breaking_pos < feat_pos, "'breaking' should come before 'feat' in typeOrder"


def test_breaking_in_type_labels():
    """
    FAIL-TO-PASS: 'breaking' must have a label in typeLabels object.

    The typeLabels object maps commit types to their display names in release notes.
    """
    with open(SCRIPT_PATH, 'r') as f:
        content = f.read()

    # Find the typeLabels object
    match = re.search(r'const typeLabels = \{([^}]+)\}', content, re.DOTALL)
    assert match, "Could not find typeLabels object in script"

    type_labels_content = match.group(1)

    # Verify 'breaking' is in typeLabels with the warning emoji
    assert "breaking:" in type_labels_content, "'breaking' key is not in typeLabels"
    assert "⚠️" in type_labels_content or "Breaking Changes" in type_labels_content, \
        "typeLabels for 'breaking' should contain warning emoji or 'Breaking Changes' text"


def test_bucket_assignment_for_breaking_changes():
    """
    FAIL-TO-PASS: Breaking changes must be assigned to 'breaking' bucket, not their original type.

    The code should use `const bucket = isBreaking ? 'breaking' : type`
    to route breaking changes to a dedicated section.
    """
    with open(SCRIPT_PATH, 'r') as f:
        content = f.read()

    # Check for the bucket assignment logic
    assert "const bucket = isBreaking ? 'breaking' : type" in content, \
        "Missing bucket assignment logic for breaking changes"

    # Check that groups[bucket] is used instead of groups[type]
    assert "groups[bucket]" in content, \
        "Code should use groups[bucket] instead of groups[type] for breaking changes"


def test_script_syntax_valid():
    """
    PASS-TO-PASS: The release script should have valid JavaScript syntax.

    Run Node.js syntax check on the script.
    """
    result = subprocess.run(
        ["node", "--check", "scripts/create-github-release.mjs"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30
    )
    assert result.returncode == 0, f"Script has syntax errors:\n{result.stderr}"


def test_repo_eslint():
    """
    PASS-TO-PASS: Repository ESLint should pass on the scripts directory.

    AGENTS.md requires running `pnpm test:eslint` before committing.
    """
    # First check if eslint config exists
    eslint_config = os.path.join(REPO, "eslint.config.js")
    if not os.path.exists(eslint_config):
        return  # Skip if no eslint config

    # Install deps first (needed for pnpm exec to work)
    subprocess.run(
        ["pnpm", "install", "--frozen-lockfile"],
        cwd=REPO,
        capture_output=True,
        timeout=120
    )

    # Run eslint on just the modified script
    result = subprocess.run(
        ["pnpm", "exec", "eslint", "scripts/create-github-release.mjs", "--max-warnings=0"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )

    # Allow for missing dependencies (npx might fail) but not for actual lint errors
    if result.returncode != 0:
        # Check if it's a real lint error vs missing deps
        if "error" in result.stderr.lower() and "module" not in result.stderr.lower():
            assert False, f"ESLint errors:\n{result.stderr}"


def test_repo_router_core_unit():
    """
    PASS-TO-PASS: @tanstack/router-core unit tests should pass.

    Core package tests verify that existing functionality is not broken.
    """
    # Install deps first
    subprocess.run(
        ["pnpm", "install", "--frozen-lockfile"],
        cwd=REPO,
        capture_output=True,
        timeout=120
    )

    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/router-core:test:unit",
         "--outputStyle=stream", "--skipRemoteCache"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"router-core unit tests failed:\n{result.stderr[-1000:]}"


def test_repo_history_unit():
    """
    PASS-TO-PASS: @tanstack/history unit tests should pass.

    History package tests verify that core history functionality works.
    """
    # Install deps first
    subprocess.run(
        ["pnpm", "install", "--frozen-lockfile"],
        cwd=REPO,
        capture_output=True,
        timeout=120
    )

    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/history:test:unit",
         "--outputStyle=stream", "--skipRemoteCache"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"history unit tests failed:\n{result.stderr[-1000:]}"


def test_is_breaking_variable_exists():
    """
    FAIL-TO-PASS: The isBreaking variable must be extracted from the regex match.

    Before the fix, this variable didn't exist. After the fix, it checks conventionalMatch[3].
    """
    with open(SCRIPT_PATH, 'r') as f:
        content = f.read()

    # Check for isBreaking variable extraction
    assert "const isBreaking = conventionalMatch ? !!conventionalMatch[3] : false" in content, \
        "Missing isBreaking variable extraction from conventionalMatch[3]"


def test_message_group_index_updated():
    """
    FAIL-TO-PASS: Message should be extracted from group 4, not group 3.

    When adding the ! capture group, the message index shifted from 3 to 4.
    """
    with open(SCRIPT_PATH, 'r') as f:
        content = f.read()

    # After adding ! group, message should be group 4
    assert "conventionalMatch[4]" in content, \
        "Message should be extracted from group 4 after adding ! capture group"

    # Should NOT have the old pattern of group 3 for message
    # (unless it's checking for breaking flag)
    lines = content.split('\n')
    for line in lines:
        if 'conventionalMatch' in line and '[3]' in line and 'isBreaking' not in line:
            # If group 3 is used but not for isBreaking, that's wrong
            assert False, f"Found incorrect use of conventionalMatch[3]: {line.strip()}"
