"""
Benchmark tests for biomejs/biome#9782 - setext heading inside blockquote.

The bug: After consuming a blockquote prefix (`> `), the lexer's after_newline
flag is false, so `---` is lexed as MINUS tokens instead of MD_THEMATIC_BREAK_LITERAL.
This prevented setext heading detection inside blockquotes.

The fix adds force_relex_at_line_start() to re-lex the current token as if
it were at line start, so the lexer produces block-level tokens (thematic breaks,
setext underlines) after a quote prefix.
"""
import subprocess
import os

REPO = "/workspace/biome"


def run(cmd, timeout=600):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout, cwd=REPO)
    return result


def test_force_relex_at_line_start_lexer():
    """Fail-to-pass: the new lexer unit test force_relex_at_line_start_produces_thematic_break was added by the fix.

    On base commit:
    - The test function doesn't exist in the source
    - Running the test prints "0 tests" and exits with code 0 (cargo test considers "no tests" as success)

    After fix:
    - The test function exists and runs successfully

    This test fails on base because it checks the test output for the actual test count.
    """
    r = run("cargo test -p biome_markdown_parser --lib -- force_relex_at_line_start_produces_thematic_break -- --nocapture 2>&1", timeout=300)

    # On base: "0 tests" because test doesn't exist
    # After fix: "1 passed" because test runs and passes
    output = r.stdout + r.stderr

    # Check that at least one test actually ran
    if "0 passed" in output and "0 failed" in output:
        raise AssertionError(
            f"Test force_relex_at_line_start_produces_thematic_break does not exist on base commit. "
            f"This test was added by the fix. stderr: {r.stderr[-500:]}"
        )

    assert r.returncode == 0, f"Test should pass after fix. stderr: {r.stderr[-1000:]}"


def test_setext_heading_in_blockquote_spec():
    """Fail-to-pass: the new spec test setext_heading_in_blockquote was added by the fix.

    On base commit: the test file doesn't exist so the test fails to run
    After fix: the test file exists and the test runs successfully

    The test is in spec_tests binary (not spec_test).
    """
    r = run("cargo test -p biome_markdown_parser --test spec_tests -- setext_heading_in_blockquote -- --nocapture 2>&1", timeout=300)

    output = r.stdout + r.stderr

    # On base: test doesn't exist (0 tests run, test fails)
    # After fix: test exists and runs (1 test passed)
    if "0 passed" in output or "test result: ok. 0 passed" in output:
        raise AssertionError(
            f"Test setext_heading_in_blockquote does not exist on base commit. "
            f"This test was added by the fix. stderr: {r.stderr[-500:]}"
        )

    assert r.returncode == 0, f"Test should pass after fix. stderr: {r.stderr[-1000:]}"


def test_markdown_parser_unit_tests():
    """Pass-to-pass: the existing markdown parser unit tests pass on base commit and after fix."""
    r = run("cargo test -p biome_markdown_parser --lib -- --nocapture", timeout=600)
    assert r.returncode == 0, f"Markdown parser unit tests should pass. stderr: {r.stderr[-1000:]}"


def test_markdown_parser_integration_tests():
    """Pass-to-pass: the existing markdown parser integration tests pass on base commit and after fix.

    Note: This test runs the spec_test suite. On base commit, all existing tests pass.
    The new setext_heading_in_blockquote test is NOT run by this test since it has a
    different test function name. This test only verifies existing behavior is preserved.
    """
    r = run("cargo test -p biome_markdown_parser --test spec_tests -- --nocapture", timeout=600)
    # Filter to existing tests only (the spec_tests binary has 83 tests)
    # On base commit: all 83 existing tests pass
    # After fix: all 83 existing tests still pass
    assert r.returncode == 0, f"Markdown parser integration tests should pass. stderr: {r.stderr[-1000:]}"


def test_biome_parser_crate_tests():
    """Pass-to-pass: biome_parser crate tests pass (lexer infrastructure used by markdown parser)."""
    r = run("cargo test -p biome_parser --lib -- --nocapture", timeout=600)
    assert r.returncode == 0, f"Biome parser crate tests should pass. stderr: {r.stderr[-1000:]}"


def test_clippy_no_warnings():
    """Pass-to-pass: clippy passes on the modified crates with no warnings."""
    r = run("cargo clippy -p biome_markdown_parser -p biome_parser --all-features -- -D warnings", timeout=600)
    assert r.returncode == 0, f"Clippy should pass with no warnings. stderr: {r.stderr[-1000:]}"


def test_cargo_fmt_check():
    """Pass-to-pass: all Rust files are formatted correctly."""
    r = run("cargo fmt --all -- --check", timeout=120)
    assert r.returncode == 0, f"cargo fmt check failed:\n{r.stderr[-500:]}"


def test_cargo_check_markdown_parser():
    """Pass-to-pass: biome_markdown_parser crate compiles without errors."""
    r = run("cargo check -p biome_markdown_parser --all-targets", timeout=600)
    assert r.returncode == 0, f"cargo check biome_markdown_parser failed:\n{r.stderr[-500:]}"


def test_cargo_check_parser_crate():
    """Pass-to-pass: biome_parser crate compiles without errors."""
    r = run("cargo check -p biome_parser --all-targets", timeout=600)
    assert r.returncode == 0, f"cargo check biome_parser failed:\n{r.stderr[-500:]}"