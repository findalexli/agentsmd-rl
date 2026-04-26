#!/usr/bin/env python3
"""
Tests for ClickHouse leftPad/rightPad heap-buffer-overflow fix.

Verifies:
1. The pad string buffer uses a container with read padding (not plain String)
2. The reinterpret_cast workaround for String::data() is removed from appendTo
3. Empty pad string fallback is placed before buffer construction
4. The C++ code has valid syntax
"""

import subprocess
import re

REPO = "/workspace/ClickHouse"
TARGET_FILE = f"{REPO}/src/Functions/padString.cpp"


def _read_target():
    with open(TARGET_FILE, 'r') as f:
        return f.read()


def _extract_class_body(content, class_name):
    """Extract the body of a class from C++ source."""
    idx = content.find(f'class {class_name}')
    if idx == -1:
        return ""
    # Find the opening brace
    brace_start = content.find('{', idx)
    if brace_start == -1:
        return ""
    depth = 1
    i = brace_start + 1
    while i < len(content) and depth > 0:
        if content[i] == '{':
            depth += 1
        elif content[i] == '}':
            depth -= 1
        i += 1
    return content[idx:i]


def _extract_method_body(content, method_name):
    """Extract the body of a method from C++ source, including its signature."""
    pattern = rf'(?:void|size_t|ALWAYS_INLINE)\s+{method_name}\s*\('
    match = re.search(pattern, content)
    if not match:
        return ""
    start = match.start()
    # Find the opening brace of the method
    brace_start = content.find('{', start)
    if brace_start == -1:
        return ""
    depth = 1
    i = brace_start + 1
    while i < len(content) and depth > 0:
        if content[i] == '{':
            depth += 1
        elif content[i] == '}':
            depth -= 1
        i += 1
    return content[start:i]


# =============================================================================
# Fail-to-pass tests
# =============================================================================

def test_pad_buffer_not_plain_string():
    """The PaddingChars class must NOT use String for the pad data member.

    String does not provide the 15-byte read padding required by
    memcpySmallAllowReadWriteOverflow15. Using it causes heap-buffer-overflow.
    """
    content = _read_target()
    padding_class = _extract_class_body(content, 'PaddingChars')
    assert padding_class, "PaddingChars class not found in source"

    # Look for member declarations in the private section
    # The old buggy code had: String pad_string;
    # Any correct fix must NOT have a bare String member for the pad data
    private_idx = padding_class.rfind('private:')
    if private_idx != -1:
        private_section = padding_class[private_idx:]
    else:
        private_section = padding_class

    # Check there is no "String pad_string;" member declaration
    assert not re.search(r'\bString\s+pad_string\s*;', private_section), \
        "pad_string member must not be plain String (lacks read padding for memcpy)"


def test_pad_buffer_has_read_padding():
    """The pad string buffer must use a container providing read padding.

    PaddedPODArray (or equivalent) provides the 15-byte read safety margin
    required by memcpySmallAllowReadWriteOverflow15 used in writeSlice.
    """
    content = _read_target()
    padding_class = _extract_class_body(content, 'PaddingChars')
    assert padding_class, "PaddingChars class not found"

    # The buffer must use PaddedPODArray (the ClickHouse container with padding)
    assert 'PaddedPODArray' in padding_class, \
        "PaddingChars must use PaddedPODArray for the pad buffer (provides read padding)"


def test_no_reinterpret_cast_in_append():
    """appendTo must not use reinterpret_cast on pad_string.data().

    The old code needed reinterpret_cast<const UInt8 *>(pad_string.data())
    because String::data() returns char*. With a UInt8 container like
    PaddedPODArray<UInt8>, data() already returns UInt8* and no cast is needed.
    This verifies the buffer type change was applied to the write path.
    """
    content = _read_target()
    append_body = _extract_method_body(content, 'appendTo')
    assert append_body, "appendTo method not found"

    assert 'reinterpret_cast' not in append_body, \
        "appendTo should not need reinterpret_cast with a UInt8 container"


def test_empty_pad_default_in_execute_path():
    """Empty pad string fallback to space must be in the execute path.

    The default of replacing an empty pad_string with " " must happen after
    retrieving the pad string from the column argument and before constructing
    PaddingChars. The old code had this inside PaddingChars::init(), but it
    should be in the executeImpl flow so the fallback applies correctly when
    the third argument is omitted.
    """
    content = _read_target()

    # The PaddingChars class should NOT contain the empty-string fallback
    padding_class = _extract_class_body(content, 'PaddingChars')
    assert padding_class, "PaddingChars class not found"

    # Check that the empty check is NOT inside PaddingChars
    has_empty_check_in_class = bool(
        re.search(r'pad_string\.empty\(\)', padding_class) and
        re.search(r'pad_string\s*=\s*"\\? "', padding_class)
    )
    assert not has_empty_check_in_class, \
        "Empty pad_string fallback should not be inside PaddingChars class"

    # The fallback should be somewhere in the file (in executeImpl)
    assert 'pad_string.empty()' in content, \
        "Empty pad_string check must exist in the execute path"


def test_cpp_syntax_valid():
    """The C++ code has valid syntax (verified via clang)."""
    result = subprocess.run(
        [
            'clang-18', '-fsyntax-only', '-std=c++23',
            '-I', f'{REPO}/src',
            '-I', f'{REPO}/base',
            '-I', f'{REPO}/contrib/libcxx/include',
            '-I', f'{REPO}/contrib/libcxxabi/include',
            '-I', f'{REPO}/contrib/boost',
            '-I', f'{REPO}/contrib/abseil-cpp',
            '-c', TARGET_FILE
        ],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO
    )
    # Only fail on syntax errors in our file, not missing dependency headers
    if result.returncode != 0:
        stderr = result.stderr
        lines = stderr.split('\n')
        our_errors = [l for l in lines if 'padString.cpp' in l and 'error:' in l]
        syntax_errors = [l for l in our_errors if 'file not found' not in l.lower()]
        if syntax_errors:
            raise AssertionError(f"Syntax errors found:\n{chr(10).join(syntax_errors)}")


# =============================================================================
# Pass-to-pass tests
# =============================================================================

def test_repo_padstring_tests_exist():
    """Test files for padString functions exist and are valid (pass_to_pass)."""
    test_files = [
        f"{REPO}/tests/queries/0_stateless/01940_pad_string.sql",
        f"{REPO}/tests/queries/0_stateless/01940_pad_string.reference",
        f"{REPO}/tests/queries/0_stateless/02986_leftpad_fixedstring.sql",
        f"{REPO}/tests/queries/0_stateless/02986_leftpad_fixedstring.reference",
    ]
    for f in test_files:
        r = subprocess.run(
            ["test", "-s", f],
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert r.returncode == 0, f"Test file missing or empty: {f}"


if __name__ == '__main__':
    import pytest
    pytest.main([__file__, '-v'])
