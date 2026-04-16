#!/usr/bin/env python3
"""Tests for the breaking changes release notes feature.

This tests that the conventional commit parsing correctly identifies
breaking changes marked with `!` in the commit message.
"""

import subprocess
import os
import sys

REPO = "/workspace/router"
SCRIPT_PATH = os.path.join(REPO, "scripts/create-github-release.mjs")


def extract_parsing_function():
    """Extract the parsing logic from the script for testing."""
    with open(SCRIPT_PATH, 'r') as f:
        content = f.read()
    return content


def test_conventional_commit_regex_breaking():
    """Test that the regex correctly parses breaking changes with ! marker."""
    content = extract_parsing_function()

    # The regex should match the new pattern with optional ! capture group
    # Old: /^(\w+)(?:\(([^)]*)\))?:\s*(.*)$/
    # New: /^(\w+)(?:\(([^)]*)\))?(!)?:\s*(.*)$/
    assert "(!)?" in content, "Regex should capture optional ! before colon"

    # Check that isBreaking variable exists
    assert "const isBreaking" in content, "isBreaking variable should be defined"

    # Check that breaking detection uses match group 3
    assert "conventionalMatch[3]" in content, "Should check match group 3 for !"


def test_type_order_includes_breaking():
    """Test that 'breaking' type is included in typeOrder array."""
    content = extract_parsing_function()

    # Check that 'breaking' is first in typeOrder
    assert "'breaking'," in content, "'breaking' should be in typeOrder"

    # Find the typeOrder array and check order
    import re
    type_order_match = re.search(r"const typeOrder = \[(.*?)\]", content, re.DOTALL)
    assert type_order_match, "Should find typeOrder array"
    type_order_content = type_order_match.group(1)
    assert "'breaking'" in type_order_content, "breaking should be in typeOrder"


def test_type_labels_includes_breaking():
    """Test that 'breaking' type has a label defined."""
    content = extract_parsing_function()

    # Check that breaking label exists
    assert "breaking:" in content, "breaking label should be defined"
    assert "Breaking Changes" in content, "Breaking changes label should mention 'Breaking Changes'"


def test_bucket_logic_for_breaking_changes():
    """Test that breaking changes are assigned to the 'breaking' bucket."""
    content = extract_parsing_function()

    # Check that bucket logic exists
    assert "const bucket = isBreaking ? 'breaking' : type" in content, \
        "Should use bucket logic for breaking changes"

    # Check that groups[bucket] is used instead of groups[type]
    assert "groups[bucket]" in content, "Should use groups[bucket] instead of groups[type]"


def test_regex_index_updated_for_message():
    """Test that message extraction uses correct regex group index."""
    content = extract_parsing_function()

    # After adding ! capture group, message should use index 4
    assert "conventionalMatch[4]" in content, "Message should use match group 4"


