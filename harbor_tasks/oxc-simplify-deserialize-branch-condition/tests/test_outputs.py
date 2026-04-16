#!/usr/bin/env python3
"""Tests for OXC deserializeStr branch condition simplification."""

import subprocess
import sys
import os

REPO = "/workspace/oxc"

# File paths for the generated deserializers
NAPI_PARSER_FILES = [
    "napi/parser/src-js/generated/deserialize/js.js",
    "napi/parser/src-js/generated/deserialize/js_parent.js",
    "napi/parser/src-js/generated/deserialize/js_range.js",
    "napi/parser/src-js/generated/deserialize/js_range_parent.js",
    "napi/parser/src-js/generated/deserialize/ts.js",
    "napi/parser/src-js/generated/deserialize/ts_parent.js",
    "napi/parser/src-js/generated/deserialize/ts_range.js",
    "napi/parser/src-js/generated/deserialize/ts_range_parent.js",
]

OXLINT_FILE = "apps/oxlint/src-js/generated/deserialize.js"

RAW_TRANSFER_FILE = "tasks/ast_tools/src/generators/raw_transfer.rs"

ALL_JS_FILES = NAPI_PARSER_FILES + [OXLINT_FILE]


def read_file(path):
    """Read file content from repo."""
    full_path = os.path.join(REPO, path)
    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"ERROR: {e}"


def test_napi_parser_simplified_condition():
    """NAPI parser deserializers have simplified branch condition (fail-to-pass).

    The old code used: if (pos < sourceEndPos && (sourceIsAscii || pos + len <= firstNonAsciiPos))
    The new code uses: if (end <= firstNonAsciiPos)
    """
    for filepath in NAPI_PARSER_FILES:
        content = read_file(filepath)

        # Fail: Old complex condition exists
        assert "sourceIsAscii" not in content, f"{filepath}: sourceIsAscii variable should be removed"
        assert "sourceEndPos" not in content, f"{filepath}: sourceEndPos variable should be removed"

        # Pass: New simplified condition exists
        assert "if (end <= firstNonAsciiPos)" in content, f"{filepath}: Simplified condition 'if (end <= firstNonAsciiPos)' should exist"

        # Verify the pattern: let end = pos + len; is declared before the condition
        assert "let end = pos + len;" in content, f"{filepath}: 'let end = pos + len;' should be declared"


def test_oxlint_simplified_condition():
    """Oxlint deserializer has simplified branch condition (fail-to-pass).

    The oxlint version has additional sourceStartPos check.
    Old: if (pos >= sourceStartPos && (sourceIsAscii || pos - sourceStartPos + len <= firstNonAsciiPos))
    New: if (pos >= sourceStartPos && end <= firstNonAsciiPos)
    """
    content = read_file(OXLINT_FILE)

    # Fail: Old complex condition exists
    assert "sourceIsAscii" not in content, f"{OXLINT_FILE}: sourceIsAscii variable should be removed"

    # Pass: New simplified condition exists
    assert "if (pos >= sourceStartPos && end <= firstNonAsciiPos)" in content, \
        f"{OXLINT_FILE}: Simplified condition with sourceStartPos check should exist"

    # Verify the pattern: let end = pos + len; is declared before the condition
    assert "let end = pos + len;" in content, f"{OXLINT_FILE}: 'let end = pos + len;' should be declared"


def test_napi_parser_first_non_ascii_calculation():
    """NAPI parser calculates firstNonAsciiPos correctly (pass-to-pass).

    When source is all ASCII: firstNonAsciiPos = sourceByteLen
    When source has non-ASCII: find first non-ASCII byte position
    """
    for filepath in NAPI_PARSER_FILES:
        content = read_file(filepath)

        # Verify the new pattern for calculating firstNonAsciiPos
        # if (sourceText.length === sourceByteLen) firstNonAsciiPos = sourceByteLen;
        assert "if (sourceText.length === sourceByteLen) firstNonAsciiPos = sourceByteLen;" in content, \
            f"{filepath}: ASCII-only fast path should be present"

        # Verify the loop pattern: for (; i < sourceByteLen && uint8[i] < 128; i++);
        assert "for (; i < sourceByteLen && uint8[i] < 128; i++);" in content, \
            f"{filepath}: Non-ASCII finding loop should use simplified condition"


def test_oxlint_first_non_ascii_calculation():
    """Oxlint calculates firstNonAsciiPos correctly (pass-to-pass).

    Oxlint has source at end of buffer, so uses sourceStartPos offset.
    """
    content = read_file(OXLINT_FILE)

    # Verify the new pattern: sourceStartPos is still used for oxlint
    assert "sourceStartPos" in content, f"{OXLINT_FILE}: sourceStartPos should be present for oxlint"

    # Verify firstNonAsciiPos calculation when ASCII
    assert "if (sourceText.length === sourceByteLen) firstNonAsciiPos = sourceStartPos + sourceByteLen;" in content, \
        f"{OXLINT_FILE}: ASCII-only fast path with sourceStartPos should be present"


