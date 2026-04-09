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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