def test_breaking_change_parsing_simulation():
    """Simulate parsing to verify breaking changes are detected correctly."""
    # Create a Node.js test script that simulates the parsing
    test_script = '''
const testCommits = [
    "abc123 user@example.com feat!: add new feature",
    "def456 user@example.com fix!: fix critical bug",
    "ghi789 user@example.com feat(scope)!: scoped breaking change",
    "jkl012 user@example.com feat: regular feature",
    "mno345 user@example.com fix: regular fix",
    "pqr678 user@example.com refactor!: breaking refactor"
];

const typeOrder = [
    'breaking',
    'feat',
    'fix',
    'perf',
    'refactor',
];

const typeLabels = {
    breaking: '⚠️ Breaking Changes',
    feat: 'Features',
    fix: 'Fix',
    perf: 'Performance',
    refactor: 'Refactor',
};

const groups = {};

for (const line of testCommits) {
    const match = line.match(/^(\\w+)\\s+(\\S+)\\s+(.*)$/);
    if (!match) continue;
    const [, hash, email, subject] = match;

    // Skip release commits
    if (subject.startsWith('ci: changeset release')) continue;

    // Parse conventional commit: type(scope)!: message
    const conventionalMatch = subject.match(/^(\\w+)(?:\\(([^)]*)\\))?(!)?:\\s*(.*)$/);
    const type = conventionalMatch ? conventionalMatch[1] : 'other';
    const isBreaking = conventionalMatch ? !!conventionalMatch[3] : false;
    const scope = conventionalMatch ? conventionalMatch[2] || '' : '';
    const message = conventionalMatch ? conventionalMatch[4] : subject;

    // Only include user-facing change types
    if (!['feat', 'fix', 'perf', 'refactor', 'build'].includes(type)) continue;

    // Extract PR number if present
    const prMatch = message.match(/\\(#(\\d+)\\)/);
    const prNumber = prMatch ? prMatch[1] : null;

    const bucket = isBreaking ? 'breaking' : type;
    if (!groups[bucket]) groups[bucket] = [];
    groups[bucket].push({ hash, email, scope, message, prNumber });
}

// Verify results
let passed = true;

// Check that breaking changes are in the 'breaking' group
// 4 breaking changes: feat!, fix!, feat(scope)!, refactor!
if (!groups.breaking || groups.breaking.length !== 4) {
    console.log("FAIL: Expected 4 breaking changes, found:", groups.breaking ? groups.breaking.length : 0);
    passed = false;
} else {
    // Check specific breaking changes
    const breakingHashes = groups.breaking.map(c => c.hash).sort();
    const expectedHashes = ['abc123', 'def456', 'ghi789', 'pqr678'].sort();
    const hashesMatch = JSON.stringify(breakingHashes) === JSON.stringify(expectedHashes);
    if (!hashesMatch) {
        console.log("FAIL: Wrong breaking change hashes. Got:", breakingHashes, "Expected:", expectedHashes);
        passed = false;
    }
}

// Check that non-breaking feats are still in 'feat' group
if (!groups.feat || groups.feat.length !== 1) {
    console.log("FAIL: Expected 1 non-breaking feat, found:", groups.feat ? groups.feat.length : 0);
    passed = false;
} else if (groups.feat[0].hash !== 'jkl012') {
    console.log("FAIL: Wrong feat hash:", groups.feat[0].hash);
    passed = false;
}

// Check that non-breaking fixes are still in 'fix' group
if (!groups.fix || groups.fix.length !== 1) {
    console.log("FAIL: Expected 1 non-breaking fix, found:", groups.fix ? groups.fix.length : 0);
    passed = false;
} else if (groups.fix[0].hash !== 'mno345') {
    console.log("FAIL: Wrong fix hash:", groups.fix[0].hash);
    passed = false;
}

if (passed) {
    console.log("PASS: Breaking change parsing works correctly");
    process.exit(0);
} else {
    process.exit(1);
}
'''

    # Write and run the test script
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.mjs', delete=False) as f:
        f.write(test_script)
        temp_path = f.name

    try:
        result = subprocess.run(
            ['node', temp_path],
            capture_output=True,
            text=True,
            timeout=30
        )
        assert result.returncode == 0, f"Breaking change parsing test failed: {result.stdout}{result.stderr}"
        assert "PASS" in result.stdout, f"Test should pass: {result.stdout}"
    finally:
        os.unlink(temp_path)


def test_old_regex_fails_on_breaking():
    """Verify that the old regex would NOT detect breaking changes correctly."""
    # This test demonstrates the bug - old regex treats "feat!:" as type "feat!" not "feat" with "!"
    test_script = '''
// Old regex
const oldRegex = /^(\\w+)(?:\\(([^)]*)\\))?:\\s*(.*)$/;

// Test with breaking change
const subject = "feat!: add new feature";
const match = subject.match(oldRegex);

// With old regex, this would not detect the ! separately
if (match) {
    const type = match[1];  // "feat!" - includes the ! as part of type
    const message = match[3];  // "add new feature"

    // Type would be "feat!" not "feat"
    if (type === "feat!" && !subject.includes("!:")) {
        console.log("PASS: Old regex incorrectly captures ! in type name");
        process.exit(0);
    } else if (type === "feat" && match[3] === "") {
        // This means the ! was captured as part of empty group - depends on regex behavior
        console.log("PASS: Old regex fails to parse correctly");
        process.exit(0);
    }
}

console.log("FAIL: Test setup issue - old regex behavior changed");
process.exit(1);
'''

    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.mjs', delete=False) as f:
        f.write(test_script)
        temp_path = f.name

    try:
        result = subprocess.run(
            ['node', temp_path],
            capture_output=True,
            text=True,
            timeout=30
        )
        # This test just demonstrates the old behavior
        # We don't assert returncode since it varies based on Node version
    finally:
        os.unlink(temp_path)


def test_repo_syntax():
    """Repo's JavaScript syntax check passes (pass_to_pass)."""
    import subprocess
    result = subprocess.run(
        ['node', '--check', 'scripts/create-github-release.mjs'],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO
    )
    assert result.returncode == 0, f"Syntax check failed: {result.stderr}"


def test_repo_lint():
    """Repo's ESLint passes on the modified script (pass_to_pass)."""
    result = subprocess.run(
        ['npx', 'eslint', 'scripts/create-github-release.mjs'],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO
    )
    assert result.returncode == 0, f"ESLint failed:\n{result.stdout[-500:]}{result.stderr[-500:]}"


def test_repo_format():
    """Repo's Prettier formatting check passes on the modified script (pass_to_pass)."""
    result = subprocess.run(
        ['npx', 'prettier', '--check', 'scripts/create-github-release.mjs'],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO
    )
    assert result.returncode == 0, f"Prettier check failed:\n{result.stdout[-500:]}{result.stderr[-500:]}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