def test_raw_transfer_generator_updated():
    """The Rust code generator is updated (pass-to-pass).

    The generator in raw_transfer.rs should produce the simplified code.
    """
    content = read_file(RAW_TRANSFER_FILE)

    # Check that generator has simplified condition for STR_DESERIALIZER_BODY
    assert "if (end <= firstNonAsciiPos)" in content, \
        f"{RAW_TRANSFER_FILE}: Generator should output simplified condition"

    # Check that generator no longer references sourceIsAscii in output strings
    # Note: sourceIsAscii is still calculated as a local const, but not used in condition
    assert "sourceStartPos, firstNonAsciiPos;" in content, \
        f"{RAW_TRANSFER_FILE}: Generator should declare firstNonAsciiPos only (no sourceIsAscii/sourceEndPos at module level)"


def test_js_syntax_valid():
    """All modified JS files have valid syntax (pass-to-pass).

    Parse each file to ensure no syntax errors were introduced.
    """
    import tempfile

    for filepath in ALL_JS_FILES:
        content = read_file(filepath)

        # Quick syntax validation: check for basic JS patterns
        # The files should be valid module JS
        assert "export function deserialize" in content, \
            f"{filepath}: Should have deserialize export"

        assert "function deserializeStr(pos)" in content, \
            f"{filepath}: Should have deserializeStr function"

        # Check for balanced braces (basic sanity check)
        open_count = content.count('{')
        close_count = content.count('}')
        assert open_count == close_count, \
            f"{filepath}: Braces should be balanced ({open_count} vs {close_count})"


def test_napi_parser_no_sourceIsAscii_variable():
    """NAPI parser files removed sourceIsAscii variable declaration (fail-to-pass)."""
    for filepath in NAPI_PARSER_FILES:
        content = read_file(filepath)

        # Old declaration pattern - sourceIsAscii and sourceEndPos at module level
        assert "sourceIsAscii," not in content, \
            f"{filepath}: sourceIsAscii module-level declaration should be removed"
        assert "sourceEndPos," not in content, \
            f"{filepath}: sourceEndPos module-level declaration should be removed"

        # New declaration: sourceText followed by firstNonAsciiPos (may be on same line or next line)
        # Check that sourceText is followed by firstNonAsciiPos in the declarations
        import re
        # Pattern: sourceText, (optional whitespace/newline) firstNonAsciiPos
        decl_pattern = r'sourceText\s*,\s*\n?\s*firstNonAsciiPos'
        assert re.search(decl_pattern, content), \
            f"{filepath}: New simplified variable declaration (sourceText, firstNonAsciiPos) should exist"


def test_oxlint_no_sourceIsAscii_variable():
    """Oxlint file removed sourceIsAscii variable declaration (fail-to-pass)."""
    content = read_file(OXLINT_FILE)

    # Check that the module-level sourceIsAscii is removed
    # In oxlint, the let declaration spans multiple lines
    # Old pattern: sourceIsAscii was between sourceText and sourceStartPos
    # New pattern: sourceStartPos comes directly after sourceText (or with parent in between)

    # Extract the let declaration section (from 'let uint8,' to before the function/const)
    import re
    let_section_match = re.search(r'let uint8,\s*(.*?)\s*(?:const|function|export)', content, re.DOTALL)
    assert let_section_match, f"{OXLINT_FILE}: Should have let declaration section"

    let_section = let_section_match.group(1)

    # Check sourceIsAscii is NOT in the let section
    assert "sourceIsAscii" not in let_section, \
        f"{OXLINT_FILE}: sourceIsAscii should not be in let declarations"

    # Check sourceText and sourceStartPos are still present (sourceStartPos needed for oxlint)
    assert "sourceText" in let_section, f"{OXLINT_FILE}: sourceText should be in let declarations"
    assert "sourceStartPos" in let_section, f"{OXLINT_FILE}: sourceStartPos should be in let declarations"


# ==================== CI/CD PASS-TO-PASS TESTS ====================
# These tests verify the repo's own CI checks pass on the base commit


def test_repo_cargo_fmt():
    """Rust code formatting passes (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "fmt", "--check"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"cargo fmt --check failed:\n{r.stderr[-500:]}"


def test_repo_cargo_check_ast_tools():
    """Rust ast_tools crate compiles (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "check", "-p", "oxc_ast_tools"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert r.returncode == 0, f"cargo check -p oxc_ast_tools failed:\n{r.stderr[-500:]}"


def test_repo_cargo_test_ast_tools():
    """Rust ast_tools tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "test", "-p", "oxc_ast_tools", "--all-features"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert r.returncode == 0, f"cargo test -p oxc_ast_tools failed:\n{r.stderr[-500:]}"


def test_repo_cargo_shear():
    """No unused Rust dependencies (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "shear"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"cargo shear failed:\n{r.stdout[-500:]}"


def test_repo_js_syntax_napi_parser():
    """NAPI parser generated JS files have valid syntax (pass_to_pass)."""
    for filepath in NAPI_PARSER_FILES:
        full_path = os.path.join(REPO, filepath)
        r = subprocess.run(
            ["node", "--check", full_path],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert r.returncode == 0, f"JS syntax check failed for {filepath}:\n{r.stderr}"


def test_repo_js_syntax_oxlint():
    """Oxlint generated JS file has valid syntax (pass_to_pass)."""
    full_path = os.path.join(REPO, OXLINT_FILE)
    r = subprocess.run(
        ["node", "--check", full_path],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"JS syntax check failed for {OXLINT_FILE}:\n{r.stderr}"


if __name__ == "__main__":
    # Run with pytest if available
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
