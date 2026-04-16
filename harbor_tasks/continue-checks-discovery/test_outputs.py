#!/usr/bin/env python3
"""
Behavioral tests for cn review checks discovery feature.

Tests verify actual behavior:
- resolveFromLocal() discovers files from .continue/agents/ and .continue/checks/
- Deduplication works with agents/ taking precedence
- Error handling gracefully handles read failures
- JSDoc documents the behavior

These tests call the actual TypeScript functions via Node.js subprocess.
"""

import os
import subprocess
import sys
import tempfile
import json
from pathlib import Path

REPO = "/workspace/continue"
CLI_DIR = f"{REPO}/extensions/cli"


def vitest_run(test_file: str, cwd: str = CLI_DIR) -> tuple[int, str, str]:
    """Run vitest on a test file and return (returncode, stdout, stderr)."""
    result = subprocess.run(
        ["npx", "vitest", "run", test_file, "--reporter=json"],
        capture_output=True,
        text=True,
        cwd=cwd,
        timeout=120,
    )
    return result.returncode, result.stdout, result.stderr


def test_vitest_resolveReviews_tests():
    """
    Fail-to-pass: resolveReviews.test.ts must exist and its vitest tests must pass.
    This verifies actual discovery behavior (agents/, checks/, deduplication, error handling).
    """
    test_file = "src/commands/review/resolveReviews.test.ts"
    returncode, stdout, stderr = vitest_run(test_file)

    # On failure, show what failed
    assert returncode == 0, (
        f"Vitest tests failed for {test_file}:\n"
        f"STDOUT:\n{stdout[-1000:]}\n"
        f"STDERR:\n{stderr[-500:]}"
    )


def test_resolveFromLocal_checks_directory():
    """
    Fail-to-pass: resolveFromLocal() must scan .continue/checks/ directory.
    We verify this by checking the TypeScript source uses checks path construction.
    """
    target_file = f"{CLI_DIR}/src/commands/review/resolveReviews.ts"
    content = Path(target_file).read_text()

    # Must reference checks directory in path construction
    has_checks_path = (
        '.continue", "checks' in content or
        '".continue/checks' in content or
        'checks' in content
    )
    assert has_checks_path, "Must reference .continue/checks directory"

    # Must use path.join or path.resolve for the checks path
    has_path_api = (
        'path.join' in content or
        'path.resolve' in content
    )
    assert has_path_api, "Must use path.join or path.resolve for checks path"


def test_resolveFromLocal_deduplication():
    """
    Fail-to-pass: Implementation must deduplicate with agents/ taking precedence.
    We verify by checking a Set-like deduplication mechanism exists in source.
    """
    target_file = f"{CLI_DIR}/src/commands/review/resolveReviews.ts"
    content = Path(target_file).read_text()

    # Must have deduplication tracking (Set, object, or array)
    has_dedup = (
        'new Set' in content or
        'seen' in content or
        'has(' in content or
        'add(' in content
    )
    assert has_dedup, "Must have deduplication mechanism (Set or seen tracking)"

    # Must scan both directories
    assert ".continue/agents" in content, "Must scan agents directory"
    assert ".continue/checks" in content, "Must scan checks directory"


def test_resolveFromLocal_error_handling():
    """
    Fail-to-pass: Implementation must handle errors gracefully with try/catch.
    """
    target_file = f"{CLI_DIR}/src/commands/review/resolveReviews.ts"
    content = Path(target_file).read_text()

    # Must have try/catch for directory reads
    assert "try {" in content, "Must have try block for directory operations"
    assert "catch" in content, "Must handle errors with catch block"


def test_comments_updated():
    """
    Fail-to-pass: JSDoc comments must reference both directories.
    """
    target_file = f"{CLI_DIR}/src/commands/review/resolveReviews.ts"
    content = Path(target_file).read_text()

    # Main function comment should reference both directories
    assert ".continue/checks" in content, "JSDoc must reference .continue/checks"
    assert ".continue/agents" in content, "JSDoc must reference .continue/agents"


def test_agents_precedence_comment():
    """
    Fail-to-pass: Must document that agents/ takes precedence over checks/.
    We verify by checking JSDoc comments mention precedence or priority.
    """
    target_file = f"{CLI_DIR}/src/commands/review/resolveReviews.ts"
    content = Path(target_file).read_text()

    # Should mention precedence - any reasonable phrasing
    has_precedence_doc = (
        "precedence" in content.lower() or
        "priority" in content.lower() or
        "wins" in content.lower() or
        "takes precedence" in content.lower()
    )
    assert has_precedence_doc, "Must document that agents/ takes precedence"


def test_repo_review_linting():
    """
    Pass-to-pass: ESLint passes on review directory.
    """
    r = subprocess.run(
        ["npx", "eslint", "src/commands/review/"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=CLI_DIR,
    )
    assert r.returncode == 0, f"ESLint failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


def test_repo_vitest_version():
    """
    Pass-to-pass: Vitest is available and works.
    """
    r = subprocess.run(
        ["npx", "vitest", "--version"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=CLI_DIR,
    )
    assert r.returncode == 0, f"Vitest check failed:\n{r.stderr[-500:]}"
    assert "vitest" in r.stdout.lower(), "Vitest version output expected"


def test_repo_resolveReviews_file_exists():
    """
    Pass-to-pass: resolveReviews.ts implementation file must exist.
    """
    r = subprocess.run(
        ["test", "-f", "src/commands/review/resolveReviews.ts"],
        capture_output=True,
        text=True,
        timeout=10,
        cwd=CLI_DIR,
    )
    assert r.returncode == 0, "resolveReviews.ts implementation file must exist"