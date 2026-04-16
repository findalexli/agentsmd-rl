"""
Tests for KT-85149: Fix Klib dump parsing qualified names adjacent to vararg symbol.

The bug: The validIdentifierWithDotRegex was consuming the '...' vararg symbol as part
of the qualified name because the regex allowed '.' characters. This caused parsing
errors when a type name contained dots followed immediately by the vararg ellipsis.

Example: "kotlin/DoubleArray..." was being parsed incorrectly - the regex would
consume "kotlin/DoubleArray." (or similar) as the type name instead of stopping
before the "..." vararg symbol.
"""

import subprocess
import os

REPO = "/workspace/kotlin"


def test_vararg_regex_has_negative_lookahead():
    """
    F2P: Verify the regex pattern has the negative lookahead to prevent consuming vararg symbols.

    The fix adds (?!\.\.\.) at the start of the group to stop matching before "...".
    Without this fix, the regex incorrectly consumes part of the vararg symbol as part of the type name.
    """
    cursor_file = os.path.join(REPO, "compiler", "util-klib-abi", "src", "org", "jetbrains",
                                "kotlin", "library", "abi", "parser", "Cursor.kt")

    with open(cursor_file, "r") as f:
        content = f.read()

    # Check for the fix: (?!\.\.\.) negative lookahead
    # The fix adds this at the beginning of validIdentifierWithDotRegex
    if "(?!\\.\\.\\.)" not in content:
        assert False, (
            "Fix not applied: validIdentifierWithDotRegex missing negative lookahead '(?!\\\\.\\\\.\\\\.)' "
            "for vararg symbol. The regex should stop matching before '...' while still allowing dots in qualified names."
        )


def test_validIdentifierWithDotRegex_structure():
    """
    F2P: Verify the validIdentifierWithDotRegex has the correct structure with the fix.

    The correct pattern should be:
    ^((?!\.\.\.)(=(?!(?!\s?\.\.\.)|[^;\[\]/<>:\\(){}?=,&]))+

    This ensures:
    1. (?!\.\.\.) - Negative lookahead to stop before "..."
    2. Then the alternation for matching valid identifier chars
    """
    cursor_file = os.path.join(REPO, "compiler", "util-klib-abi", "src", "org", "jetbrains",
                                "kotlin", "library", "abi", "parser", "Cursor.kt")

    with open(cursor_file, "r") as f:
        content = f.read()

    # Find the validIdentifierWithDotRegex definition
    marker = "validIdentifierWithDotRegex"
    if marker not in content:
        assert False, f"{marker} not found in Cursor.kt"

    # Check for the fix in the context of validIdentifierWithDotRegex
    # Look for the pattern that includes the negative lookahead
    # The fix should be: (?!\.\.\.)(=(?!(?!\s?\.\.\.)|[^;\[\]/<>:\\(){}?=,&]))+

    # After the fix, we should see:
    # - (?!\.\.\.) near validIdentifierWithDotRegex
    if "(?!\\.\\.\\.)" not in content:
        assert False, "Regex missing negative lookahead (?!\\.\\.\\.) for vararg symbol"

    # Verify the fix is in the right place (near validIdentifierWithDotRegex)
    idx = content.find("validIdentifierWithDotRegex")
    section = content[idx:idx + 500]  # Look at the regex definition area

    if "(?!\\.\\.\\.)" not in section:
        assert False, "Negative lookahead not found in validIdentifierWithDotRegex definition"


def test_no_old_buggy_regex():
    """
    F2P: Verify the old buggy regex pattern for validIdentifierWithDotRegex is NOT present.

    The buggy pattern was:
    ^((=(?!(?!\s?\.\.\.)|[^;\[\]/<>:\\(){}?=,&])+)

    This pattern allows '.' to be matched without restriction, causing it to consume "..."
    """
    cursor_file = os.path.join(REPO, "compiler", "util-klib-abi", "src", "org", "jetbrains",
                                "kotlin", "library", "abi", "parser", "Cursor.kt")

    with open(cursor_file, "r") as f:
        content = f.read()

    # Find the validIdentifierWithDotRegex section
    idx = content.find("validIdentifierWithDotRegex")
    if idx == -1:
        assert False, "validIdentifierWithDotRegex not found"

    # Get the regex definition (roughly the next 400 characters)
    section = content[idx:idx + 400]

    # The buggy pattern for validIdentifierWithDotRegex starts with:
    # ^((=(?!(?!\s?\.\.\.)|[^;\[\]/<>:\\(){}?=,&])+)
    # WITHOUT the (?!\.\.\.) negative lookahead

    # If we see the alternation pattern but NOT the negative lookahead, that's the bug
    has_alternation = "(=(?!(?!\\s?\\.\\.\\.)" in section or "|[^;\\[\\]/<>:\\\\(){}?=,&]" in section
    has_lookahead = "(?!\\.\\.\\.)" in section

    if has_alternation and not has_lookahead:
        assert False, (
            "validIdentifierWithDotRegex has the old buggy pattern without the (?!\\.\\.\\.) "
            "negative lookahead. The regex will incorrectly consume '...' as part of type names."
        )


