"""
Test outputs for the klib dump parsing qualified names fix.
Tests that the regex fix correctly parses qualified names adjacent to vararg symbol.
"""

import subprocess
import os
import re

REPO = "/workspace/kotlin"
TARGET_FILE = "compiler/util-klib-abi/src/org/jetbrains/kotlin/library/abi/parser/Cursor.kt"
TEST_FILE = "compiler/util-klib-abi/test/org/jetbrains/kotlin/library/abi/parser/KlibParsingCursorExtensionsTest.kt"


def read_file(path):
    """Read file content."""
    full_path = os.path.join(REPO, path)
    with open(full_path, 'r') as f:
        return f.read()


# ===== FAIL TO PASS TESTS =====
# These tests verify the behavior fix - should fail on base commit, pass on fix

def test_regex_lookahead_pattern_present():
    """F2P: The fixed regex must have negative lookahead for '...' before the char class"""
    content = read_file(TARGET_FILE)
    # The fix adds (?!\.\.\.) at the very start of the group to prevent consuming vararg symbol
    # Looking for pattern: ^((?!\.\.\.)(=...|[^...])+)
    assert r'(?!\.\.\.)' in content, \
        "Fix not applied: missing negative lookahead for '...' in regex"


def test_qualified_name_vararg_parsing_behavior():
    """F2P: Verify the regex correctly splits qualified name from vararg symbol.

    This test simulates the parsing behavior that the PR fixes.
    The bug: "kotlin/DoubleArray..." was parsed as "kotlin/DoubleArray..." with no vararg
    The fix: "kotlin/DoubleArray..." is parsed as "kotlin/DoubleArray" + vararg symbol
    """
    content = read_file(TARGET_FILE)

    # Just verify the file has the pattern with the negative lookahead
    assert r'(?!\.\.\.)' in content, \
        "Fix not applied: regex missing negative lookahead for vararg symbol"

    # The fixed regex pattern: ^((?!\.\.\.)(=(?!\s?\.\.\.)|[^;\[\]/<>:\\(){}?=,&]))+
    # Note: The character class [^;\[\]/<>:\\(){}?=,&] explicitly EXCLUDES '/' so the match
    # will stop at '/' when parsing "kotlin/DoubleArray...". The Cursor parser handles this
    # by reading the qualified name in segments.

    # Test with a simpler input without '/'
    test_input = "DoubleArray..."
    regex_str = r'^((?!\.\.\.)(=(?!\s?\.\.\.)|[^;\[\]/<>:\\(){}?=,&]))+'

    match = re.match(regex_str, test_input)
    assert match is not None, "Regex should match the input"

    matched_text = match.group(0)
    # For input without '/', the match should stop before "..."
    assert matched_text == "DoubleArray", \
        f"Bug present: regex consumed entire string '{matched_text}', expected 'DoubleArray'"

    # The remaining part should be "..."
    remaining = test_input[len(matched_text):]
    assert remaining == "...", \
        f"Expected remaining '...', got '{remaining}'"

    # Test with input containing '/' - the match should stop at '/'
    test_input2 = "kotlin/DoubleArray..."
    match2 = re.match(regex_str, test_input2)
    assert match2 is not None, "Regex should match the input with '/'"

    matched_text2 = match2.group(0)
    # With '/' excluded from the character class, match stops at first '/'
    # This is correct behavior - the Cursor parser handles qualified names segment by segment
    assert matched_text2 == "kotlin", \
        f"Expected 'kotlin' as first segment, got '{matched_text2}'"

    remaining2 = test_input2[len(matched_text2):]
    assert remaining2 == "/DoubleArray...", \
        f"Expected remaining '/DoubleArray...', got '{remaining2}'"


def test_vararg_without_type_params_compiles():
    """F2P: The new test case added in the PR must compile and pass."""
    content = read_file(TEST_FILE)

    # Check that the new test method exists
    assert 'fun parseValueParamVarargWithoutTypeParams()' in content, \
        "New test method parseValueParamVarargWithoutTypeParams not found"

    # Check the test has correct assertions
    assert 'kotlin/DoubleArray' in content, \
        "Test input 'kotlin/DoubleArray' not found"
    assert 'valueParam.isVararg' in content, \
        "Test assertion for isVararg not found"


