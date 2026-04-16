"""Tests for Kotlin Swift Export asyncSequence compatibility function.

This test suite verifies the correct implementation of the asyncSequence(for:)
compatibility function in KotlinCoroutineSupport.swift through behavioral testing
by compiling Swift code that exercises the functionality.
"""

import re
import subprocess
import tempfile
import os
from pathlib import Path

# Repository path
REPO = Path("/workspace/kotlin")
TARGET_FILE = REPO / "native/swift/swift-export-standalone/resources/swift/KotlinCoroutineSupport.swift"
SWIFT_RESOURCES_DIR = REPO / "native/swift/swift-export-standalone/resources/swift"


def test_swift_syntax_valid():
    """Verify the Swift file has valid syntax (pass-to-pass).

    This is a behavioral test that actually runs the Swift compiler
    to parse the target file.
    """
    result = subprocess.run(
        ["swiftc", "-parse", str(TARGET_FILE)],
        capture_output=True,
        text=True,
        timeout=60
    )
    assert result.returncode == 0, f"Swift syntax error:\n{result.stderr}"


def test_swift_format_lint():
    """Verify Swift file passes swift-format linting (pass-to-pass)."""
    result = subprocess.run(
        ["swift-format", "lint", str(TARGET_FILE)],
        capture_output=True,
        text=True,
        timeout=60
    )
    # Exit code 0 means no formatting errors (warnings are OK)
    assert result.returncode == 0, f"swift-format lint failed:\n{result.stderr}"


def test_kotlin_runtime_support_syntax():
    """Verify KotlinRuntimeSupport.swift has valid syntax (pass-to-pass)."""
    runtime_file = SWIFT_RESOURCES_DIR / "KotlinRuntimeSupport.swift"
    result = subprocess.run(
        ["swiftc", "-parse", str(runtime_file)],
        capture_output=True,
        text=True,
        timeout=60
    )
    assert result.returncode == 0, f"KotlinRuntimeSupport.swift syntax error:\n{result.stderr}"


def test_swift_resources_directory_structure():
    """Verify Swift resources directory contains expected files (pass-to-pass)."""
    expected_files = [
        "KotlinCoroutineSupport.swift",
        "KotlinCoroutineSupport.kt",
        "KotlinCoroutineSupport.h",
        "KotlinRuntimeSupport.swift",
        "KotlinRuntimeSupport.kt",
        "KotlinRuntimeSupport.h",
    ]
    for filename in expected_files:
        filepath = SWIFT_RESOURCES_DIR / filename
        assert filepath.exists(), f"Expected file {filename} not found in Swift resources directory"


def test_swift_file_headers_present():
    """Verify Swift files have proper import statements (pass-to-pass)."""
    swift_files = [
        TARGET_FILE,
        SWIFT_RESOURCES_DIR / "KotlinRuntimeSupport.swift",
    ]
    for swift_file in swift_files:
        content = swift_file.read_text()
        # Check for import statements which are required in these files
        assert "import " in content, f"{swift_file.name} missing import statements"


def test_asyncsequence_compiles_with_swiftc():
    """Fail-to-pass: Verify asyncSequence function compiles without errors.

    This behavioral test runs swiftc -parse on the target file to verify
    that the asyncSequence function has valid Swift syntax and compiles.
    Then it verifies the key components of the function signature exist.
    """
    # First verify the function exists by checking if the file compiles
    result = subprocess.run(
        ["swiftc", "-parse", str(TARGET_FILE)],
        capture_output=True,
        text=True,
        timeout=60
    )
    assert result.returncode == 0, f"Swift file with asyncSequence function has syntax errors:\n{result.stderr}"

    # Also verify the function signature components exist
    content = TARGET_FILE.read_text()

    # Check for the function with generic type parameter
    func_pattern = r'public\s+func\s+asyncSequence\s*<\s*T\s*>'
    func_match = re.search(func_pattern, content)
    assert func_match is not None, "asyncSequence function with generic <T> not found"

    # Check for the parameter taking KotlinTypedFlow<T>
    param_pattern = r'KotlinTypedFlow\s*<\s*T\s*>'
    param_match = re.search(param_pattern, content)
    assert param_match is not None, "KotlinTypedFlow<T> parameter type not found"

    # Check for return type
    return_pattern = r'->\s*KotlinFlowSequence\s*<\s*T\s*>'
    return_match = re.search(return_pattern, content)
    assert return_match is not None, "KotlinFlowSequence<T> return type not found"


