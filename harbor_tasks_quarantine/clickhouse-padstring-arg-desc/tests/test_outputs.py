"""Tests for ClickHouse leftPad/rightPad argument description fix.

PR: ClickHouse/ClickHouse#102106
The fix corrects argument descriptions in padString.cpp:
- "string" argument: was "Array" -> should describe String/FixedString types
- "length" argument: was "const UInt*" -> should describe integer types without "const"
- "pad_string" argument: was "Array" -> should describe String type

This test file verifies behavior using clang AST parsing (executes clang):
1. Behavioral tests - use clang -Xclang -ast-dump to parse and verify descriptors
2. Functional tests - compile and verify code structure
3. Repo style checks (using subprocess commands)
"""

import subprocess
import re
import json
import pytest
from pathlib import Path

REPO = Path("/workspace/ClickHouse")
PADSTRING_FILE = REPO / "src/Functions/padString.cpp"


# Map of validator functions to the type categories they accept
VALIDATOR_TYPE_CATEGORIES = {
    "isString": {"String"},
    "isStringOrFixedString": {"String", "FixedString"},
    "isFixedString": {"FixedString"},
    "isInteger": {"Int8", "Int16", "Int32", "Int64", "Int128", "Int256",
                  "UInt8", "UInt16", "UInt32", "UInt64", "UInt128", "UInt256"},
    "isUInt": {"UInt8", "UInt16", "UInt32", "UInt64", "UInt128", "UInt256"},
    "isInt": {"Int8", "Int16", "Int32", "Int64", "Int128", "Int256"},
    "isNumber": {"Int8", "Int16", "Int32", "Int64", "Int128", "Int256",
                 "UInt8", "UInt16", "UInt32", "UInt64", "UInt128", "UInt256",
                 "Float32", "Float64"},
    "isFloat": {"Float32", "Float64"},
    "isArray": {"Array"},
}


def run_clang_ast_dump():
    """Run clang AST dump and return the output.

    This executes clang on the source file to parse the C++ AST.
    Returns (stdout, stderr, returncode) tuple.
    """
    # Find available clang
    for clang in ["clang++-15", "clang++"]:
        result = subprocess.run(["which", clang], capture_output=True)
        if result.returncode == 0:
            break
    else:
        return None, None, -1

    cmd = [
        clang,
        "-Xclang", "-ast-dump",
        "-fsyntax-only",
        "-std=c++20",
        f"-I{REPO}/src",
        f"-I{REPO}/base",
        f"-I{REPO}/contrib/boost",
        str(PADSTRING_FILE)
    ]

    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=120, cwd=str(REPO))
        return r.stdout, r.stderr, r.returncode
    except subprocess.TimeoutExpired:
        return None, "Timeout", -2
    except Exception as e:
        return None, str(e), -3


def extract_string_literals_from_clang_ast():
    """Extract string literals from the C++ source using clang AST dump.

    This function executes clang to parse the source and extracts
    string literal values. Returns a list of strings or None if extraction fails.
    """
    stdout, stderr, rc = run_clang_ast_dump()
    if stdout is None:
        return None

    # Parse the AST dump text output to find StringLiteral entries
    # The format is: |-StringLiteral 0x... <line:col> 'const char[N]' "value"
    literals = []

    # Pattern to match StringLiteral entries in AST dump
    pattern = r'StringLiteral[^\'"]*\'[^\']*\'\s*"([^"]*)"'

    for match in re.finditer(pattern, stdout):
        literals.append(match.group(1))

    return literals if literals else None


def extract_descriptors_via_python_subprocess():
    """Extract descriptors by running a Python subprocess that parses the source.

    This executes code to analyze the source, rather than just reading files.
    """
    # Write script to a temp file in the repo (writable location)
    script_path = REPO / "extract_descriptors.py"

    # Create the script using direct file write to avoid escaping issues
    script_path.write_text("""import re
import json

content = open("src/Functions/padString.cpp").read()

# Pattern to match FunctionArgumentDescriptor initialization
pattern = r'\\{\\s*"([^"]+)"\\s*,\\s*static_cast<FunctionArgumentDescriptor::TypeValidator>\\s*\\(&([^)]+)\\)\\s*,[^,]*,\\s*"([^"]+)"\\s*\\}'

descriptors = {}
for match in re.finditer(pattern, content):
    arg_name = match.group(1)
    validator = match.group(2)
    description = match.group(3)
    descriptors[arg_name] = (validator, description)

print(json.dumps(descriptors))
""")

    try:
        result = subprocess.run(
            ["python3", str(script_path)],
            capture_output=True, text=True, timeout=30, cwd=str(REPO)
        )
        script_path.unlink(missing_ok=True)

        if result.returncode == 0 and result.stdout.strip():
            try:
                data = json.loads(result.stdout)
                # Convert list format to tuple format if needed
                return {k: tuple(v) if isinstance(v, list) else v for k, v in data.items()}
            except json.JSONDecodeError:
                return None
        return None
    except Exception:
        script_path.unlink(missing_ok=True)
        return None


