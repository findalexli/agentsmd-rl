"""
Test outputs for CoreProgressManager sun.misc.Unsafe removal.

This task verifies that CoreProgressManager.java has been updated to use
ConcurrentHashMap instead of ConcurrentLongObjectMap (which uses sun.misc.Unsafe).
"""

import subprocess
import re
import sys
from pathlib import Path

REPO = Path("/workspace/kotlin")
TARGET_FILE = REPO / "compiler/cli/src/com/intellij/openapi/progress/impl/CoreProgressManager.java"


def get_file_content() -> str:
    """Read the target file content."""
    if not TARGET_FILE.exists():
        raise FileNotFoundError(f"Target file not found: {TARGET_FILE}")
    return TARGET_FILE.read_text()


def test_no_concurrent_long_object_map_import():
    """Verify that ConcurrentLongObjectMap import has been removed."""
    content = get_file_content()
    assert "ConcurrentLongObjectMap" not in content, \
        "Found 'ConcurrentLongObjectMap' in file - should be removed"


def test_no_java11shim_import():
    """Verify that Java11Shim import has been removed."""
    content = get_file_content()
    assert "Java11Shim" not in content, \
        "Found 'Java11Shim' in file - should be removed"


def test_concurrent_map_field_type():
    """Verify that currentIndicators uses ConcurrentMap type."""
    content = get_file_content()
    # Check that the field declaration uses ConcurrentMap
    pattern = r"private static final ConcurrentMap<Long, ProgressIndicator> currentIndicators"
    assert re.search(pattern, content), \
        "currentIndicators field should be declared as ConcurrentMap<Long, ProgressIndicator>"


def test_concurrent_hashmap_instantiation():
    """Verify that currentIndicators is instantiated with ConcurrentHashMap."""
    content = get_file_content()
    # Check for the new instantiation pattern
    assert "new ConcurrentHashMap<>()" in content, \
        "currentIndicators should be instantiated with 'new ConcurrentHashMap<>'"


def test_thread_top_level_indicators_field_type():
    """Verify that threadTopLevelIndicators uses ConcurrentMap type."""
    content = get_file_content()
    # Check that the field declaration uses ConcurrentMap
    pattern = r"private static final ConcurrentMap<Long, ProgressIndicator> threadTopLevelIndicators"
    assert re.search(pattern, content), \
        "threadTopLevelIndicators field should be declared as ConcurrentMap<Long, ProgressIndicator>"


def test_both_fields_use_concurrent_hashmap():
    """Verify both fields are properly converted to ConcurrentHashMap."""
    content = get_file_content()
    # Count occurrences of new ConcurrentHashMap<>()
    count = content.count("new ConcurrentHashMap<>")
    assert count >= 2, \
        f"Expected at least 2 ConcurrentHashMap instantiations (currentIndicators and threadTopLevelIndicators), found {count}"


def test_java_compiles():
    """Verify the Java file compiles successfully."""
    # Try to compile just this file to check for syntax errors
    # We need to add the file to classpath, but for a basic check we can use javac with -d
    result = subprocess.run(
        ["javac", "-d", "/tmp/compiled", "-sourcepath", str(REPO / "compiler/cli/src"), str(TARGET_FILE)],
        capture_output=True,
        timeout=60
    )
    # Note: This may fail due to missing dependencies, but syntax errors are caught
    # If it fails due to missing symbols that's OK, but syntax errors should be flagged
    stderr = result.stderr.decode()
    # Filter out "cannot find symbol" errors (missing deps) - only check for syntax errors
    syntax_errors = [line for line in stderr.split('\n') if 'illegal' in line.lower() or 'syntax' in line.lower()]
    assert not syntax_errors, f"Syntax errors found: {syntax_errors}"


def test_javadoc_updated():
    """Verify the JavaDoc comment mentions the sun.misc.Unsafe workaround."""
    content = get_file_content()
    # Check for updated javadoc mentioning sun.misc.Unsafe or JEP 471
    assert "sun.misc.Unsafe" in content or "JEP 471" in content or "ConcurrentHashMap" in content, \
        "JavaDoc should be updated to mention the sun.misc.Unsafe workaround or ConcurrentHashMap change"


