"""Tests for Move compiler byte string hex escape fix."""

import subprocess
import tempfile
import os

REPO = "/workspace/sui"
MOVE_COMPILER_PATH = f"{REPO}/external-crates/move/crates/move-compiler"


def test_multibyte_hex_escape_produces_error_not_ice():
    r"""
    Test that multi-byte UTF-8 character after \x escape produces proper error.

    This was previously causing an internal compiler error (ICE) because
    the hex::decode would fail on multi-byte UTF-8 characters, and the
    error was marked as unreachable.
    """
    # Create test file with the problematic byte string
    test_code = '''module 0x42::m {
    fun f(): vector<u8> {
        b"\\xAñ"
    }
}
'''

    with tempfile.NamedTemporaryFile(mode='w', suffix='.move', delete=False) as f:
        f.write(test_code)
        test_file = f.name

    try:
        # Run move compiler on the test file
        result = subprocess.run(
            ["cargo", "run", "-p", "move-compiler", "--bin", "move-build", "--",
             test_file],
            capture_output=True,
            text=True,
            timeout=300,
            cwd=f"{REPO}/external-crates/move"
        )

        # The compiler should fail with an error, not succeed
        assert result.returncode != 0, "Expected compilation to fail with error"

        output = result.stdout + result.stderr

        # Should contain the proper error message, not an ICE/unreachable
        assert "Invalid hexadecimal character" in output, \
            f"Expected 'Invalid hexadecimal character' in error output, got:\n{output}"

        # Should NOT contain ICE/unreachable panic message
        assert "ICE unexpected error" not in output, \
            f"Got internal compiler error (ICE), expected proper error message:\n{output}"

        # Should NOT contain panic/backtrace
        assert "panic" not in output.lower() or "thread" not in output.lower(), \
            f"Got panic/backtrace, expected proper error:\n{output}"

    finally:
        os.unlink(test_file)


def test_valid_byte_string_compiles():
    r"""
    Test that valid byte strings still compile correctly.
    This ensures the fix doesn't break normal functionality.
    """
    test_code = '''module 0x42::m {
    fun f(): vector<u8> {
        b"\\x41\\x42\\x43"  // Valid hex escapes
    }

    fun g(): vector<u8> {
        b"hello world"  // Regular ASCII string
    }
}
'''

    with tempfile.NamedTemporaryFile(mode='w', suffix='.move', delete=False) as f:
        f.write(test_code)
        test_file = f.name

    try:
        result = subprocess.run(
            ["cargo", "run", "-p", "move-compiler", "--bin", "move-build", "--",
             test_file],
            capture_output=True,
            text=True,
            timeout=300,
            cwd=f"{REPO}/external-crates/move"
        )

        output = result.stdout + result.stderr
        assert result.returncode == 0, \
            f"Valid byte string should compile, but got error:\n{output}"

    finally:
        os.unlink(test_file)


def test_hex_escape_error_variations():
    r"""
    Test various hex escape error scenarios.
    """
    test_cases = [
        # (code, should_have_error)
        ('b"\\xAñ"', True),   # Multi-byte UTF-8 in first position
        ('b"\\xñA"', True),   # Multi-byte UTF-8 in second position
        ('b"\\xAB"', False),  # Valid hex escape
        ('b"\\x01"', False),  # Valid hex escape
    ]

    for byte_string, should_error in test_cases:
        test_code = f'''module 0x42::m {{
    fun f(): vector<u8> {{
        {byte_string}
    }}
}}
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.move', delete=False) as f:
            f.write(test_code)
            test_file = f.name

        try:
            result = subprocess.run(
                ["cargo", "run", "-p", "move-compiler", "--bin", "move-build", "--",
                 test_file],
                capture_output=True,
                text=True,
                timeout=300,
                cwd=f"{REPO}/external-crates/move"
            )

            output = result.stdout + result.stderr

            if should_error:
                assert result.returncode != 0, \
                    f"Expected error for {byte_string}"
                assert "Invalid hexadecimal character" in output or "E01007" in output, \
                    f"Expected proper error for {byte_string}, got:\n{output}"
            else:
                assert result.returncode == 0, \
                    f"Expected success for {byte_string}, got error:\n{output}"

        finally:
            os.unlink(test_file)


def test_move_compiler_byte_string_tests():
    """
    Run the move-compiler's existing byte string tests to ensure they still pass.
    """
    result = subprocess.run(
        ["cargo", "test", "-p", "move-compiler", "byte_string", "--", "--nocapture"],
        capture_output=True,
        text=True,
        timeout=600,
        cwd=f"{REPO}/external-crates/move"
    )

    output = result.stdout + result.stderr
    assert result.returncode == 0, \
        f"Byte string tests failed:\n{output[-2000:]}"


def test_move_compiler_check_passes():
    """
    Test that the move-compiler crate compiles without errors.
    """
    result = subprocess.run(
        ["cargo", "check", "-p", "move-compiler"],
        capture_output=True,
        text=True,
        timeout=600,
        cwd=f"{REPO}/external-crates/move"
    )

    output = result.stdout + result.stderr
    assert result.returncode == 0, \
        f"cargo check failed:\n{output[-1000:]}"


def test_move_compiler_all_tests_pass():
    """
    Repo CI: All move-compiler tests pass (pass_to_pass).
    Ensures the fix doesn't break any existing functionality.
    """
    result = subprocess.run(
        ["cargo", "test", "-p", "move-compiler", "--", "--test-threads=4"],
        capture_output=True,
        text=True,
        timeout=600,
        cwd=f"{REPO}/external-crates/move"
    )

    output = result.stdout + result.stderr
    assert result.returncode == 0, \
        f"move-compiler tests failed:\n{output[-2000:]}"
