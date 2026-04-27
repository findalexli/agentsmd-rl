"""
Tests for ClickHouse padString heap-buffer-overflow fix.

The bug was a heap-buffer-overflow caused by memcpySmallAllowReadWriteOverflow15
reading beyond allocated memory because the PaddingChars class stored the pad
string in a regular std::string without 15 extra bytes of read padding.
"""

import subprocess
import os

REPO = "/workspace/ClickHouse"
TARGET_FILE = "src/Functions/padString.cpp"
FULL_PATH = os.path.join(REPO, TARGET_FILE)


def _read_target():
    """Read the target source file."""
    with open(FULL_PATH, "r") as f:
        return f.read()


# =============================================================================
# Fail-to-pass tests
# =============================================================================


def test_pad_string_uses_padded_buffer():
    """
    Fail-to-pass: The pad_string member in PaddingChars must use a buffer type
    that provides at least 15 extra bytes of read padding (PaddedPODArray),
    not String (std::string).

    String does not guarantee any read padding beyond its size, causing
    memcpySmallAllowReadWriteOverflow15 to read out of bounds.
    """
    r = subprocess.run(
        [
            "python3",
            "-c",
            "import re, sys\n"
            "\n"
            "with open('{}') as f:\n"
            "    content = f.read()\n"
            "\n"
            "# The PaddingChars class must declare pad_string as PaddedPODArray\n"
            "# (not String) to provide 15 extra bytes of read padding.\n"
            "# Note: there is a separate local String pad_string in executeImpl\n"
            "# which is fine - we only care about the class member.\n"
            "if not re.search(r'PaddedPODArray<.*>\\s+pad_string\\b', content):\n"
            "    print('FAIL: pad_string member should use PaddedPODArray')\n"
            "    sys.exit(1)\n"
            "\n"
            "print('PASS')".format(FULL_PATH),
        ],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Buffer type check failed: {r.stdout.strip()} {r.stderr.strip()}"
    assert "PASS" in r.stdout


def test_write_slice_compatible_with_buffer():
    """
    Fail-to-pass: writeSlice calls should use pad_string.data() directly
    without reinterpret_cast. When the storage is PaddedPODArray<UInt8>,
    data() already returns UInt8*, so no cast is needed.

    The old code needed reinterpret_cast because String::data() returns char*.
    """
    r = subprocess.run(
        [
            "python3",
            "-c",
            "import re, sys\n"
            "\n"
            "with open('{}') as f:\n"
            "    content = f.read()\n"
            "\n"
            "# Old pattern: writeSlice(...reinterpret_cast...pad_string.data()...)\n"
            "if re.search(r'writeSlice.*reinterpret_cast.*pad_string\\.data\\(\\)', content):\n"
            "    print('FAIL: writeSlice still uses reinterpret_cast on pad_string.data()')\n"
            "    sys.exit(1)\n"
            "\n"
            "# New pattern: writeSlice(...pad_string.data()...)\n"
            "if not re.search(r'writeSlice.*pad_string\\.data\\(\\)', content):\n"
            "    print('FAIL: writeSlice should reference pad_string.data()')\n"
            "    sys.exit(1)\n"
            "\n"
            "print('PASS')".format(FULL_PATH),
        ],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert r.returncode == 0, f"writeSlice check failed: {r.stdout.strip()} {r.stderr.strip()}"
    assert "PASS" in r.stdout


def test_uses_standard_argument_validation():
    """
    Fail-to-pass: Argument validation should use ClickHouse's standard
    validateFunctionArguments helper instead of manual type-checking throws
    with NUMBER_OF_ARGUMENTS_DOESNT_MATCH.
    """
    r = subprocess.run(
        [
            "python3",
            "-c",
            "import sys\n"
            "\n"
            "with open('{}') as f:\n"
            "    content = f.read()\n"
            "\n"
            "if 'validateFunctionArguments' not in content:\n"
            "    print('FAIL: should use validateFunctionArguments helper')\n"
            "    sys.exit(1)\n"
            "\n"
            "if 'NUMBER_OF_ARGUMENTS_DOESNT_MATCH' in content:\n"
            "    print('FAIL: manual argument count check should be removed')\n"
            "    sys.exit(1)\n"
            "\n"
            "print('PASS')".format(FULL_PATH),
        ],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Validation check failed: {r.stdout.strip()} {r.stderr.strip()}"
    assert "PASS" in r.stdout


def test_error_message_reflects_accepted_types():
    """
    Fail-to-pass: The error message for the first argument should accurately
    state that both String and FixedString are accepted types.
    """
    content = _read_target()
    assert "String or FixedString" in content, \
        "Error message should mention both String and FixedString as accepted types"


def test_no_redundant_runtime_exception_for_const_column():
    """
    Fail-to-pass: The runtime exception for null column_pad_const should be
    replaced with a debug assertion, since the argument validator already
    guarantees the third argument is a const column.
    """
    content = _read_target()
    assert "must be a constant string" not in content, \
        "Redundant 'must be a constant string' runtime exception should be removed"


# =============================================================================
# Pass-to-pass tests (origin: repo_tests)
# =============================================================================


def test_pad_string_sql_test_exists():
    """
    Pass-to-pass: Existing 01940_pad_string SQL test files should be present.
    """
    r = subprocess.run(
        ["test", "-f", os.path.join(REPO, "tests/queries/0_stateless/01940_pad_string.sql")],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert r.returncode == 0, "01940_pad_string.sql test file should exist"

    r = subprocess.run(
        ["test", "-f", os.path.join(REPO, "tests/queries/0_stateless/01940_pad_string.reference")],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert r.returncode == 0, "01940_pad_string.reference test file should exist"


def test_leftpad_fixedstring_sql_test_exists():
    """
    Pass-to-pass: Existing 02986_leftpad_fixedstring SQL test files should be present.
    """
    r = subprocess.run(
        ["test", "-f", os.path.join(REPO, "tests/queries/0_stateless/02986_leftpad_fixedstring.sql")],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert r.returncode == 0, "02986_leftpad_fixedstring.sql test file should exist"


def test_pad_string_cpp_has_valid_structure():
    """
    Pass-to-pass: padString.cpp should have valid include/namespace structure.
    """
    r = subprocess.run(
        [
            "python3",
            "-c",
            "import sys\n"
            "\n"
            "with open('{}') as f:\n"
            "    content = f.read()\n"
            "\n"
            "if '#include <' not in content:\n"
            "    print('FAIL: missing include statements')\n"
            "    sys.exit(1)\n"
            "\n"
            "if 'namespace DB' not in content:\n"
            "    print('FAIL: missing DB namespace')\n"
            "    sys.exit(1)\n"
            "\n"
            "if 'class PaddingChars' not in content:\n"
            "    print('FAIL: missing PaddingChars class')\n"
            "    sys.exit(1)\n"
            "\n"
            "print('PASS')".format(FULL_PATH),
        ],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Structure check failed: {r.stdout.strip()} {r.stderr.strip()}"
    assert "PASS" in r.stdout