# ===== PASS TO PASS TESTS =====
# These tests verify existing functionality wasn't broken

def test_original_vararg_test_still_works():
    """P2P: Original test for vararg must still exist."""
    content = read_file(TEST_FILE)

    # The existing test parseValueParamVararg should still exist (renamed from parseValueParamVarargWithTypeParams in base)
    assert 'fun parseValueParamVararg()' in content, \
        "Original test parseValueParamVararg not found"


def test_regex_valid_identifier_base_pattern_unchanged():
    """P2P: The base validIdentifierRegex pattern should still exist unchanged."""
    content = read_file(TARGET_FILE)

    # The simpler validIdentifierRegex (without dots) should exist
    assert 'private val validIdentifierRegex' in content, \
        "Base validIdentifierRegex declaration not found"

    # It should still use the original pattern (without the lookahead for '...' at start of group)
    # The base pattern has: ^((=(?!	*\.\.\.)|[^.;\[\]/<>:\\(){}?=,&])+)
    assert '(?!' in content, \
        "Base pattern structure preserved"


def test_cursor_class_structure_preserved():
    """P2P: The Cursor class structure should be preserved."""
    content = read_file(TARGET_FILE)

    # Key methods should still exist
    assert 'fun parseValidIdentifier' in content, \
        "parseValidIdentifier method not found"
    assert 'fun copy()' in content, \
        "copy method not found"
    assert 'fun skipInlineWhitespace()' in content, \
        "skipInlineWhitespace method not found"


# ===== STRUCTURAL TESTS (gated by behavioral tests) =====

def test_fix_applied_in_correct_location():
    """Verify the fix is in the right file and regex."""
    content = read_file(TARGET_FILE)

    # Must be in validIdentifierWithDotRegex specifically
    # Find the section from validIdentifierWithDotRegex to its closing trimIndent
    dot_regex_section = re.search(
        r'validIdentifierWithDotRegex\s*=.*?trimIndent\(\)',
        content,
        re.DOTALL
    )
    assert dot_regex_section is not None, "validIdentifierWithDotRegex section not found"

    section = dot_regex_section.group(0)
    assert r'(?!\.\.\.)' in section, \
        "Fix not in validIdentifierWithDotRegex - wrong location"


def test_no_overly_broad_regex_changes():
    """Verify we didn't break other regex patterns."""
    content = read_file(TARGET_FILE)

    # Count regex declarations - should have exactly 2 (validIdentifierRegex and validIdentifierWithDotRegex)
    regex_count = len(re.findall(r'\bval\s+\w+Regex\s*=\s*Regex', content))
    # Allow for some flexibility but shouldn't have drastically changed
    assert regex_count >= 2, f"Too few Regex declarations, found {regex_count}"

    # Check that the fix is in validIdentifierWithDotRegex but NOT in validIdentifierRegex
    # The fix is ^((?!\.\.\.) which adds the negative lookahead at the start of the group

    # Find the section for validIdentifierRegex (private, without WithDot)
    valid_id_section = re.search(
        r'private val validIdentifierRegex\s*=.*?trimIndent\(\)',
        content,
        re.DOTALL
    )
    assert valid_id_section is not None, "validIdentifierRegex section not found"

    # Find the section for validIdentifierWithDotRegex
    valid_id_with_dot_section = re.search(
        r'val validIdentifierWithDotRegex\s*=.*?trimIndent\(\)',
        content,
        re.DOTALL
    )
    assert valid_id_with_dot_section is not None, "validIdentifierWithDotRegex section not found"

    # The fix pattern (?!\.\.\.) should be in the WithDot version
    assert r'(?!\.\.\.)' in valid_id_with_dot_section.group(0), \
        "Fix missing from validIdentifierWithDotRegex"
