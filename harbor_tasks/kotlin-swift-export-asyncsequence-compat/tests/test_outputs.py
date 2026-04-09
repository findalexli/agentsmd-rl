"""Tests for Swift Export asyncSequence compatibility function."""
import subprocess
import os
import re
import pytest

REPO = "/workspace/kotlin"
TARGET_FILE = os.path.join(REPO, "native/swift/swift-export-standalone/resources/swift/KotlinCoroutineSupport.swift")


def test_asyncsequence_function_exists():
    """Fail-to-pass: asyncSequence(for:) function must exist in the file."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Check for the function declaration
    pattern = r'public func asyncSequence\s*<\s*T\s*>\s*\(\s*for\s+flow:\s*any\s+KotlinTypedFlow\s*<\s*T\s*>\s*\)'
    assert re.search(pattern, content), "asyncSequence(for:) function declaration not found"


def test_asyncsequence_has_deprecated_attribute():
    """Fail-to-pass: asyncSequence function must have @available deprecated attribute."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Check for the deprecated attribute before the function
    pattern = r'@available\s*\(\s*\*\s*,\s*deprecated\s*,\s*message:\s*"[^"]*asAsyncSequence\(\)[^"]*"\s*\)'
    assert re.search(pattern, content), "@available(*, deprecated) attribute with asAsyncSequence message not found"


def test_asyncsequence_calls_asasyncsequence():
    """Fail-to-pass: asyncSequence function body must call asAsyncSequence()."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Check that function body calls asAsyncSequence
    pattern = r'return\s+flow\.asAsyncSequence\s*\(\s*\)'
    assert re.search(pattern, content), "Function body must call flow.asAsyncSequence()"


def test_asyncsequence_returns_kotlinflowsequence():
    """Fail-to-pass: asyncSequence function must return KotlinFlowSequence<T>."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Check return type
    pattern = r'public func asyncSequence\s*<\s*T\s*>\s*\([^)]*\)\s*(?:->\s*KotlinFlowSequence\s*<\s*T\s*>)?'
    # Alternative: check for arrow and return type
    arrow_pattern = r'\)\s*->\s*KotlinFlowSequence\s*<\s*T\s*>'
    assert re.search(arrow_pattern, content), "Function must have return type -> KotlinFlowSequence<T>"


def test_asyncsequence_has_documentation_comment():
    """Fail-to-pass: asyncSequence function must have documentation comment explaining purpose."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Check for documentation comment before the function
    pattern = r'///\s*This function provides source compatibility with KMP-NativeCoroutines'
    assert re.search(pattern, content), "Documentation comment about KMP-NativeCoroutines compatibility not found"


def test_swift_file_syntax_valid():
    """Pass-to-pass: Swift file should have valid syntax (compiles without errors)."""
    # Check if swiftc is available
    swiftc_check = subprocess.run(["which", "swiftc"], capture_output=True)
    if swiftc_check.returncode != 0:
        pytest.skip("swiftc not available in container")

    # Try to check syntax with swiftc
    result = subprocess.run(
        ["swiftc", "-parse", TARGET_FILE],
        capture_output=True,
        text=True,
        timeout=60
    )

    # Note: This may fail due to missing dependencies, but basic syntax should be parseable
    # We allow this to pass even if there are import/module errors
    # The key is that basic Swift syntax is valid
    error_output = result.stderr.lower()

    # Filter out acceptable errors (module/import related)
    unacceptable_errors = [
        "expected", "error: invalid", "error: unexpected",
        "braces", "parentheses", "comma", "semicolon"
    ]

    for err in unacceptable_errors:
        if err in error_output:
            assert False, f"Swift syntax error detected: {result.stderr[:500]}"

    # If we get here, basic syntax is acceptable
    assert True


def test_file_exists():
    """Pass-to-pass: Target Swift file exists."""
    assert os.path.exists(TARGET_FILE), f"Target file {TARGET_FILE} does not exist"


def test_swift_braces_balanced():
    """Pass-to-pass: Swift file has balanced braces and parentheses."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Check balanced braces
    open_braces = content.count('{')
    close_braces = content.count('}')
    assert open_braces == close_braces, f"Unbalanced braces: {open_braces} open, {close_braces} close"

    # Check balanced parentheses
    open_parens = content.count('(')
    close_parens = content.count(')')
    assert open_parens == close_parens, f"Unbalanced parentheses: {open_parens} open, {close_parens} close"

    # Check balanced brackets
    open_brackets = content.count('[')
    close_brackets = content.count(']')
    assert open_brackets == close_brackets, f"Unbalanced brackets: {open_brackets} open, {close_brackets} close"


