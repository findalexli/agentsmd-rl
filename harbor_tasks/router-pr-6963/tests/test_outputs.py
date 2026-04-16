"""
Tests for TanStack/router PR #6963: ci: support semver breaking changes

This PR modifies the release script to properly recognize and group
breaking changes marked with '!' in conventional commit messages.

For example, 'feat!: new breaking feature' should be grouped under
'Breaking Changes' instead of 'Features'.
"""

import re
import subprocess
from pathlib import Path

REPO = Path("/workspace/router")
SCRIPT_PATH = REPO / "scripts" / "create-github-release.mjs"


def extract_conventional_commit_regex(script_content: str) -> str:
    """Extract the conventional commit regex pattern from the script."""
    # Look for: conventionalMatch = subject.match(/.../)
    match = re.search(
        r"conventionalMatch\s*=\s*subject\.match\(/(.+?)/\)",
        script_content,
    )
    if not match:
        raise AssertionError("Could not find conventional commit regex in script")
    return match.group(1)


class TestBreakingCommitRegex:
    """Tests for the regex pattern that parses conventional commits."""

    def test_regex_matches_breaking_commit_with_exclamation(self):
        """
        The regex should match breaking commits like 'feat!: message'.

        On the base commit, the regex doesn't have the (!)?  group, so
        'feat!: message' won't match because ! appears before the colon.

        On the fix, the regex has (!)?  which allows the ! marker.
        """
        script = SCRIPT_PATH.read_text()
        pattern = extract_conventional_commit_regex(script)

        # Test various breaking commit formats
        test_cases = [
            "feat!: breaking feature",
            "fix!: breaking fix",
            "refactor!: breaking refactor",
            "perf!: breaking performance change",
        ]

        for commit_msg in test_cases:
            match = re.match(pattern, commit_msg)
            assert match is not None, (
                f"Regex should match breaking commit '{commit_msg}'. "
                f"Pattern: {pattern}"
            )

    def test_regex_matches_breaking_commit_with_scope(self):
        """Breaking commits with scope should also match: 'feat(api)!: message'."""
        script = SCRIPT_PATH.read_text()
        pattern = extract_conventional_commit_regex(script)

        test_cases = [
            "feat(api)!: breaking API change",
            "fix(core)!: breaking core fix",
            "refactor(router)!: breaking router refactor",
        ]

        for commit_msg in test_cases:
            match = re.match(pattern, commit_msg)
            assert match is not None, (
                f"Regex should match scoped breaking commit '{commit_msg}'. "
                f"Pattern: {pattern}"
            )

    def test_regex_captures_breaking_marker(self):
        """
        The regex should capture the '!' marker in a group.

        On the fix, group(3) should be '!' for breaking commits.
        """
        script = SCRIPT_PATH.read_text()
        pattern = extract_conventional_commit_regex(script)

        match = re.match(pattern, "feat!: breaking feature")
        assert match is not None, "Regex should match breaking commits"

        groups = match.groups()
        # The ! should be captured in one of the groups
        assert "!" in groups, (
            f"The '!' marker should be captured in a group. "
            f"Captured groups: {groups}"
        )


class TestBreakingCommitGrouping:
    """Tests for the commit grouping logic."""

    def test_breaking_type_in_type_order(self):
        """
        The 'breaking' type should be in typeOrder, and it should be first.
        """
        script = SCRIPT_PATH.read_text()

        # Check that 'breaking' is in typeOrder
        type_order_match = re.search(
            r"const\s+typeOrder\s*=\s*\[([\s\S]*?)\]",
            script,
        )
        assert type_order_match, "Could not find typeOrder in script"

        type_order_content = type_order_match.group(1)
        assert "'breaking'" in type_order_content or '"breaking"' in type_order_content, (
            "'breaking' should be in typeOrder to properly sort breaking changes. "
            f"Found: {type_order_content[:200]}"
        )

    def test_breaking_type_in_type_labels(self):
        """
        The 'breaking' type should have a label in typeLabels.
        """
        script = SCRIPT_PATH.read_text()

        # Check that 'breaking' has a label
        assert "breaking:" in script or "breaking :" in script, (
            "'breaking' should have a label entry in typeLabels"
        )

        # Verify it has an appropriate label text
        type_labels_match = re.search(
            r"const\s+typeLabels\s*=\s*\{([\s\S]*?)\}",
            script,
        )
        assert type_labels_match, "Could not find typeLabels in script"

        type_labels_content = type_labels_match.group(1)
        # Should contain something like 'Breaking' in the label
        assert "breaking" in type_labels_content.lower(), (
            "typeLabels should have an entry for 'breaking'"
        )

    def test_is_breaking_variable_exists(self):
        """
        The script should have an isBreaking variable to track breaking commits.
        """
        script = SCRIPT_PATH.read_text()

        assert "isBreaking" in script, (
            "Script should have an 'isBreaking' variable to track breaking commits"
        )

    def test_bucket_uses_breaking_type(self):
        """
        The script should use 'breaking' as the bucket/group for breaking commits.
        """
        script = SCRIPT_PATH.read_text()

        # Check that there's logic to group breaking commits separately
        # Look for pattern like: bucket = isBreaking ? 'breaking' : type
        has_breaking_bucket = (
            "isBreaking ? 'breaking'" in script or
            'isBreaking ? "breaking"' in script or
            "bucket" in script and "breaking" in script
        )

        assert has_breaking_bucket, (
            "Script should group breaking commits under 'breaking' bucket. "
            "Expected pattern like: bucket = isBreaking ? 'breaking' : type"
        )