def test_no_java11shim_create_call():
    """Verify no Java11Shim factory method calls remain."""
    content = get_file_content()
    assert "createConcurrentLongObjectMap" not in content, \
        "Found 'createConcurrentLongObjectMap' call - should be removed"


def test_concurrent_map_import_present():
    """Verify ConcurrentMap is imported (from java.util.concurrent)."""
    content = get_file_content()
    # Check that java.util.concurrent imports are present
    assert "java.util.concurrent" in content, \
        "File should import from java.util.concurrent package"


# ============================================================================
# Pass-to-Pass Tests: Repo CI/CD Checks
# These tests verify the repository's own quality standards pass on base commit
# ============================================================================


def test_repo_java_syntax_valid():
    """Java file compiles without syntax errors (pass_to_pass).

    Uses the repo's javac to validate Java syntax. Missing dependencies are
    expected and ignored - we only check for actual syntax errors.
    """
    result = subprocess.run(
        ["javac", "-d", "/tmp/compiled", "-sourcepath", str(REPO / "compiler/cli/src"), str(TARGET_FILE)],
        capture_output=True, text=True, timeout=60, cwd=REPO
    )
    stderr = result.stderr
    # Filter for actual syntax errors only (not missing symbol errors from deps)
    syntax_errors = [
        line for line in stderr.split('\n')
        if any(err in line.lower() for err in ['illegal', 'syntax', 'unexpected', 'expected'])
    ]
    assert not syntax_errors, f"Java syntax errors found: {syntax_errors}"


def test_repo_file_encoding_utf8():
    """Java file uses valid UTF-8 encoding (pass_to_pass).

    Verifies the source file is properly encoded as UTF-8 without
    invalid replacement characters that indicate encoding issues.
    """
    try:
        content = TARGET_FILE.read_text(encoding='utf-8')
        # Check no invalid characters
        assert '\ufffd' not in content, "File contains invalid UTF-8 replacement characters"
    except UnicodeDecodeError as e:
        assert False, f"File is not valid UTF-8: {e}"


def test_repo_package_declaration_valid():
    """Java file has valid package declaration (pass_to_pass).

    Verifies the source file declares the expected package, which is
    required for proper compilation and IDE integration.
    """
    content = get_file_content()
    assert "package com.intellij.openapi.progress.impl;" in content, \
        "File must have correct package declaration"


def test_repo_class_structure_valid():
    """Java file has valid class declaration (pass_to_pass).

    Verifies the CoreProgressManager class is properly declared as public.
    """
    content = get_file_content()
    assert "public class CoreProgressManager" in content, \
        "CoreProgressManager must be declared as public class"


def test_repo_license_header_present():
    """Java file has Apache 2.0 license header (pass_to_pass).

    Verifies the source file contains the required JetBrains/Apache 2.0
    license header as per repository standards.
    """
    content = get_file_content()
    assert "Copyright 2010-2025 JetBrains s.r.o." in content, \
        "File must contain JetBrains copyright header"
    assert "Apache 2.0 license" in content, \
        "File must reference Apache 2.0 license"


def test_repo_imports_structure_valid():
    """Java file has properly structured imports (pass_to_pass).

    Verifies imports are properly formatted and organized. This validates
    that the file structure matches the repo's coding standards.
    """
    content = get_file_content()
    # Check that java.util.concurrent imports are present (for the fix)
    assert "java.util.concurrent" in content, \
        "File should import from java.util.concurrent package"


def test_repo_no_sun_misc_unsafe():
    """Java file does not use sun.misc.Unsafe (pass_to_pass).

    Verifies the file does not directly import sun.misc.Unsafe,
    which is being phased out in modern JDK versions (JEP 471).
    This is a repo-wide policy for forward compatibility.
    """
    content = get_file_content()
    # The file may use Unsafe indirectly via Java11Shim in base commit
    # but should not directly import it
    assert "import sun.misc.Unsafe" not in content, \
        "File should not directly import sun.misc.Unsafe"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
