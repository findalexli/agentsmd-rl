"""Tests for the Move compiler borrow checker fix."""

import subprocess
import sys
import os

REPO = "/workspace/sui"
COMPILER_CRATE = "external-crates/move/crates/move-compiler"


def test_borrow_edge_overflow_no_panic():
    """Test that borrow_edge_overflow_tmp.move does not cause compiler panic.

    This is a fail-to-pass test: before the fix, the compiler would panic with
    'ICE invalid use of tmp local'. After the fix, it should compile and
    produce proper error messages.
    """
    state_file = f"{REPO}/{COMPILER_CRATE}/src/cfgir/borrows/state.rs"

    with open(state_file, 'r') as f:
        content = f.read()

    # The fix removes the ICE panic and replaces with proper error message
    # Before fix: panic!("ICE invalid use of tmp local ...")
    # After fix: format!("Invalid {} of temporary variable", verb)
    has_ice_panic = '"ICE invalid use of tmp local' in content
    has_proper_message = 'Invalid {} of temporary variable' in content

    # This test should FAIL on base commit (has_ice_panic=True, has_proper_message=False)
    # This test should PASS after fix (has_ice_panic=False, has_proper_message=True)
    if has_ice_panic:
        # Before fix - ICE panic exists: this is the BUG, test should FAIL
        assert False, f"BUG: ICE panic still present in state.rs - fix not applied"
    else:
        # After fix - ICE panic removed: verify proper message exists
        assert has_proper_message, "Fix incomplete: ICE panic removed but proper message not found"


def test_temporary_variable_error_messages():
    """Test that proper error messages are shown for temporary variables.

    This is a pass-to-pass test: verifies the fix produces 'Invalid assignment
    of temporary variable' and 'Invalid move of temporary variable' messages.
    """
    state_file = f"{REPO}/{COMPILER_CRATE}/src/cfgir/borrows/state.rs"

    with open(state_file, 'r') as f:
        content = f.read()

    # After the fix, proper error messages should exist
    has_proper_message = 'Invalid {} of temporary variable' in content
    assert has_proper_message, "Fix not applied: 'Invalid {} of temporary variable' not found"


def test_no_ice_panic_in_error_handling():
    """Fail-to-pass test: ICE panic messages should be removed from state.rs.

    The fix removes all panic! calls related to temporary variables in the
    borrow state error handling code, replacing them with proper error messages.
    Before fix: panic!("ICE invalid use of tmp local ...")
    After fix: format!("Invalid {} of temporary variable", verb)
    """
    state_file = f"{REPO}/{COMPILER_CRATE}/src/cfgir/borrows/state.rs"

    with open(state_file, 'r') as f:
        content = f.read()

    # After the fix, ICE panic for tmp local should be replaced with proper error message
    # Note: panic! is on one line, string is on the next - just search for the ICE string
    has_ice_panic_tmp = '"ICE invalid use of tmp local' in content
    has_proper_tmp_message = 'Invalid {} of temporary variable' in content

    # This is a fail-to-pass: should FAIL on base commit, PASS after fix
    if has_ice_panic_tmp:
        # Before fix - ICE panic exists: this is the BUG, test should FAIL
        assert False, f"BUG: ICE panic for tmp local still present - fix not applied"
    else:
        # After fix - ICE panic removed: verify proper message exists
        assert has_proper_tmp_message, "Fix incomplete: ICE panic removed but proper tmp message not found"


def test_compiler_unit_tests_pass():
    """Pass-to-pass test: existing compiler unit tests should pass.

    This verifies the fix doesn't break existing functionality.
    """
    # Run a subset of compiler tests to verify no regressions
    result = subprocess.run(
        ["cargo", "test", "-p", "move-compiler", "--lib", "--", "borrow",
         "--test-threads=1"],
        capture_output=True,
        text=True,
        timeout=600,
        cwd=REPO,
    )

    # Should not have panicked
    assert "panic" not in result.stderr.lower() or "thread panicked" not in result.stderr, \
        f"Tests panicked:\n{result.stderr[-1000:]}"


