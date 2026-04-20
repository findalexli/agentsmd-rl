"""
Test suite for civitai/civitai#2059 - Username blocklist anti-impersonation

This tests that the username blocklist correctly blocks 'civit' and leet-speak variants.
The PR adds "civit", "c1vit", "civ1t", "c1v1t" to the partial blocklist to prevent
Civitai staff impersonation via username variations.

Fail-to-pass (f2p) tests:
- test_blocklist_rejects_civit_variants: Checks that 'civit' and variants are blocked
  FAIL at base (no civit in blocklist) -> PASS after fix (civit added)

Pass-to-pass (p2p) tests:
- test_blocklist_exact_still_blocks: Checks existing exact blocklist still works
- test_blocklist_allows_normal_usernames: Normal usernames are allowed
- test_blocklist_allows_non_matching_substrings: Partial matches that don't match are allowed
- test_repo_vitest_unit_tests: Repo unit tests pass (via vitest)
"""

import json
import os
import subprocess
import unittest
from pathlib import Path

REPO = "/workspace/civitai"
BLOCKLIST_PATH = os.path.join(REPO, "src/utils/blocklist-username.json")


def load_blocklist():
    """Load the username blocklist JSON."""
    with open(BLOCKLIST_PATH, "r") as f:
        return json.load(f)


def is_username_permitted(username: str, blocklist: dict) -> bool:
    """
    Mirror of the static blocklist checking logic from user.service.ts.
    Tests the JSON blocklist directly without needing the full codebase.
    """
    lower = username.lower()
    blocked_partial = blocklist.get("partial", [])
    blocked_exact = blocklist.get("exact", [])

    # Check partial matches
    if any(x in lower for x in blocked_partial):
        return False

    # Check exact matches
    if lower in blocked_exact:
        return False

    return True


class TestUsernameBlocklist(unittest.TestCase):
    """Tests for username blocklist functionality."""

    def setUp(self):
        self.blocklist = load_blocklist()

    def test_blocklist_exact_still_blocks(self):
        """Existing exact blocklist entries should still block correctly (p2p)."""
        # These are existing exact blocklist entries that should be blocked
        self.assertFalse(is_username_permitted("civitai", self.blocklist))
        self.assertFalse(is_username_permitted("Civitai", self.blocklist))
        self.assertFalse(is_username_permitted("civitai", self.blocklist))
        self.assertFalse(is_username_permitted("admin", self.blocklist))
        self.assertFalse(is_username_permitted("support", self.blocklist))

    def test_blocklist_allows_normal_usernames(self):
        """Normal usernames should be allowed (p2p)."""
        allowed = ["alice", "bob_123", "ModelMaker99", "PixelArtist"]
        for username in allowed:
            self.assertTrue(
                is_username_permitted(username, self.blocklist),
                f"Expected {username} to be allowed"
            )

    def test_blocklist_rejects_civit_variants(self):
        """
        FAIL-TO-PASS: Usernames containing 'civit' should be blocked.
        At base commit: FAIL (civit not in blocklist)
        After fix: PASS (civit added to partial blocklist)
        """
        # These should all be rejected after the fix
        civit_variants = [
            "civitmod",
            "civitai_support",
            "the_civit_team",
            "Civit",
            "CIVITADMIN",
        ]
        for username in civit_variants:
            self.assertFalse(
                is_username_permitted(username, self.blocklist),
                f"Expected {username} to be blocked but it was allowed"
            )

    def test_blocklist_rejects_leet_speak_civit(self):
        """
        FAIL-TO-PASS: Leet-speak variants of 'civit' should be blocked.
        At base commit: FAIL (variants not in blocklist)
        After fix: PASS (variants added to partial blocklist)
        """
        leet_variants = [
            "c1vitai",
            "civ1tai",
            "c1v1tai",
            "C1VIT_staff",
            "xCIV1Tx",
        ]
        for username in leet_variants:
            self.assertFalse(
                is_username_permitted(username, self.blocklist),
                f"Expected {username} (leet-speak) to be blocked but it was allowed"
            )

    def test_blocklist_allows_non_matching_substrings(self):
        """
        Substrings that don't match should still be allowed (p2p).
        'civic' and 'civil' should NOT be blocked as they don't contain 'civit'.
        """
        allowed = ["civic", "civil"]
        for username in allowed:
            self.assertTrue(
                is_username_permitted(username, self.blocklist),
                f"Expected {username} to be allowed but it was blocked"
            )


class TestBlocklistJsonStructure(unittest.TestCase):
    """Tests that verify the blocklist JSON structure is correct."""

    def setUp(self):
        self.blocklist = load_blocklist()

    def test_blocklist_has_partial_key(self):
        """Blocklist JSON should have 'partial' key (p2p)."""
        self.assertIn("partial", self.blocklist)

    def test_blocklist_has_exact_key(self):
        """Blocklist JSON should have 'exact' key (p2p)."""
        self.assertIn("exact", self.blocklist)

    def test_blocklist_partial_is_array(self):
        """Blocklist 'partial' should be an array (p2p)."""
        self.assertIsInstance(self.blocklist["partial"], list)

    def test_blocklist_exact_is_array(self):
        """Blocklist 'exact' should be an array (p2p)."""
        self.assertIsInstance(self.blocklist["exact"], list)


class TestRepoCI(unittest.TestCase):
    """Tests that verify repo's CI infrastructure works (pass_to_pass)."""

    def test_repo_vitest_unit_tests(self):
        """Repo's vitest unit tests pass (pass_to_pass).

        Runs a subset of vitest tests that pass cleanly at base commit.
        This verifies the test infrastructure is working.
        """
        # Run vitest on a specific test file that passes cleanly
        result = subprocess.run(
            ["./node_modules/.bin/vitest", "run",
             "src/server/games/daily-challenge/__tests__/challenge-helpers.test.ts"],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=REPO,
        )
        # Vitest exits 0 when tests pass
        assert result.returncode == 0, (
            f"Vitest unit tests failed:\n"
            f"stdout: {result.stdout[-500:]}\n"
            f"stderr: {result.stderr[-500:]}"
        )

    def test_repo_vitest_multiple_pass(self):
        """Multiple repo vitest test files pass (pass_to_pass).

        Runs several vitest test files that pass at base commit.
        """
        test_files = [
            "src/server/games/daily-challenge/template-engine.test.ts",
            "src/server/games/daily-challenge/daily-challenge-scoring.test.ts",
            "src/server/jobs/__tests__/process-strikes.test.ts",
        ]
        for test_file in test_files:
            result = subprocess.run(
                ["./node_modules/.bin/vitest", "run", test_file],
                capture_output=True,
                text=True,
                timeout=120,
                cwd=REPO,
            )
            assert result.returncode == 0, (
                f"Vitest test {test_file} failed:\n"
                f"stdout: {result.stdout[-500:]}\n"
                f"stderr: {result.stderr[-500:]}"
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)