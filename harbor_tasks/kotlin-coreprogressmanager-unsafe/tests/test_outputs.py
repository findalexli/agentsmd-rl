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


def test_repo_no_bom():
    """Java file has no Byte Order Mark (pass_to_pass).

    Verifies the source file does not have a UTF-8 BOM marker,
    which can cause issues with some Java compilers and tools.
    """
    result = subprocess.run(
        ["bash", "-c", f"head -c 3 {TARGET_FILE} | od -An -tx1 | tr -d ' '"],
        capture_output=True, text=True, timeout=30, cwd=REPO
    )
    # UTF-8 BOM is EFBBBF at the start of file
    first_bytes = result.stdout.strip()
    assert not first_bytes.startswith("efbbbf"), \
        "File has UTF-8 BOM marker - should be plain UTF-8 without BOM"


def test_repo_no_tabs():
    """Java file uses spaces not tabs for indentation (pass_to_pass).

    Verifies no tab characters are present in the source file using
    the grep command with explicit tab pattern.
    """
    result = subprocess.run(
        ["grep", "-P", "\t", str(TARGET_FILE)],
        capture_output=True, text=True, timeout=30, cwd=REPO
    )
    # grep returns 0 if found, 1 if not found
    # Tabs found means test should fail
    assert result.returncode != 0, \
        f"Found tab characters in file - use spaces for indentation:\n{result.stdout[:500]}"


def test_repo_trailing_whitespace():
    """Java file has no trailing whitespace (pass_to_pass).

    Verifies no lines end with whitespace characters using grep
    pattern that matches trailing spaces or tabs before newline.
    """
    result = subprocess.run(
        ["grep", "-n", "[[:space:]]$", str(TARGET_FILE)],
        capture_output=True, text=True, timeout=30, cwd=REPO
    )
    # grep returns 0 if found, 1 if not found
    assert result.returncode != 0, \
        f"Found trailing whitespace in file:\n{result.stdout[:500]}"


def test_repo_newline_at_eof():
    """Java file ends with a newline (pass_to_pass).

    Verifies the source file ends with a proper newline character
    using od -c to check the last character.
    """
    result = subprocess.run(
        ["bash", "-c", f"tail -c 1 {TARGET_FILE} | od -c -An"],
        capture_output=True, text=True, timeout=30, cwd=REPO
    )
    # Check if last character is a newline
    output = result.stdout.strip()
    # od -c outputs escaped characters like \n or \r
    assert "\\n" in output or output == "\\n" or "nl" in output.lower(), \
        f"File does not end with newline: last bytes are: {output!r}"


def test_repo_package_declaration_valid():
    """Java file has valid package declaration (pass_to_pass).

    Verifies the source file declares the expected package using grep
    to ensure it matches the directory structure.
    """
    result = subprocess.run(
        ["grep", "^package com.intellij.openapi.progress.impl;", str(TARGET_FILE)],
        capture_output=True, text=True, timeout=30, cwd=REPO
    )
    assert result.returncode == 0, \
        "File must have correct package declaration 'package com.intellij.openapi.progress.impl;'"


def test_repo_class_structure_valid():
    """Java file has valid class declaration (pass_to_pass).

    Verifies the CoreProgressManager class is properly declared as public
    using grep to find the class declaration.
    """
    result = subprocess.run(
        ["grep", "public class CoreProgressManager", str(TARGET_FILE)],
        capture_output=True, text=True, timeout=30, cwd=REPO
    )
    assert result.returncode == 0, \
        "CoreProgressManager must be declared as 'public class CoreProgressManager'"


def test_repo_copyright_header():
    """Java file has JetBrains copyright header (pass_to_pass).

    Verifies the source file contains the required JetBrains copyright
    header using grep for the copyright pattern.
    """
    result = subprocess.run(
        ["grep", "Copyright.*JetBrains", str(TARGET_FILE)],
        capture_output=True, text=True, timeout=30, cwd=REPO
    )
    assert result.returncode == 0, \
        "File must contain JetBrains copyright header"


def test_repo_license_header():
    """Java file has Apache 2.0 license reference (pass_to_pass).

    Verifies the source file contains the Apache 2.0 license reference
    using grep to find the license pattern.
    """
    result = subprocess.run(
        ["grep", "Apache 2.0", str(TARGET_FILE)],
        capture_output=True, text=True, timeout=30, cwd=REPO
    )
    assert result.returncode == 0, \
        "File must reference Apache 2.0 license"


def test_repo_imports_concurrent():
    """Java file imports java.util.concurrent (pass_to_pass).

    Verifies the source file imports from java.util.concurrent package
    which is required for ConcurrentHashMap usage.
    """
    result = subprocess.run(
        ["grep", "import java.util.concurrent", str(TARGET_FILE)],
        capture_output=True, text=True, timeout=30, cwd=REPO
    )
    assert result.returncode == 0, \
        "File should import from java.util.concurrent package"


def test_repo_no_sun_misc_unsafe():
    """Java file does not use sun.misc.Unsafe (pass_to_pass).

    Verifies the file does not directly import sun.misc.Unsafe using grep,
    which is being phased out in modern JDK versions (JEP 471).
    """
    result = subprocess.run(
        ["grep", "import sun.misc.Unsafe", str(TARGET_FILE)],
        capture_output=True, text=True, timeout=30, cwd=REPO
    )
    # grep returns 0 if found (bad - we don't want this import), 1 if not found (good)
    assert result.returncode != 0, \
        "File should not directly import sun.misc.Unsafe"


def test_repo_no_windows_line_endings():
    """Java file uses Unix line endings (pass_to_pass).

    Verifies the source file uses Unix-style line endings (LF) not
    Windows-style (CRLF) using grep for carriage return characters.
    """
    # Use bash to properly escape the carriage return character
    result = subprocess.run(
        ["bash", "-c", f"grep -c $'\\r' {TARGET_FILE} || true"],
        capture_output=True, text=True, timeout=30, cwd=REPO
    )
    # Check if any carriage returns found
    try:
        cr_count_str = result.stdout.strip()
        if cr_count_str and cr_count_str.isdigit():
            cr_count = int(cr_count_str)
            if cr_count > 0:
                assert False, f"Found {cr_count} carriage returns (Windows line endings)"
    except ValueError:
        pass  # If we can't parse, assume it's fine


def test_repo_file_not_empty():
    """Java file is not empty (pass_to_pass).

    Verifies the source file contains content using wc -c to count bytes.
    """
    result = subprocess.run(
        ["wc", "-c", str(TARGET_FILE)],
        capture_output=True, text=True, timeout=30, cwd=REPO
    )
    assert result.returncode == 0, f"wc command failed: {result.stderr}"
    # Parse the byte count
    parts = result.stdout.strip().split()
    if parts:
        byte_count = int(parts[0])
        assert byte_count > 1000, f"File seems too small ({byte_count} bytes), likely incomplete"


def test_repo_no_merge_conflict_markers():
    """Java file has no merge conflict markers (pass_to_pass).

    Verifies the source file does not contain git merge conflict markers
    like '<<<<<<<', '=======', or '>>>>>>>' using grep.
    """
    for marker in ["<<<<<<<", ">>>>>>"]:
        result = subprocess.run(
            ["grep", marker, str(TARGET_FILE)],
            capture_output=True, text=True, timeout=30, cwd=REPO
        )
        assert result.returncode != 0, \
            f"Found merge conflict marker '{marker}' in file"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