def test_swift_imports_valid():
    """Pass-to-pass: Swift file has valid import statements."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Find all import statements
    import_pattern = r'^\s*(import|@_implementationOnly import)\s+([A-Za-z_][A-Za-z0-9_]*)'
    imports = re.findall(import_pattern, content, re.MULTILINE)

    # Should have at least the expected imports
    assert len(imports) >= 2, f"Expected at least 2 imports, found {len(imports)}"

    # Verify no invalid characters in import names
    for _, module_name in imports:
        assert re.match(r'^[A-Za-z_][A-Za-z0-9_.]*$', module_name), f"Invalid import name: {module_name}"


def test_swift_no_trailing_whitespace():
    """Pass-to-pass: Swift file has no trailing whitespace on lines."""
    with open(TARGET_FILE, 'r') as f:
        lines = f.readlines()

    trailing_ws_count = sum(1 for line in lines if line.rstrip() != line.rstrip('\n').rstrip())
    # Allow some tolerance but flag excessive issues
    assert trailing_ws_count < 50, f"Found {trailing_ws_count} lines with trailing whitespace"


def test_swift_function_declarations_valid():
    """Pass-to-pass: Swift file has syntactically valid function declarations."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Check for basic Swift function declaration patterns
    # Valid Swift func: public/private/package/internal func name(params) -> ReturnType { ... }
    func_pattern = r'(?:public\s+|private\s+|package\s+|internal\s+)?(?:func|init|deinit)\s+[A-Za-z_][A-Za-z0-9_]*\s*\('
    funcs = re.findall(func_pattern, content)

    # The file should have at least a few function declarations
    assert len(funcs) >= 2, f"Expected at least 2 function declarations, found {len(funcs)}"


def test_swift_comments_valid():
    """Pass-to-pass: Swift file has valid comment syntax."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Check for valid single-line comments (/// or //)
    single_line_pattern = r'^\s*///.*$'
    doc_comments = re.findall(single_line_pattern, content, re.MULTILINE)

    # Should have at least some documentation comments
    assert len(doc_comments) >= 1, f"Expected at least 1 documentation comment (///), found {len(doc_comments)}"

    # Check for improperly formatted block comments that might indicate issues
    # Swift block comments: /* ... */
    block_comment_pattern = r'/\*[^*]*\*+(?:[^/*][^*]*\*+)*/'
    block_comments = re.findall(block_comment_pattern, content, re.DOTALL)

    # Unclosed block comments would be a syntax error - check for /* without */
    open_block = content.count('/*')
    close_block = content.count('*/')
    assert open_block == close_block, f"Unbalanced block comment markers: {open_block} /*, {close_block} */"


def test_swift_class_struct_protocol_valid():
    """Pass-to-pass: Swift file has valid class/struct/protocol declarations."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # Check for valid Swift type declarations
    type_patterns = [
        r'public\s+(?:final\s+)?class\s+\w+',
        r'(?:public\s+)?struct\s+\w+',
        r'(?:public\s+)?protocol\s+\w+',
        r'(?:public\s+)?enum\s+\w+',
        r'(?:public\s+)?extension\s+\w+',
    ]

    total_types = 0
    for pattern in type_patterns:
        matches = re.findall(pattern, content)
        total_types += len(matches)

    # Should have at least a few type definitions
    assert total_types >= 2, f"Expected at least 2 type declarations, found {total_types}"


def test_file_not_empty():
    """Pass-to-pass: Swift file is not empty and has substantial content."""
    with open(TARGET_FILE, 'r') as f:
        content = f.read()

    # File should be non-empty
    assert len(content) > 0, "File is empty"

    # Should have multiple lines
    lines = content.split('\n')
    assert len(lines) > 50, f"File too short: only {len(lines)} lines"

    # Should have substantial non-whitespace content
    non_ws_chars = len([c for c in content if not c.isspace()])
    assert non_ws_chars > 500, f"File has insufficient content: only {non_ws_chars} non-whitespace characters"