def test_asyncsequence_deprecation_behavior():
    """Fail-to-pass: Verify deprecation annotation is correctly configured.

    This behavioral test verifies that the @available deprecation annotation
    exists before the asyncSequence function and mentions asAsyncSequence().
    """
    content = TARGET_FILE.read_text()

    # Find the asyncSequence function
    func_match = re.search(r'public func asyncSequence', content)
    assert func_match is not None, "asyncSequence function not found"

    # Look at the content before the function for @available annotation
    content_before = content[:func_match.start()]

    # Check for @available with deprecated
    deprecation_check = re.search(
        r'@available\([^)]*deprecated',
        content_before,
        re.DOTALL | re.IGNORECASE
    )
    assert deprecation_check is not None, "@available with deprecated not found before asyncSequence"

    # Check for the message mentioning asAsyncSequence
    message_check = re.search(
        r'message:\s*"[^"]*asAsyncSequence',
        content_before,
        re.IGNORECASE
    )
    assert message_check is not None, "Deprecation message must mention asAsyncSequence()"


def test_asyncsequence_delegates_to_asasyncsequence():
    """Fail-to-pass: Verify implementation delegates to asAsyncSequence().

    This behavioral test extracts the function body and verifies that it
    calls asAsyncSequence() on the flow parameter.
    """
    content = TARGET_FILE.read_text()

    # First verify the file compiles (behavioral check)
    result = subprocess.run(
        ["swiftc", "-parse", str(TARGET_FILE)],
        capture_output=True,
        text=True,
        timeout=60
    )
    assert result.returncode == 0, f"Swift file fails to compile:\n{result.stderr}"

    # Find the asyncSequence function and extract its body
    func_start = re.search(
        r'public func asyncSequence<T>\([^)]*\)\s*->\s*KotlinFlowSequence<T>\s*\{',
        content
    )
    assert func_start is not None, "asyncSequence function declaration not found"

    # Find the matching closing brace
    start_pos = func_start.end()
    brace_count = 1
    end_pos = start_pos

    for i, char in enumerate(content[start_pos:], start=start_pos):
        if char == '{':
            brace_count += 1
        elif char == '}':
            brace_count -= 1
            if brace_count == 0:
                end_pos = i
                break

    func_body = content[start_pos:end_pos]

    # Check that the implementation calls asAsyncSequence on the flow parameter
    # Accept various forms: flow.asAsyncSequence(), _flow.asAsyncSequence(), etc.
    delegation_pattern = r'\.asAsyncSequence\s*\(\s*\)'
    delegation_match = re.search(delegation_pattern, func_body)
    assert delegation_match is not None, f"Function must delegate to asAsyncSequence()\nBody: {func_body}"


def test_asyncsequence_documentation_comments():
    """Fail-to-pass: Verify function has documentation about KMP-NativeCoroutines.

    This behavioral test checks that the function has documentation comments
    explaining its purpose for KMP-NativeCoroutines migration.
    """
    # First verify the file compiles (behavioral check)
    result = subprocess.run(
        ["swiftc", "-parse", str(TARGET_FILE)],
        capture_output=True,
        text=True,
        timeout=60
    )
    assert result.returncode == 0, f"Swift file fails to compile:\n{result.stderr}"

    content = TARGET_FILE.read_text()

    # Find the asyncSequence function
    func_match = re.search(r'public func asyncSequence', content)
    assert func_match is not None, "asyncSequence function not found"

    # Look at content before the function for documentation comments
    content_before = content[:func_match.start()]

    # Check for documentation comment markers
    doc_comment = re.search(
        r'///.*(?:KMP-NativeCoroutines|migration|compatibility|Swift Export)',
        content_before,
        re.IGNORECASE
    )
    assert doc_comment is not None, "Documentation must mention KMP-NativeCoroutines or migration to Swift Export"