class TestMessageExtraction:
    """Tests for correct message extraction from commits."""

    def test_message_uses_correct_group_index(self):
        """
        After adding the (!)? group, the message should be extracted from
        group 4 instead of group 3.
        """
        script = SCRIPT_PATH.read_text()
        pattern = extract_conventional_commit_regex(script)

        # Test that we can correctly extract the message from a breaking commit
        match = re.match(pattern, "feat!: new breaking feature")
        assert match is not None, "Regex should match breaking commits"

        groups = match.groups()
        # The message should be 'new breaking feature'
        # With the fix, this is in group(4) which is groups[3]
        assert "new breaking feature" in groups, (
            f"Message 'new breaking feature' should be in captured groups. "
            f"Captured: {groups}"
        )

    def test_regular_commit_message_extraction(self):
        """
        Regular commits (without !) should still have their message extracted correctly.
        """
        script = SCRIPT_PATH.read_text()
        pattern = extract_conventional_commit_regex(script)

        match = re.match(pattern, "feat: regular feature")
        assert match is not None, "Regex should match regular commits"

        groups = match.groups()
        assert "regular feature" in groups, (
            f"Message 'regular feature' should be in captured groups. "
            f"Captured: {groups}"
        )

    def test_scoped_commit_message_extraction(self):
        """
        Scoped commits should have their message extracted correctly.
        """
        script = SCRIPT_PATH.read_text()
        pattern = extract_conventional_commit_regex(script)

        match = re.match(pattern, "feat(api): add new endpoint")
        assert match is not None, "Regex should match scoped commits"

        groups = match.groups()
        assert "add new endpoint" in groups, (
            f"Message 'add new endpoint' should be in captured groups. "
            f"Captured: {groups}"
        )


class TestRepoLinting:
    """Pass-to-pass tests using repo's existing CI commands."""

    def test_eslint_passes(self):
        """Repo's ESLint check should pass."""
        result = subprocess.run(
            ["pnpm", "test:eslint"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=300,
        )
        assert result.returncode == 0, (
            f"ESLint failed:\n{result.stderr[-1000:]}\n{result.stdout[-1000:]}"
        )

    def test_typescript_check_passes(self):
        """Repo's TypeScript type checking should pass."""
        result = subprocess.run(
            ["pnpm", "test:types"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=300,
        )
        assert result.returncode == 0, (
            f"TypeScript check failed:\n{result.stderr[-1000:]}\n{result.stdout[-1000:]}"
        )

    def test_script_eslint(self):
        """ESLint passes on the release script (pass_to_pass)."""
        result = subprocess.run(
            ["npx", "eslint", "scripts/create-github-release.mjs"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=120,
        )
        assert result.returncode == 0, (
            f"ESLint failed on release script:\n{result.stderr[-500:]}\n{result.stdout[-500:]}"
        )

    def test_script_prettier(self):
        """Prettier formatting check passes on the release script (pass_to_pass)."""
        result = subprocess.run(
            ["npx", "prettier", "--check", "scripts/create-github-release.mjs"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=60,
        )
        assert result.returncode == 0, (
            f"Prettier check failed on release script:\n{result.stderr[-500:]}\n{result.stdout[-500:]}"
        )

    def test_script_node_syntax(self):
        """Node.js syntax check passes on the release script (pass_to_pass)."""
        result = subprocess.run(
            ["node", "--check", "scripts/create-github-release.mjs"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, (
            f"Node syntax check failed:\n{result.stderr[-500:]}"
        )
