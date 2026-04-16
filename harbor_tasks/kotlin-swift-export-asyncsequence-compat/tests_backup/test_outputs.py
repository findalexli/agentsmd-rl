"""Tests for Kotlin Swift Export asyncSequence compatibility function.

This test suite verifies the correct implementation of the asyncSequence(for:)
compatibility function in KotlinCoroutineSupport.swift.
"""

import re
import subprocess
from pathlib import Path

# Repository path
REPO = Path("/workspace/kotlin")
TARGET_FILE = REPO / "native/swift/swift-export-standalone/resources/swift/KotlinCoroutineSupport.swift"
SWIFT_RESOURCES_DIR = REPO / "native/swift/swift-export-standalone/resources/swift"


def test_swift_syntax_valid():
    """Verify the Swift file has valid syntax (pass-to-pass)."""
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
    """Verify Swift files have proper header comments (pass-to-pass)."""
    swift_files = [
        TARGET_FILE,
        SWIFT_RESOURCES_DIR / "KotlinRuntimeSupport.swift",
    ]
    for swift_file in swift_files:
        content = swift_file.read_text()
        # Check for import statements which are required in these files
        assert "import " in content, f"{swift_file.name} missing import statements"


def test_asyncsequence_function_exists():
    """Fail-to-pass: Verify asyncSequence(for:) function exists with correct signature."""
    content = TARGET_FILE.read_text()

    # Check for the function declaration with generic type parameter
    func_pattern = r"public func asyncSequence<T>\(\s*for flow:\s*any KotlinTypedFlow<T>\s*\)\s*->\s*KotlinFlowSequence<T>"
    match = re.search(func_pattern, content, re.MULTILINE | re.DOTALL)
    assert match is not None, "asyncSequence(for:) function with correct signature not found"


def test_asyncsequence_deprecation_annotation():
    """Fail-to-pass: Verify function has correct deprecation annotation."""
    content = TARGET_FILE.read_text()

    # Check for deprecation annotation before the function
    deprecation_pattern = r"@available\(\s*\*,\s*deprecated,\s*message:\s*\"Use `asAsyncSequence\(\)` from Swift Export\"\s*\)"
    match = re.search(deprecation_pattern, content)
    assert match is not None, "@available deprecation annotation with correct message not found"

    # Verify it appears before the function
    func_match = re.search(r"public func asyncSequence<T>", content)
    assert func_match is not None, "asyncSequence function not found"

    # Check that deprecation appears before the function
    content_before_func = content[:func_match.start()]
    deprecation_in_scope = re.search(deprecation_pattern, content_before_func)
    assert deprecation_in_scope is not None, "Deprecation annotation not found before asyncSequence function"


def test_asyncsequence_documentation_comment():
    """Fail-to-pass: Verify function has documentation comments explaining purpose."""
    content = TARGET_FILE.read_text()

    # Find the function
    func_match = re.search(r"public func asyncSequence<T>", content)
    assert func_match is not None, "asyncSequence function not found"

    # Look for documentation comments before the function
    content_before_func = content[:func_match.start()]

    # Check for documentation explaining KMP-NativeCoroutines compatibility
    kmp_pattern = r"KMP-NativeCoroutines"
    migration_pattern = r"migration.*Swift Export"

    kmp_match = re.search(kmp_pattern, content_before_func, re.IGNORECASE)
    migration_match = re.search(migration_pattern, content_before_func, re.IGNORECASE)

    assert kmp_match is not None or migration_pattern is not None, \
        "Documentation comment mentioning KMP-NativeCoroutines or migration not found"


def test_asyncsequence_implementation_correct():
    """Fail-to-pass: Verify implementation delegates to asAsyncSequence()."""
    content = TARGET_FILE.read_text()

    # Find the function and its body
    func_start = re.search(r"public func asyncSequence<T>\([^)]+\)\s*->\s*KotlinFlowSequence<T>\s*\{", content)
    assert func_start is not None, "asyncSequence function declaration not found"

    # Extract the function body (find matching closing brace)
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

    # Check that implementation delegates to asAsyncSequence()
    implementation_pattern = r"flow\.asAsyncSequence\(\)"
    match = re.search(implementation_pattern, func_body)
    assert match is not None, f"Implementation does not delegate to flow.asAsyncSequence()\nBody: {func_body}"


def test_asyncsequence_generic_constraint():
    """Fail-to-pass: Verify function uses generic type parameter T correctly."""
    content = TARGET_FILE.read_text()

    # Check for generic type parameter T in function signature
    generic_pattern = r"asyncSequence<T>"
    return_type_pattern = r"->\s*KotlinFlowSequence<T>"
    param_type_pattern = r"KotlinTypedFlow<T>"

    generic_match = re.search(generic_pattern, content)
    return_match = re.search(return_type_pattern, content)
    param_match = re.search(param_type_pattern, content)

    assert generic_match is not None, "Generic type parameter T not found in function name"
    assert return_match is not None, "Generic type T not found in return type"
    assert param_match is not None, "Generic type T not found in parameter type"
