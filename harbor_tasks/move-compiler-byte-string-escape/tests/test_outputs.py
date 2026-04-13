"""
Test outputs for Move compiler byte string escape fix.

This tests that the Move compiler properly handles multi-byte UTF-8 characters
in hex escape sequences, producing proper error messages instead of panicking.
"""

import subprocess
import tempfile
import os
import sys

REPO = "/workspace/sui"
MOVE_COMPILER_PATH = f"{REPO}/external-crates/move/crates/move-compiler"


def run_move_check(move_code: str) -> tuple[int, str, str]:
    """
    Run the Move compiler check on the given Move code.
    Returns (returncode, stdout, stderr).
    """
    with tempfile.NamedTemporaryFile(mode="w", suffix=".move", delete=False) as f:
        f.write(move_code)
        temp_path = f.name

    try:
        # Create a minimal package structure for the test
        pkg_dir = tempfile.mkdtemp()
        sources_dir = os.path.join(pkg_dir, "sources")
        os.makedirs(sources_dir)

        # Write the test file
        test_file = os.path.join(sources_dir, "test.move")
        with open(test_file, "w") as f:
            f.write(move_code)

        # Write Move.toml
        move_toml = os.path.join(pkg_dir, "Move.toml")
        with open(move_toml, "w") as f:
            f.write("""[package]
name = "test_pkg"
edition = "legacy"

[dependencies]
""")

        # Run the move compiler from the external-crates/move workspace
        move_repo = f"{REPO}/external-crates/move"
        result = subprocess.run(
            ["cargo", "run", "--quiet", "-p", "move-compiler", "--bin", "move-check", "--", test_file],
            cwd=move_repo,
            capture_output=True,
            text=True,
            timeout=300
        )

        return result.returncode, result.stdout, result.stderr
    finally:
        # Cleanup
        try:
            os.unlink(temp_path)
        except:
            pass


def test_multibyte_hex_escape_error_handling():
    """
    Test that the compiler properly reports an error for multi-byte UTF-8
    characters in hex escape sequences instead of panicking.
    """
    # This is the test case from the PR - n-tilde is a multi-byte UTF-8 char
    move_code = """module 0x42::m {
    fun f(): vector<u8> {
        b"\\xA\xc3\xb1"
    }
}
"""

    returncode, stdout, stderr = run_move_check(move_code)

    # Should NOT panic - should produce a proper error message
    combined_output = stdout + stderr

    # Should NOT contain unreachable panic message (this is the bug we are testing for)
    assert "ICE unexpected error parsing hex byte string value" not in combined_output, \
        f"Compiler panicked with unreachable!() instead of proper error handling:\n{combined_output}"

    # Should NOT have a thread panic
    assert "thread 'main' panicked" not in combined_output, \
        f"Compiler panicked instead of producing proper error:\n{combined_output}"

    # Check that we get a proper error message about invalid hex character
    # This must pass AFTER confirming no panic above (i.e., only when fix is applied)
    assert "Invalid hexadecimal character" in combined_output, \
        f"Expected 'Invalid hexadecimal character' error message, but got:\nstdout: {stdout}\nstderr: {stderr}"


def test_valid_hex_escape_still_works():
    """
    Test that valid hex escape sequences still work correctly.
    """
    move_code = """module 0x42::m {
    fun f(): vector<u8> {
        b"\\xAB\\xCD"
    }
}
"""

    returncode, stdout, stderr = run_move_check(move_code)
    combined_output = stdout + stderr

    # Valid hex escapes should compile without error
    assert "Invalid hexadecimal character" not in combined_output, \
        f"Valid hex escapes should not produce errors:\n{combined_output}"
    assert "thread 'main' panicked" not in combined_output, \
        f"Compiler panicked on valid hex escape:\n{combined_output}"


def test_single_invalid_hex_character():
    """
    Test error handling for a single invalid hex character.
    """
    move_code = """module 0x42::m {
    fun f(): vector<u8> {
        b"\\xAG"
    }
}
"""

    returncode, stdout, stderr = run_move_check(move_code)
    combined_output = stdout + stderr

    # Should NOT panic
    assert "thread 'main' panicked" not in combined_output, \
        f"Compiler panicked on invalid hex char:\n{combined_output}"
    assert "ICE unexpected error parsing hex byte string value" not in combined_output, \
        f"Compiler panicked with internal error:\n{combined_output}"

    # Should produce an error (G is not a valid hex digit)
    assert "Invalid hexadecimal character" in combined_output, \
        f"Expected 'Invalid hexadecimal character' error for hex char 'G':\nstdout: {stdout}\nstderr: {stderr}"


