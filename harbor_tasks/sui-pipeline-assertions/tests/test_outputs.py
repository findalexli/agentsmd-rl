#!/usr/bin/env python3
"""Tests for sui-indexer-alt-framework pipeline assertions fix.

PR #26022 changes debug_assert to assert in two places and adds a new
bounds check to catch unrecoverable pipeline states.
"""

import subprocess
import re

REPO = "/workspace/sui"
FILE_PATH = "crates/sui-indexer-alt-framework/src/pipeline/mod.rs"


# =============================================================================
# Pass-to-Pass Tests: Repo CI/CD checks that should pass on both base and fixed
# =============================================================================

def test_repo_fmt():
    """Repo code formatting passes (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "fmt", "--check"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"Format check failed:\n{r.stderr[-500:]}{r.stdout[-500:]}"


def test_repo_clippy():
    """Repo clippy lints pass (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "clippy", "--package", "sui-indexer-alt-framework", "--", "-D", "warnings"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"Clippy check failed:\n{r.stderr[-500:]}{r.stdout[-500:]}"


def test_repo_check():
    """Repo typecheck passes (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "check", "--package", "sui-indexer-alt-framework"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"Typecheck failed:\n{r.stderr[-500:]}{r.stdout[-500:]}"


# =============================================================================
# Fail-to-Pass Tests: Verify the fix was applied correctly
# =============================================================================

def _read_source():
    """Read the source file content."""
    with open(f"{REPO}/{FILE_PATH}", "r") as f:
        return f.read()

def test_add_uses_assert_not_debug_assert():
    """The add() method should use assert_eq! not debug_assert_eq! (f2p)."""
    content = _read_source()

    # Find the add method
    add_method_match = re.search(
        r'fn add\(&mut self, other: WatermarkPart\)\s*\{([^}]+)\}',
        content,
        re.DOTALL
    )
    assert add_method_match, "Could not find add() method"

    add_body = add_method_match.group(1)

    # Should use assert_eq! not debug_assert_eq!
    assert "assert_eq!" in add_body, "add() should use assert_eq!"
    assert "debug_assert_eq!" not in add_body, "add() should not use debug_assert_eq!"

def test_take_uses_assert_not_debug_assert():
    """The take() method should use assert! not debug_assert! (f2p)."""
    content = _read_source()

    # Find the take method
    take_method_match = re.search(
        r'fn take\(&mut self, rows: usize\)\s*->\s*WatermarkPart\s*\{([^}]+)\}',
        content,
        re.DOTALL
    )
    assert take_method_match, "Could not find take() method"

    take_body = take_method_match.group(1)

    # Should use assert! not debug_assert!
    # The assertion is about batch_rows >= rows
    assert "assert!" in take_body, "take() should use assert!"
    assert "debug_assert!" not in take_body, "take() should not use debug_assert!"

def test_add_has_batch_rows_bounds_check():
    """The add() method should check that batch_rows <= total_rows (f2p)."""
    content = _read_source()

    # Find the add method
    add_method_match = re.search(
        r'fn add\(&mut self, other: WatermarkPart\)\s*\{([^}]+)\}',
        content,
        re.DOTALL
    )
    assert add_method_match, "Could not find add() method"

    add_body = add_method_match.group(1)

    # Should have the new bounds check assertion - check for the pattern
    # (may have self. prefix)
    assert re.search(r'batch_rows\s*<=\s*(?:self\.)?total_rows', add_body), \
        "add() should check batch_rows <= total_rows"

def test_patch_applied_correctly():
    """All three changes from the patch should be present (f2p/p2p hybrid)."""
    content = _read_source()

    # Find the add method
    add_method_match = re.search(
        r'fn add\(&mut self, other: WatermarkPart\)\s*\{([^}]+)\}',
        content,
        re.DOTALL
    )
    assert add_method_match, "Could not find add() method"
    add_body = add_method_match.group(1)

    # Find the take method
    take_method_match = re.search(
        r'fn take\(&mut self, rows: usize\)\s*->\s*WatermarkPart\s*\{([^}]+)\}',
        content,
        re.DOTALL
    )
    assert take_method_match, "Could not find take() method"
    take_body = take_method_match.group(1)

    # All three assertions should be in place
    assertions = [
        ("assert_eq!" in add_body and "debug_assert_eq!" not in add_body,
         "add() uses assert_eq! not debug_assert_eq!"),
        (re.search(r'batch_rows\s*<=\s*(?:self\.)?total_rows', add_body),
         "add() has batch_rows <= total_rows check"),
        ("assert!" in take_body and "debug_assert!" not in take_body,
         "take() uses assert! not debug_assert!"),
    ]

    for passed, description in assertions:
        assert passed, f"Missing: {description}"
