"""Test that the pipeline assertions correctly panic in unrecoverable states.

This PR changes debug_assert to assert in the WatermarkPart methods,
ensuring that invariant violations are caught in release builds.
"""

import subprocess
import re
import sys

REPO = "/workspace/sui"
TARGET_FILE = "crates/sui-indexer-alt-framework/src/pipeline/mod.rs"


def test_compilation():
    """Verify the crate compiles successfully."""
    result = subprocess.run(
        ["cargo", "check", "-p", "sui-indexer-alt-framework"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )
    assert result.returncode == 0, f"Compilation failed:\n{result.stderr}"


def test_checkpoint_assertion_uses_assert():
    """Verify that checkpoint equality check uses assert_eq, not debug_assert_eq."""
    with open(f"{REPO}/{TARGET_FILE}", "r") as f:
        content = f.read()

    # Find the add method and check its first assertion
    # Should use assert_eq! not debug_assert_eq!
    add_method_pattern = r'fn add\(&mut self, other: WatermarkPart\)\s*\{([^}]+)\}'
    match = re.search(add_method_pattern, content)

    if match:
        add_body = match.group(1)
        # Check that first assertion is assert_eq not debug_assert_eq
        assert "assert_eq!(self.checkpoint(), other.checkpoint())" in add_body, \
            "First assertion in add() should use assert_eq!, not debug_assert_eq!"
        assert "debug_assert_eq!(self.checkpoint(), other.checkpoint())" not in add_body, \
            "Found debug_assert_eq! instead of assert_eq! in add() method"
    else:
        # Multi-line body - search more broadly
        lines = content.split('\n')
        in_add_method = False
        brace_count = 0
        add_body_lines = []

        for line in lines:
            if 'fn add(&mut self, other: WatermarkPart)' in line:
                in_add_method = True
                brace_count = 0

            if in_add_method:
                add_body_lines.append(line)
                brace_count += line.count('{') - line.count('}')
                if brace_count == 0 and '{' in ''.join(add_body_lines):
                    break

        add_body = '\n'.join(add_body_lines)
        assert "assert_eq!(self.checkpoint(), other.checkpoint())" in add_body, \
            "First assertion in add() should use assert_eq!, not debug_assert_eq!"
        assert "debug_assert_eq!(self.checkpoint(), other.checkpoint())" not in add_body, \
            "Found debug_assert_eq! instead of assert_eq! in add() method"


def test_batch_rows_bounds_assertion():
    """Verify that batch_rows <= total_rows assertion is present and uses assert!."""
    with open(f"{REPO}/{TARGET_FILE}", "r") as f:
        content = f.read()

    # Look for the new assertion that batch_rows <= total_rows
    assert 'assert!(\n            self.batch_rows <= self.total_rows,' in content or \
           'assert!(self.batch_rows <= self.total_rows,' in content or \
           'batch_rows ({}) exceeded total_rows ({})' in content, \
        "Missing batch_rows <= total_rows assertion in add() method"

    # Ensure it uses assert! not debug_assert!
    assert "debug_assert!(\n            self.batch_rows <= self.total_rows," not in content and \
           "debug_assert!(self.batch_rows <= self.total_rows," not in content, \
        "Found debug_assert! instead of assert! for batch_rows bounds check"


def test_take_rows_assertion_uses_assert():
    """Verify that take() method uses assert! not debug_assert! for row bounds."""
    with open(f"{REPO}/{TARGET_FILE}", "r") as f:
        content = f.read()

    # Find the take method and check its assertion
    take_method_pattern = r'fn take\(&mut self, rows: usize\) -> WatermarkPart\s*\{([^}]+)\}'
    match = re.search(take_method_pattern, content)

    if match:
        take_body = match.group(1)
        # Check that it uses assert! not debug_assert!
        assert "assert!(\n            self.batch_rows >= rows," in take_body or \
               "assert!(self.batch_rows >= rows," in take_body, \
            "take() should use assert! for batch_rows >= rows check"
        assert "debug_assert!(\n            self.batch_rows >= rows," not in take_body and \
               "debug_assert!(self.batch_rows >= rows," not in take_body, \
            "Found debug_assert! instead of assert! in take() method"
    else:
        # Multi-line body
        assert "assert!(\n            self.batch_rows >= rows," in content or \
               "assert!(self.batch_rows >= rows," in content, \
            "take() should use assert! for batch_rows >= rows check"
        assert "debug_assert!(\n            self.batch_rows >= rows," not in content and \
               "debug_assert!(self.batch_rows >= rows," not in content, \
            "Found debug_assert! instead of assert! in take() method"


def test_take_rows_error_message():
    """Verify the error message in take() assertion is preserved."""
    with open(f"{REPO}/{TARGET_FILE}", "r") as f:
        content = f.read()

    # The error message should be preserved
    assert '"Can\'t take more rows than are available"' in content, \
        "Error message 'Can't take more rows than are available' should be preserved"
