#!/usr/bin/env python3
"""
Test suite for verifying the utf8Slice optimization fix.

This tests that TextDecoder has been replaced with Buffer.prototype.utf8Slice
for UTF-8 string decoding in the oxc codebase.
"""

import subprocess
import os
import re
import pytest

REPO = "/workspace/oxc"

# Files that should contain utf8Slice after the fix
GENERATED_JS_FILES = [
    "napi/parser/src-js/generated/deserialize/js.js",
    "napi/parser/src-js/generated/deserialize/js_parent.js",
    "napi/parser/src-js/generated/deserialize/js_range.js",
    "napi/parser/src-js/generated/deserialize/js_range_parent.js",
    "napi/parser/src-js/generated/deserialize/ts.js",
    "napi/parser/src-js/generated/deserialize/ts_parent.js",
    "napi/parser/src-js/generated/deserialize/ts_range.js",
    "napi/parser/src-js/generated/deserialize/ts_range_parent.js",
    "apps/oxlint/src-js/generated/deserialize.js",
]

# The Rust code generator that produces these files
RUST_GENERATOR = "tasks/ast_tools/src/generators/raw_transfer.rs"

# Source file that also uses utf8Slice
SOURCE_CODE_TS = "apps/oxlint/src-js/plugins/source_code.ts"


def read_file(filepath):
    """Read file content, return None if file doesn't exist."""
    full_path = os.path.join(REPO, filepath)
    try:
        with open(full_path, 'r') as f:
            return f.read()
    except FileNotFoundError:
        return None
    except Exception as e:
        return None


# =============================================================================
# Fail-to-pass tests: These should FAIL on base commit and PASS after fix
# =============================================================================

def test_rust_generator_uses_utf8slice():
    """
    Rust code generator should use utf8Slice instead of decodeStr/TextDecoder.

    This is the source of truth - the Rust generator produces the JS files.
    """
    content = read_file(RUST_GENERATOR)
    assert content is not None, f"Rust generator file not found: {RUST_GENERATOR}"

    # Should have utf8Slice in the destructuring pattern
    assert "utf8Slice, latin1Slice" in content, \
        "Rust generator should destructure utf8Slice from Buffer.prototype"

    # Should use utf8Slice.call instead of decodeStr
    assert "utf8Slice.call(uint8, pos, end)" in content, \
        "Rust generator should use utf8Slice.call(uint8, pos, end) instead of decodeStr"

    # Should NOT have the old TextDecoder pattern in the string deserializer body
    str_body_match = re.search(r'static STR_DESERIALIZER_BODY.*?;', content, re.DOTALL)
    if str_body_match:
        str_body = str_body_match.group(0)
        assert "decodeStr" not in str_body, \
            "STR_DESERIALIZER_BODY should not use decodeStr (TextDecoder)"
        assert "textDecoder" not in str_body.lower(), \
            "STR_DESERIALIZER_BODY should not reference textDecoder"


def test_rust_generator_comments_updated():
    """
    Comments in Rust generator should reference utf8Slice not TextDecoder.
    """
    content = read_file(RUST_GENERATOR)
    assert content is not None, f"Rust generator file not found: {RUST_GENERATOR}"

    # Look for the string deserializer body section
    str_body_match = re.search(r'static STR_DESERIALIZER_BODY:.*?=.*?"(.*?)";',
                               content, re.DOTALL | re.MULTILINE)
    if str_body_match:
        str_body = str_body_match.group(1)
        # Should reference utf8Slice in comments, not TextDecoder
        assert "Use `utf8Slice`" in str_body or "utf8Slice" in str_body, \
            "Comments should reference utf8Slice for long strings"


def test_generated_js_use_utf8slice():
    """
    All generated JS files should use utf8Slice instead of TextDecoder.
    """
    for filepath in GENERATED_JS_FILES:
        content = read_file(filepath)
        if content is None:
            continue  # Skip files that don't exist (some variants might not be present)

        # Should have utf8Slice in the Buffer.prototype destructuring
        assert "{ utf8Slice, latin1Slice } = Buffer.prototype" in content, \
            f"{filepath}: Should destructure utf8Slice from Buffer.prototype"

        # Should use utf8Slice.call for decoding
        assert "utf8Slice.call(uint8, pos, end)" in content, \
            f"{filepath}: Should use utf8Slice.call(uint8, pos, end) for UTF-8 decoding"


def test_no_textdecoder_in_generated_js():
    """
    Generated JS files should NOT use TextDecoder or decodeStr.
    """
    for filepath in GENERATED_JS_FILES:
        content = read_file(filepath)
        if content is None:
            continue

        # Should NOT have TextDecoder instantiation
        assert "new TextDecoder" not in content, \
            f"{filepath}: Should not use new TextDecoder() - use utf8Slice instead"

        # Should NOT have decodeStr function
        assert "decodeStr(" not in content, \
            f"{filepath}: Should not use decodeStr() - use utf8Slice.call() instead"

        # Should NOT have textDecoder variable
        assert "textDecoder" not in content, \
            f"{filepath}: Should not reference textDecoder variable"