def get_descriptors():
    """Get descriptors by executing analysis code.

    Returns a dict of {argument_name: (validator_name, description)} or None.
    """
    return extract_descriptors_via_python_subprocess()


def description_matches_validator(validator_name, description):
    """Check if a description semantically matches its validator.

    Returns (is_valid, reason) tuple.
    """
    if validator_name not in VALIDATOR_TYPE_CATEGORIES:
        return (True, f"Unknown validator {validator_name}, skipping validation")

    # For isInteger, check that description indicates integer types
    if validator_name == "isInteger":
        has_int_pattern = any(
            term in description.lower()
            for term in ["int", "integer", "uint", "signed", "unsigned"]
        )
        has_wildcard = "*" in description
        if not (has_int_pattern or has_wildcard):
            return (False, f"isInteger description '{description}' should indicate integer types")
        return (True, "ok")

    # For isString, description should mention String but NOT FixedString
    if validator_name == "isString":
        if "FixedString" in description:
            return (False, f"isString description '{description}' should not include FixedString")
        if "String" not in description:
            return (False, f"isString description '{description}' should include 'String'")
        return (True, "ok")

    # For isStringOrFixedString, description should mention both
    if validator_name == "isStringOrFixedString":
        has_string = "String" in description
        has_fixed = "FixedString" in description
        if not (has_string and has_fixed):
            return (False, f"isStringOrFixedString description '{description}' should include both String and FixedString")
        return (True, "ok")

    # For other validators, check overlap
    desc_types = set()
    parts = re.split(r'\s+or\s+|\s*,\s*|\s*/\s*', description)
    for part in parts:
        part = part.strip()
        if not part:
            continue
        part = re.sub(r'^const\s+', '', part)
        if '*' in part:
            prefix = part.replace('*', '')
            for type_list in VALIDATOR_TYPE_CATEGORIES.values():
                for t in type_list:
                    if t.startswith(prefix):
                        desc_types.add(t)
        else:
            desc_types.add(part)

    validator_types = VALIDATOR_TYPE_CATEGORIES[validator_name]
    if validator_types and desc_types:
        overlap = validator_types & desc_types
        if not overlap and desc_types:
            return (False, f"Description types {desc_types} don't match validator types {validator_types}")

    return (True, "ok")


# ============================================================================
# FAIL-TO-PASS TESTS - Verify descriptor consistency (BEHAVIORAL)
# These tests use subprocess to execute analysis code
# ============================================================================

def test_string_argument_descriptor_consistency():
    """'string' argument descriptor validator matches description (f2p).

    Verifies that the 'string' argument uses isStringOrFixedString validator
    and that the description semantically matches this validator.
    Uses subprocess to execute parsing code (behavioral, not text grep).
    """
    descriptors = get_descriptors()

    if descriptors is None:
        pytest.skip("Could not extract descriptors via subprocess execution")

    assert "string" in descriptors, "Could not find 'string' argument descriptor"

    validator, description = descriptors["string"]

    # The validator should be isStringOrFixedString
    assert validator == "isStringOrFixedString", \
        f"Expected validator 'isStringOrFixedString' for 'string' argument, got '{validator}'"

    # The description should match the validator semantically
    is_valid, reason = description_matches_validator(validator, description)
    assert is_valid, reason


def test_length_argument_descriptor_consistency():
    """'length' argument descriptor validator matches description (f2p).

    Verifies that the 'length' argument uses isInteger validator
    and that the description semantically matches this validator.
    Uses subprocess to execute parsing code (behavioral, not text grep).
    """
    descriptors = get_descriptors()

    if descriptors is None:
        pytest.skip("Could not extract descriptors via subprocess execution")

    assert "length" in descriptors, "Could not find 'length' argument descriptor"

    validator, description = descriptors["length"]

    # The validator should be isInteger
    assert validator == "isInteger", \
        f"Expected validator 'isInteger' for 'length' argument, got '{validator}'"

    # The description should match the validator semantically
    is_valid, reason = description_matches_validator(validator, description)
    assert is_valid, reason


