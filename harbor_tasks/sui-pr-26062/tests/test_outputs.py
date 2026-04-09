"""Tests for sui-display implicit :json transform feature."""

import subprocess
import sys
import json

REPO = "/workspace/sui"
DISPLAY_CRATE = "crates/sui-display"


def test_cargo_check():
    """Crate compiles without errors (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "check", "-p", "sui-display"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert r.returncode == 0, f"cargo check failed:\n{r.stderr}"


def test_cargo_clippy():
    """Crate passes clippy lints (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "clippy", "-p", "sui-display", "--", "-D", "warnings"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert r.returncode == 0, f"cargo clippy failed:\n{r.stderr[-500:]}"


def test_cargo_fmt():
    """Crate code is properly formatted (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "fmt", "--check", "-p", "sui-display"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"cargo fmt check failed:\n{r.stderr}"


def test_transform_enum_no_default():
    """Transform enum no longer has #[default] on Str variant - f2p check."""
    parser_file = f"{REPO}/{DISPLAY_CRATE}/src/v2/parser.rs"
    with open(parser_file) as f:
        content = f.read()

    # After fix: Transform enum should NOT have #[derive(Default...)] and NOT have #[default] on Str
    # Check that Str variant doesn't have #[default] attribute
    lines = content.split("\n")
    in_transform_enum = False
    str_variant_line = None
    derive_line = None

    for i, line in enumerate(lines):
        if "pub enum Transform" in line:
            in_transform_enum = True
            # Check the derive line before this
            if i > 0:
                derive_line = lines[i - 1]
        if in_transform_enum and "Str," in line:
            str_variant_line = line
            break

    # The derive line should NOT contain Default
    assert derive_line is not None, "Could not find derive line for Transform enum"
    assert "Default" not in derive_line, f"Transform enum still has Default derive: {derive_line}"

    # The Str variant should NOT have #[default] attribute
    assert str_variant_line is not None, "Could not find Str variant"
    assert "#[default]" not in str_variant_line, f"Str variant still has #[default]: {str_variant_line}"


def test_strand_value_has_optional_transform():
    """Strand::Value has Option<Transform> instead of Transform - f2p check."""
    value_file = f"{REPO}/{DISPLAY_CRATE}/src/v2/value.rs"
    with open(value_file) as f:
        content = f.read()

    # Look for the Strand::Value variant with Option<Transform>
    assert "transform: Option<Transform>" in content, \
        "Strand::Value should have transform: Option<Transform>"


def test_writer_handles_none_transform():
    """Writer handles None transform by checking if atom can be formatted as str - f2p check."""
    writer_file = f"{REPO}/{DISPLAY_CRATE}/src/v2/writer.rs"
    with open(writer_file) as f:
        content = f.read()

    # Check for the pattern matching None | Some(Transform::Json)
    assert "transform: None | Some(Transform::Json)" in content, \
        "Writer should match on None | Some(Transform::Json)"

    # Check that writer tries format_as_str for None transform on atoms
    assert "format_as_str" in content, \
        "Writer should use format_as_str for atom values"

    # Check that transform.is_none() is checked
    assert "transform.is_none()" in content, \
        "Writer should check transform.is_none()"


def test_interpreter_passes_transform_directly():
    """Interpreter passes transform directly without unwrapping - f2p check."""
    interpreter_file = f"{REPO}/{DISPLAY_CRATE}/src/v2/interpreter.rs"
    with open(interpreter_file) as f:
        content = f.read()

    # Check that the interpreter no longer calls unwrap_or_default()
    assert "unwrap_or_default()" not in content, \
        "Interpreter should not use unwrap_or_default() for transform"

    # Check that it passes transform directly with dereference
    assert "transform: *transform" in content, \
        "Interpreter should pass transform: *transform directly"


def test_format_as_str_is_pub_crate():
    """format_as_str method is pub(crate) for use by writer - f2p check."""
    value_file = f"{REPO}/{DISPLAY_CRATE}/src/v2/value.rs"
    with open(value_file) as f:
        content = f.read()

    # Check that format_as_str is pub(crate)
    assert "pub(crate) fn format_as_str" in content, \
        "format_as_str should be pub(crate)"


def test_unit_test_exists():
    """Unit test for implicit JSON formatting exists - f2p check."""
    mod_file = f"{REPO}/{DISPLAY_CRATE}/src/v2/mod.rs"
    with open(mod_file) as f:
        content = f.read()

    # Check that the new test exists
    assert "test_format_single_bare_expression_falls_back_to_json" in content, \
        "Unit test for bare expression JSON fallback should exist"


def test_bare_struct_formatting():
    """Bare struct expression implicitly uses JSON formatting - behavioral f2p."""
    # Run the specific unit test that validates JSON output for structs
    r = subprocess.run(
        ["cargo", "test", "-p", "sui-display", "--lib",
         "test_format_single_bare_expression_falls_back_to_json"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    # Check that the test actually ran and passed (not "0 tests" or filtered out)
    assert r.returncode == 0 and "1 passed" in r.stdout, \
        f"Unit test failed or not found:\nstdout:{r.stdout}\nstderr:{r.stderr}"


def test_display_tests_pass():
    """All sui-display library tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "test", "-p", "sui-display", "--lib"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, f"Tests failed:\n{r.stderr}"