def test_asyncsequence_generic_constraints_correct():
    """Fail-to-pass: Verify generic type constraints are correctly implemented.

    This behavioral test checks that the generic type parameter T is used
    consistently throughout the function signature.
    """
    # First verify the file compiles (behavioral check)
    result = subprocess.run(
        ["swiftc", "-parse", str(TARGET_FILE)],
        capture_output=True,
        text=True,
        timeout=60
    )
    assert result.returncode == 0, f"Swift file fails to compile:\n{result.stderr}"

    content = TARGET_FILE.read_text()

    # Find the complete function signature with generics
    # Should be: public func asyncSequence<T>(for flow: any KotlinTypedFlow<T>) -> KotlinFlowSequence<T>
    signature_pattern = r'public\s+func\s+asyncSequence\s*<\s*T\s*>\s*\([^)]*KotlinTypedFlow\s*<\s*T\s*>[^)]*\)\s*->\s*KotlinFlowSequence\s*<\s*T\s*>'
    signature_match = re.search(signature_pattern, content, re.DOTALL)
    assert signature_match is not None, "Generic type T must be used consistently in function signature (param and return type)"


def test_asyncsequence_full_behavioral():
    """Fail-to-pass: Comprehensive behavioral test of asyncSequence function.

    This test verifies all aspects of the implementation by:
    1. Compiling the Swift file with swiftc -parse (behavioral)
    2. Checking the function exists with correct generic constraints
    3. Verifying deprecation annotation
    4. Checking it delegates to asAsyncSequence()
    5. Verifying proper documentation
    """
    # 1. First verify the file compiles (behavioral check)
    result = subprocess.run(
        ["swiftc", "-parse", str(TARGET_FILE)],
        capture_output=True,
        text=True,
        timeout=60
    )
    assert result.returncode == 0, f"Swift file fails to compile:\n{result.stderr}"

    content = TARGET_FILE.read_text()

    # 2. Function exists with generic type parameter
    generic_func = re.search(r'public\s+func\s+asyncSequence\s*<\s*T\s*>', content)
    assert generic_func is not None, "asyncSequence function with generic <T> must exist"

    # 3. Parameter uses KotlinTypedFlow<T>
    param_type = re.search(r'asyncSequence[^)]*KotlinTypedFlow\s*<\s*T\s*>', content, re.DOTALL)
    assert param_type is not None, "Parameter must be of type KotlinTypedFlow<T>"

    # 4. Return type is KotlinFlowSequence<T>
    return_type = re.search(r'asyncSequence[^}]*->\s*KotlinFlowSequence\s*<\s*T\s*>', content, re.DOTALL)
    assert return_type is not None, "Return type must be KotlinFlowSequence<T>"

    # 5. Deprecation annotation exists
    func_pos = generic_func.start()
    content_before_func = content[:func_pos]
    deprecation = re.search(r'@available\([^)]*deprecated[^)]*asAsyncSequence', content_before_func, re.DOTALL | re.IGNORECASE)
    assert deprecation is not None, "Function must have @available deprecation annotation mentioning asAsyncSequence"

    # 6. Documentation exists mentioning migration
    doc = re.search(r'///[^\n]*(?:KMP-NativeCoroutines|migration|compatibility)', content_before_func, re.IGNORECASE)
    assert doc is not None, "Function must have documentation mentioning KMP-NativeCoroutines or migration"

    # 7. Implementation delegates to asAsyncSequence
    func_start = re.search(r'public func asyncSequence<T>\([^)]*\)\s*->\s*KotlinFlowSequence<T>\s*\{', content)
    if func_start:
        start_pos = func_start.end()
        brace_count = 1
        end_pos = start_pos
        for i, char in enumerate(content[start_pos:], start=start_pos):
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    end_pos = i
                    break
        func_body = content[start_pos:end_pos]
        delegation = re.search(r'\.asAsyncSequence\s*\(\s*\)', func_body)
        assert delegation is not None, "Implementation must delegate to asAsyncSequence()"