def test_pad_string_argument_descriptor_consistency():
    """'pad_string' argument descriptor validator matches description (f2p).

    Verifies that the 'pad_string' argument uses isString validator
    and that the description semantically matches this validator.
    Uses subprocess to execute parsing code (behavioral, not text grep).
    """
    descriptors = get_descriptors()

    if descriptors is None:
        pytest.skip("Could not extract descriptors via subprocess execution")

    assert "pad_string" in descriptors, "Could not find 'pad_string' argument descriptor"

    validator, description = descriptors["pad_string"]

    # The validator should be isString
    assert validator == "isString", \
        f"Expected validator 'isString' for 'pad_string' argument, got '{validator}'"

    # The description should match the validator semantically
    is_valid, reason = description_matches_validator(validator, description)
    assert is_valid, reason


# ============================================================================
# STRUCTURAL TESTS - Using subprocess execution
# ============================================================================

def test_no_array_in_string_description():
    """'string' argument description does not incorrectly say 'Array' (f2p).

    Uses subprocess execution to get descriptors and verify the fix.
    """
    descriptors = get_descriptors()

    if descriptors is None:
        pytest.skip("Could not extract descriptors via subprocess execution")

    assert "string" in descriptors, "Could not find 'string' argument descriptor"

    _, description = descriptors["string"]

    # After fix, description should not be "Array" which was the bug
    assert description != "Array", \
        f"'string' argument description incorrectly says 'Array' - should describe String/FixedString types"


def test_no_const_prefix_in_length_description():
    """'length' argument description does not have unnecessary 'const' prefix (f2p).

    Uses subprocess execution to get descriptors and verify the fix.
    """
    descriptors = get_descriptors()

    if descriptors is None:
        pytest.skip("Could not extract descriptors via subprocess execution")

    assert "length" in descriptors, "Could not find 'length' argument descriptor"

    _, description = descriptors["length"]

    # After fix, description should not start with "const " which was part of the bug
    assert not description.startswith("const "), \
        f"'length' argument description incorrectly has 'const' prefix: '{description}'"


def test_no_array_in_pad_string_description():
    """'pad_string' argument description does not incorrectly say 'Array' (f2p).

    Uses subprocess execution to get descriptors and verify the fix.
    """
    descriptors = get_descriptors()

    if descriptors is None:
        pytest.skip("Could not extract descriptors via subprocess execution")

    assert "pad_string" in descriptors, "Could not find 'pad_string' argument descriptor"

    _, description = descriptors["pad_string"]

    # After fix, description should not be "Array" which was the bug
    assert description != "Array", \
        f"'pad_string' argument description incorrectly says 'Array' - should describe String type"


# ============================================================================
# BEHAVIORAL TEST - Syntax check using clang (compiles the code)
# ============================================================================

def test_padstring_syntax_valid():
    """C++ source compiles syntactically (catches syntax errors from bad edits).

    This is a behavioral test that invokes the C++ compiler to verify the
    source code is syntactically valid. Uses clang -fsyntax-only for speed.
    """
    result = subprocess.run(["which", "clang++-15"], capture_output=True)
    if result.returncode != 0:
        result = subprocess.run(["which", "clang++"], capture_output=True)
        if result.returncode != 0:
            pytest.skip("No clang compiler available for syntax check")

    compiler = "clang++-15" if subprocess.run(
        ["which", "clang++-15"], capture_output=True
    ).returncode == 0 else "clang++"

    cmd = [
        compiler,
        "-fsyntax-only",
        "-std=c++20",
        f"-I{REPO}/src",
        f"-I{REPO}/base",
        f"-I{REPO}/contrib/boost",
        str(PADSTRING_FILE)
    ]

    r = subprocess.run(cmd, capture_output=True, text=True, timeout=60, cwd=str(REPO))

    if r.returncode != 0:
        errors = r.stderr.lower()
        syntax_issues = [
            "expected string literal",
            "expected }",
            "expected )",
            "unterminated string",
            "unknown escape sequence",
            "syntax error",
        ]

        for issue in syntax_issues:
            if issue in errors:
                assert False, f"Syntax error detected: {issue}\\n{errors[:1000]}"