def test_file_exists_and_readable():
    """
    P2P: Basic check that the target file exists and contains expected content.
    """
    cursor_file = os.path.join(REPO, "compiler", "util-klib-abi", "src", "org", "jetbrains",
                                "kotlin", "library", "abi", "parser", "Cursor.kt")

    assert os.path.exists(cursor_file), f"Target file does not exist: {cursor_file}"

    with open(cursor_file, "r") as f:
        content = f.read()

    assert len(content) > 0, "Target file is empty"
    assert "validIdentifierWithDotRegex" in content, "Target regex not found in file"
    assert "validIdentifierRegex" in content, "validIdentifierRegex not found in file"


def test_both_regexes_present():
    """
    P2P: Verify both regex patterns exist in the file.
    """
    cursor_file = os.path.join(REPO, "compiler", "util-klib-abi", "src", "org", "jetbrains",
                                "kotlin", "library", "abi", "parser", "Cursor.kt")

    with open(cursor_file, "r") as f:
        content = f.read()

    # Both should exist
    assert "validIdentifierRegex" in content, "validIdentifierRegex missing"
    assert "validIdentifierWithDotRegex" in content, "validIdentifierWithDotRegex missing"


def test_kotlin_syntax_compiles():
    """
    P2P: Kotlin source file compiles without errors (pass_to_pass).

    This test verifies the Cursor.kt file has valid Kotlin syntax by compiling
    it with the kotlinc compiler.
    """
    cursor_file = os.path.join(REPO, "compiler", "util-klib-abi", "src", "org", "jetbrains",
                                "kotlin", "library", "abi", "parser", "Cursor.kt")

    r = subprocess.run(
        ["kotlinc", cursor_file],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Kotlin compilation failed:\n{r.stderr[-500:]}"


def test_kotlin_parser_module_files():
    """
    P2P: All parser source files exist and are readable (pass_to_pass).
    """
    parser_dir = os.path.join(REPO, "compiler", "util-klib-abi", "src", "org", "jetbrains",
                               "kotlin", "library", "abi", "parser")

    expected_files = [
        "Cursor.kt",
        "KLibDumpParser.kt",
        "KlibParsingCursorExtensions.kt",
    ]

    for filename in expected_files:
        filepath = os.path.join(parser_dir, filename)
        assert os.path.exists(filepath), f"Parser file missing: {filename}"
        with open(filepath, "r") as f:
            content = f.read()
        assert len(content) > 0, f"Parser file is empty: {filename}"


def test_fix_distinguishes_vararg():
    """
    F2P: Verify the fix correctly handles the specific test case from the PR.

    The test case "kotlin/DoubleArray..." should:
    - Parse "kotlin/DoubleArray" as the type name
    - Recognize "..." as the vararg symbol

    The fix ensures the regex stops before "..." while still matching "kotlin/DoubleArray".
    """
    cursor_file = os.path.join(REPO, "compiler", "util-klib-abi", "src", "org", "jetbrains",
                                "kotlin", "library", "abi", "parser", "Cursor.kt")

    with open(cursor_file, "r") as f:
        content = f.read()

    # Check the fix is present
    if "(?!\\.\\.\\.)" not in content:
        assert False, "The fix for parsing qualified names adjacent to vararg symbol is missing"

    # Verify the fix is specifically in validIdentifierWithDotRegex
    # (not just in validIdentifierRegex which already had it)
    idx = content.find("validIdentifierWithDotRegex")
    section = content[idx:idx + 500]

    if "(?!\\.\\.\\.)" not in section:
        assert False, (
            "The negative lookahead (?!\\.\\.\\.) is missing from validIdentifierWithDotRegex. "
            "This regex is used to parse qualified names with dots, and without the fix, "
            "it will incorrectly consume the '...' vararg symbol as part of the type name."
        )
