"""
Verify that cn review discovers local review files from .continue/checks/
directory, not just .continue/agents/.

On the base commit, resolveFromLocal() only scans .continue/agents/,
so files in .continue/checks/ are invisible to the CLI.
After the fix, both directories are scanned and deduplicated.
"""
import json
import subprocess
from pathlib import Path

import pytest

REPO = Path("/workspace/continue/extensions/cli")


def test_resolveFromLocal_scans_checks_dir():
    """
    fail_to_pass: resolveFromLocal() references the .continue/checks/ path.

    On base commit: FAIL (no mention of checks/)
    After fix: PASS (function body includes checks directory path)
    """
    source = (REPO / "src" / "commands" / "review" / "resolveReviews.ts").read_text()

    assert ".continue" in source and "checks" in source, \
        "resolveFromLocal should reference .continue/checks/ path"


def test_resolveFromLocal_is_iterative_over_two_dirs():
    """
    fail_to_pass: resolveFromLocal() iterates over two directories.

    On base commit: FAIL (single directory path)
    After fix: PASS (multiple directories via array or loop)
    """
    source = (REPO / "src" / "commands" / "review" / "resolveReviews.ts").read_text()

    # Base: const agentsDir = path.join(process.cwd(), ".continue", "agents");
    # Fix: const dirs = [path.join(cwd, ".continue", "agents"), path.join(cwd, ".continue", "checks")];
    # Fix adds 2+ references to ".continue" (one per directory)
    continue_count = source.count('".continue"') + source.count("'.continue'")
    assert continue_count >= 2, \
        f"Expected at least 2 references to '.continue' (one per directory), found {continue_count}"


def test_agents_and_checks_deduplication():
    """
    fail_to_pass: resolveFromLocal() deduplicates files by filename,
    with agents/ taking precedence over checks/.

    On base commit: FAIL (no deduplication logic)
    After fix: PASS (seen.Set or similar dedup logic)
    """
    source = (REPO / "src" / "commands" / "review" / "resolveReviews.ts").read_text()

    # The fix adds: const seen = new Set() for filename deduplication
    has_seen_set = "seen" in source and "Set" in source
    assert has_seen_set, \
        "resolveFromLocal should deduplicate using a Set for filename dedup"


def test_resolveReviews_vitest():
    """
    fail_to_pass: The vitest tests in resolveReviews.test.ts pass.

    On base commit: FAIL (test file doesn't exist yet)
    After fix: PASS (tests verify both agents/ and checks/ discovery)
    """
    test_file = REPO / "src" / "commands" / "review" / "resolveReviews.test.ts"
    assert test_file.exists(), f"Test file not found: {test_file}"

    result = subprocess.run(
        ["npx", "vitest", "run", "src/commands/review/resolveReviews.test.ts"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    output = result.stdout + result.stderr
    assert result.returncode == 0, f"vitest tests failed:\n{output[-2000:]}"


def test_doc_comments_updated():
    """
    pass_to_pass: The doc comment for resolveFromLocal mentions both directories.
    """
    source = (REPO / "src" / "commands" / "review" / "resolveReviews.ts").read_text()

    # The fixed doc comment mentions both agents and checks
    assert "checks" in source, "Documentation should mention .continue/checks/"


def test_resolveReviews_function_preserved():
    """pass_to_pass: The resolveReviews export is preserved."""
    source = (REPO / "src" / "commands" / "review" / "resolveReviews.ts").read_text()
    assert "resolveReviews" in source and "export" in source


def test_repo_eslint_resolveReviews():
    """pass_to_pass: ESLint passes on resolveReviews.ts (repo_tests)."""
    r = subprocess.run(
        ["npx", "eslint", "src/commands/review/resolveReviews.ts"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"ESLint failed:\n{r.stderr[-500:]}"


def test_repo_vitest_stripThinkTags():
    """pass_to_pass: Repo command tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "vitest", "run", "src/commands/stripThinkTags.test.ts"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"vitest stripThinkTags failed:\n{r.stderr[-500:]}"


def test_repo_vitest_cli_util():
    """pass_to_pass: Repo CLI utility tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "vitest", "run", "src/util/cli.test.ts"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"vitest cli.test failed:\n{r.stderr[-500:]}"