def test_various_multibyte_chars():
    """
    Test with various multi-byte UTF-8 characters in hex escapes.
    """
    # Test with emoji (4 bytes in UTF-8)
    move_code = """module 0x42::m {
    fun f(): vector<u8> {
        b"\\xA\xf0\x9f\x98\x80"
    }
}
"""

    returncode, stdout, stderr = run_move_check(move_code)
    combined_output = stdout + stderr

    # Should produce proper error, not panic
    assert "thread 'main' panicked" not in combined_output, \
        f"Compiler panicked on emoji in hex escape:\n{combined_output}"
    assert "ICE unexpected error parsing hex byte string value" not in combined_output, \
        f"Compiler panicked with internal error:\n{combined_output}"

    # Should report the specific error message
    assert "Invalid hexadecimal character" in combined_output, \
        f"Expected 'Invalid hexadecimal character' error for emoji in hex escape:\n{combined_output}"


def test_hex_escape_at_end():
    """
    Test hex escape at end of string (edge case).
    """
    move_code = """module 0x42::m {
    fun f(): vector<u8> {
        b"\\xA"
    }
}
"""

    returncode, stdout, stderr = run_move_check(move_code)
    combined_output = stdout + stderr

    # Should handle this gracefully (either error or accept)
    # The key is it should not panic
    assert "thread 'main' panicked" not in combined_output, \
        f"Compiler panicked on incomplete hex escape:\n{combined_output}"


def test_compiler_unit_tests():
    """
    Run the existing Move compiler unit tests to ensure no regressions.
    """
    move_repo = f"{REPO}/external-crates/move"
    result = subprocess.run(
        ["cargo", "test", "--quiet", "-p", "move-compiler", "--lib"],
        cwd=move_repo,
        capture_output=True,
        text=True,
        timeout=600
    )

    # Tests should pass (return code 0)
    assert result.returncode == 0, \
        f"Move compiler unit tests failed:\nstdout: {result.stdout}\nstderr: {result.stderr}"


def test_byte_string_expansion_compiles():
    """
    Test that the byte_string.rs module compiles without errors.
    """
    move_repo = f"{REPO}/external-crates/move"
    result = subprocess.run(
        ["cargo", "check", "-p", "move-compiler"],
        cwd=move_repo,
        capture_output=True,
        text=True,
        timeout=300
    )

    assert result.returncode == 0, \
        f"move-compiler failed to compile:\nstderr: {result.stderr}"


def test_move_compiler_formatting():
    """
    Repo code formatting check (pass_to_pass).
    Verifies move-compiler code follows standard Rust formatting.
    """
    move_repo = f"{REPO}/external-crates/move"
    result = subprocess.run(
        ["cargo", "fmt", "--check", "--all"],
        cwd=move_repo,
        capture_output=True,
        text=True,
        timeout=60
    )

    assert result.returncode == 0, \
        f"Formatting check failed:\nstdout: {result.stdout}\nstderr: {result.stderr}"


def test_move_compiler_clippy():
    """
    Move compiler clippy lints pass (pass_to_pass).
    CI command from .github/workflows/external.yml.
    """
    move_repo = f"{REPO}/external-crates/move"
    r = subprocess.run(
        ["cargo", "move-clippy", "-D", "warnings"],
        capture_output=True, text=True, timeout=600, cwd=move_repo,
    )
    assert r.returncode == 0, f"Move clippy failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


def test_move_compiler_unit_tests_p2p():
    """
    Move compiler unit tests pass at base commit (pass_to_pass).
    Runs the library tests for move-compiler.
    """
    move_repo = f"{REPO}/external-crates/move"
    r = subprocess.run(
        ["cargo", "test", "-p", "move-compiler", "--lib", "--quiet"],
        capture_output=True, text=True, timeout=600, cwd=move_repo,
    )
    assert r.returncode == 0, f"Move compiler unit tests failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


def test_repo_xlint():
    """Repo's custom linter passes (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "xlint"], capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"Lint failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


def test_repo_git_checks():
    """Repo's git checks pass (pass_to_pass)."""
    r = subprocess.run(
        ["./scripts/git-checks.sh"], capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"Git checks failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"



def test_move_compiler_cargo_check():
    """Move compiler compiles without errors (cargo check pass_to_pass)."""
    move_repo = f"{REPO}/external-crates/move"
    r = subprocess.run(
        ["cargo", "check", "-p", "move-compiler"],
        capture_output=True, text=True, timeout=300, cwd=move_repo,
    )
    assert r.returncode == 0, f"cargo check failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"