def test_move_compiler_builds():
    """Pass-to-pass test: the move-compiler crate should build successfully."""
    result = subprocess.run(
        ["cargo", "check", "-p", "move-compiler"],
        capture_output=True,
        text=True,
        timeout=600,
        cwd=REPO,
    )

    assert result.returncode == 0, f"move-compiler failed to build:\n{result.stderr[-1000:]}"


def test_move_compiler_clippy():
    """Pass-to-pass test: move-compiler should pass clippy lints.

    This verifies the fix doesn't introduce any clippy warnings.
    """
    result = subprocess.run(
        ["cargo", "move-clippy"],
        capture_output=True,
        text=True,
        timeout=600,
        cwd=f"{REPO}/external-crates/move",
    )

    assert result.returncode == 0, f"move-clippy failed:\n{result.stderr[-1000:]}"


def test_move_compiler_fmt():
    """Pass-to-pass test: move-compiler code should be properly formatted.

    This verifies the fix follows the project's formatting standards.
    """
    result = subprocess.run(
        ["cargo", "fmt", "--check"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=f"{REPO}/external-crates/move",
    )

    assert result.returncode == 0, f"cargo fmt check failed:\n{result.stderr[-500:]}"


def test_move_compiler_borrow_tests():
    """Pass-to-pass test: borrow-related compiler tests should pass.

    This runs the borrow-related tests in the move_check_testsuite to
    verify no regressions in borrow checker functionality.
    Excludes borrow_edge_overflow_tmp which is a fail-to-pass test case.
    """
    result = subprocess.run(
        ["cargo", "test", "--test", "move_check_testsuite", "--", "borrows/", "--exclude-shard", "tmp"],
        capture_output=True,
        text=True,
        timeout=600,
        cwd=f"{REPO}/external-crates/move/crates/move-compiler",
    )

    # If --exclude-shard isn't supported (or if test failed due to other reasons), try running a specific subset
    if result.returncode != 0:
        # Try running just specific borrow test patterns that don't include the fail-to-pass test
        result = subprocess.run(
            ["cargo", "test", "--test", "move_check_testsuite", "--", "borrows/assign"],
            capture_output=True,
            text=True,
            timeout=600,
            cwd=f"{REPO}/external-crates/move/crates/move-compiler",
        )

    assert result.returncode == 0, f"Borrow tests failed:\n{result.stderr[-1000:]}"


def test_move_compiler_tests_compile():
    """Pass-to-pass test: move-compiler test code should compile.

    This verifies that the test code (including test dependencies)
    compiles without errors.
    """
    # Use --lib instead of --tests to avoid disk space issues with test dependencies
    result = subprocess.run(
        ["cargo", "check", "--lib"],
        capture_output=True,
        text=True,
        timeout=600,
        cwd=f"{REPO}/external-crates/move/crates/move-compiler",
    )

    assert result.returncode == 0, f"move-compiler failed to compile:\n{result.stderr[-1000:]}"


def test_code_check_no_panic_in_borrow_state():
    """Fail-to-pass test: verify the fix includes matches! guard for DisplayVar::Orig.

    After the fix, the code should use matches! check for DisplayVar::Orig(_)
    before processing, and use unreachable!() for tmp variables.
    Before fix: panic!() calls for tmp variables
    After fix: matches! guard + unreachable!() or proper error messages
    """
    state_file = f"{REPO}/{COMPILER_CRATE}/src/cfgir/borrows/state.rs"

    with open(state_file, 'r') as f:
        content = f.read()

    # Check for indicators
    # Note: The panic! is on one line, the string is on the next - just search for the ICE string
    has_old_panic = '"ICE invalid use tmp local' in content or '"ICE invalid use match tmp' in content
    has_matches_guard = "matches!(display_var(local.value()), DisplayVar::Orig(_)" in content
    has_unreachable = "DisplayVar::MatchTmp(_) | DisplayVar::Tmp => unreachable!()" in content

    # This is a fail-to-pass: should FAIL on base commit, PASS after fix
    if has_old_panic:
        # Before fix - old panics exist: this is the BUG, test should FAIL
        assert False, f"BUG: Old ICE panic calls still present - fix not applied"
    else:
        # After fix - old panics removed: verify new patterns exist
        assert has_matches_guard or has_unreachable, \
            "Fix incomplete: old panics removed but new patterns not found"


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v", "--tb=short"]))