def test_source_code_ts_uses_utf8slice():
    """
    apps/oxlint/src-js/plugins/source_code.ts should use utf8Slice.
    """
    content = read_file(SOURCE_CODE_TS)
    assert content is not None, f"source_code.ts not found"

    # Should destructure utf8Slice from Buffer.prototype
    assert "{ utf8Slice } = Buffer.prototype" in content, \
        "source_code.ts should destructure utf8Slice from Buffer.prototype"

    # Should use utf8Slice.call for decoding source text
    assert "utf8Slice.call(buffer, sourceStartPos, sourceStartPos + sourceByteLen)" in content, \
        "source_code.ts should use utf8Slice.call for decoding source text"

    # Should NOT have TextDecoder
    assert "new TextDecoder" not in content, \
        "source_code.ts should not use TextDecoder"
    assert "textDecoder" not in content.lower(), \
        "source_code.ts should not reference textDecoder"


def test_comments_reference_utf8slice():
    """
    Comments in generated files should reference utf8Slice not TextDecoder.
    """
    for filepath in GENERATED_JS_FILES:
        content = read_file(filepath)
        if content is None:
            continue

        # Look for the deserializeStr function
        if "function deserializeStr" in content:
            # Check that comments reference utf8Slice
            assert "Use `utf8Slice`" in content or "utf8Slice" in content, \
                f"{filepath}: Comments should reference utf8Slice"

            # Should NOT have old comment about TextDecoder
            if "Use `TextDecoder`" in content:
                # This is a failure - old comment still present
                assert False, f"{filepath}: Should not reference TextDecoder in comments"


# =============================================================================
# Pass-to-pass tests: Repo CI/CD commands (should pass on both base and fix)
# =============================================================================

def test_rust_ast_tools_compiles():
    """
    Rust oxc_ast_tools compiles with cargo check (pass_to_pass).

    This is the package that contains the raw_transfer.rs generator.
    """
    result = subprocess.run(
        ["cargo", "check", "-p", "oxc_ast_tools"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )
    assert result.returncode == 0, \
        f"cargo check failed:\n{result.stderr[-1000:]}"


def test_rust_ast_tools_tests_pass():
    """
    Rust oxc_ast_tools unit tests pass (pass_to_pass).
    """
    result = subprocess.run(
        ["cargo", "test", "-p", "oxc_ast_tools"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )
    assert result.returncode == 0, \
        f"cargo test failed:\n{result.stderr[-1000:]}"


def test_rust_parser_compiles():
    """
    Rust oxc_parser compiles with cargo check (pass_to_pass).

    The parser uses the raw transfer deserialization code.
    """
    result = subprocess.run(
        ["cargo", "check", "-p", "oxc_parser"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )
    assert result.returncode == 0, \
        f"cargo check failed:\n{result.stderr[-1000:]}"


def test_rust_parser_tests_pass():
    """
    Rust oxc_parser tests pass (pass_to_pass).
    """
    result = subprocess.run(
        ["cargo", "test", "-p", "oxc_parser"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )
    assert result.returncode == 0, \
        f"cargo test failed:\n{result.stderr[-1000:]}"


def test_rust_ast_tests_pass():
    """
    Rust oxc_ast tests pass (pass_to_pass).
    """
    result = subprocess.run(
        ["cargo", "test", "-p", "oxc_ast"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )
    assert result.returncode == 0, \
        f"cargo test failed:\n{result.stderr[-1000:]}"


def test_rust_fmt_check():
    """
    Rust code formatting passes cargo fmt --check (pass_to_pass).
    """
    result = subprocess.run(
        ["cargo", "fmt", "--", "--check"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, \
        f"cargo fmt check failed:\n{result.stderr[-500:]}"


# =============================================================================
# Integration test: Verify functional behavior if possible
# =============================================================================

def test_utf8slice_functionally_correct():
    """
    Verify that utf8Slice is available in Node.js Buffer.prototype.
    This ensures the fix uses valid Node.js APIs.
    """
    # Skip if Node.js is not available (not installed in this environment)
    try:
        subprocess.run(["node", "--version"], capture_output=True, timeout=5)
    except FileNotFoundError:
        pytest.skip("Node.js not available in this environment")
        return

    # Test that utf8Slice exists and works in Node.js
    test_code = '''
const buf = Buffer.from([0x68, 0x65, 0x6c, 0x6c, 0x6f]); // "hello"
const { utf8Slice } = Buffer.prototype;
const result = utf8Slice.call(buf, 0, 5);
if (result !== "hello") {
    console.error("utf8Slice failed: expected 'hello', got:", result);
    process.exit(1);
}

// Test with UTF-8 multibyte characters
const buf2 = Buffer.from([0xc3, 0xa9]); // "é"
const result2 = utf8Slice.call(buf2, 0, 2);
if (result2 !== "é") {
    console.error("utf8Slice failed for UTF-8: expected 'é', got:", result2);
    process.exit(1);
}
console.log("utf8Slice works correctly");
'''
    result = subprocess.run(
        ["node", "-e", test_code],
        capture_output=True,
        text=True,
        timeout=10
    )
    assert result.returncode == 0, \
        f"utf8Slice functional test failed:\n{result.stderr}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