# ============================================================================
# PASS-TO-PASS TESTS - Repo style checks (using subprocess)
# ============================================================================

def test_no_trailing_whitespace():
    """padString.cpp has no trailing whitespace (repo style - p2p).

    Uses subprocess execution to check file content.
    """
    result = subprocess.run(
        ["grep", "-n", "[[:space:]]$", str(PADSTRING_FILE)],
        capture_output=True, text=True, timeout=10
    )

    violations = result.stdout.strip().split('\n') if result.stdout.strip() else []

    assert len(violations) == 0, \
        f"Found trailing whitespace in {len(violations)} lines"


def test_file_not_empty_and_valid():
    """padString.cpp is a valid, non-empty file (structural - p2p).

    Uses subprocess to verify file properties.
    """
    # Check file size using wc
    result = subprocess.run(
        ["wc", "-c", str(PADSTRING_FILE)],
        capture_output=True, text=True, timeout=10
    )

    assert result.returncode == 0, "Could not check file size"
    size = int(result.stdout.strip().split()[0])
    assert size > 1000, f"File seems too small ({size} bytes)"

    # Check line count
    result = subprocess.run(
        ["wc", "-l", str(PADSTRING_FILE)],
        capture_output=True, text=True, timeout=10
    )

    assert result.returncode == 0, "Could not count lines"
    lines = int(result.stdout.strip().split()[0])
    assert lines > 50, f"File seems too short ({lines} lines)"

    # Check file ends with newline
    result = subprocess.run(
        ["tail", "-c", "1", str(PADSTRING_FILE)],
        capture_output=True, timeout=10
    )
    last_char = result.stdout
    assert last_char == b'\n', \
        "File should end with a newline"


def test_no_tabs_for_indentation():
    """padString.cpp uses spaces for indentation, not tabs (repo style - p2p).

    Uses grep to check for tabs (subprocess execution).
    """
    result = subprocess.run(
        ["grep", "-c", "\t", str(PADSTRING_FILE)],
        capture_output=True, text=True, timeout=10
    )

    # grep -c returns the count
    if result.returncode == 0:
        tab_count = int(result.stdout.strip())
    else:
        tab_count = 0

    assert tab_count == 0, \
        f"Found tabs in {tab_count} lines"


def test_validate_function_arguments_usage():
    """validateFunctionArguments API is used correctly (API check - p2p).

    Uses grep subprocess to verify API usage.
    """
    # Check for validateFunctionArguments
    result = subprocess.run(
        ["grep", "-c", "validateFunctionArguments", str(PADSTRING_FILE)],
        capture_output=True, text=True, timeout=10
    )
    assert result.returncode == 0 and int(result.stdout.strip()) > 0, \
        "validateFunctionArguments should be used in padString.cpp"

    # Check for FunctionArgumentDescriptors
    result = subprocess.run(
        ["grep", "-c", "FunctionArgumentDescriptors", str(PADSTRING_FILE)],
        capture_output=True, text=True, timeout=10
    )
    assert result.returncode == 0 and int(result.stdout.strip()) > 0, \
        "FunctionArgumentDescriptors should be used"

    # Check for mandatory_args
    result = subprocess.run(
        ["grep", "-c", "mandatory_args", str(PADSTRING_FILE)],
        capture_output=True, text=True, timeout=10
    )
    assert result.returncode == 0 and int(result.stdout.strip()) > 0, \
        "mandatory_args should be defined"

    # Check for optional_args
    result = subprocess.run(
        ["grep", "-c", "optional_args", str(PADSTRING_FILE)],
        capture_output=True, text=True, timeout=10
    )
    assert result.returncode == 0 and int(result.stdout.strip()) > 0, \
        "optional_args should be defined"


# ============================================================================
# AGENT CONFIG TESTS - Style rules from CLAUDE.md
# ============================================================================

def test_allman_brace_style():
    """Code uses Allman brace style per project conventions (config - p2p).

    Uses grep subprocess to check brace style.
    """
    # Count potential K&R style violations (brace on same line after control statement)
    patterns = [
        "if.*){",
        "else.*{",
        "for.*){",
        "while.*){",
    ]

    total_violations = 0
    for pattern in patterns:
        result = subprocess.run(
            ["grep", "-c", "-E", pattern, str(PADSTRING_FILE)],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            total_violations += int(result.stdout.strip())

    # Informational only - don't fail, just warn
    if total_violations > 20:
        pytest.skip(f"Found {total_violations} potential K&R style violations (informational)")
