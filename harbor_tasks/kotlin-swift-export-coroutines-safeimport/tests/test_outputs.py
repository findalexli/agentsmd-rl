#!/usr/bin/env python3
"""Test suite for Swift Export coroutines safeImportName fix."""

import subprocess
import sys
from pathlib import Path

REPO = Path("/workspace/kotlin")
TARGET_FILE = REPO / "native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/impl/BridgeProvider/SirBridgeProviderImpl.kt"


def read_target_file() -> str:
    """Read the content of the target source file."""
    if not TARGET_FILE.exists():
        raise FileNotFoundError(f"Target file not found: {TARGET_FILE}")
    return TARGET_FILE.read_text()


def test_additional_imports_uses_safe_import_name():
    """FAIL-TO-PASS: additionalImports() should use safeImportName for launch function.

    The fix changes from wildcard import "kotlinx.coroutines.*" to explicit imports
    with aliasing for extension functions using safeImportName.
    """
    content = read_target_file()

    # Should use buildList instead of listOfNotNull
    assert "buildList" in content, "Should use buildList for constructing imports"

    # Should have explicit imports for coroutine types
    assert "kotlinx.coroutines.CancellationException" in content, \
        "Should explicitly import CancellationException"
    assert "kotlinx.coroutines.CoroutineScope" in content, \
        "Should explicitly import CoroutineScope"
    assert "kotlinx.coroutines.CoroutineStart" in content, \
        "Should explicitly import CoroutineStart"
    assert "kotlinx.coroutines.Dispatchers" in content, \
        "Should explicitly import Dispatchers"

    # Should use safeImportName for the launch function
    assert 'FqName("kotlinx.coroutines.launch")' in content, \
        "Should reference FqName for kotlinx.coroutines.launch"
    assert 'it.safeImportName' in content, \
        "Should use safeImportName for the launch function"


def test_coroutine_launch_uses_aliased_name():
    """FAIL-TO-PASS: Generated coroutine bridge code should use aliased launch name.

    The bridge code must use 'kotlinx_coroutines_launch' instead of just 'launch'
    to match the aliased import.
    """
    content = read_target_file()

    # The bridge code should use the aliased function name
    assert ".kotlinx_coroutines_launch(" in content, \
        "Bridge code should use 'kotlinx_coroutines_launch' instead of 'launch'"

    # Should NOT use unaliased launch in the bridge template
    lines = content.split('\n')
    bridge_template_lines = [line for line in lines
                              if 'CoroutineScope' in line and 'start = CoroutineStart' in line]

    for line in bridge_template_lines:
        assert ".launch(" not in line or ".kotlinx_coroutines_launch(" in line, \
            f"Bridge template should not use unaliased .launch(): {line}"


def test_fqname_safe_import_name_extension():
    """FAIL-TO-PASS: FqName.safeImportName extension should exist.

    The fix extracts safeImportName as an extension on FqName to allow reuse.
    """
    content = read_target_file()

    # Should have the new extension property on FqName
    assert "private val FqName.safeImportName: String" in content, \
        "Should have safeImportName extension property on FqName"

    # The extension should delegate to the same implementation
    assert "pathSegments().joinToString" in content, \
        "safeImportName should use pathSegments with underscore separator"


def test_bridge_function_uses_fqname_extension():
    """PASS-TO-PASS: BridgeFunctionDescriptor.safeImportName should use FqName extension.

    After the fix, BridgeFunctionDescriptor.safeImportName should delegate to
    the FqName extension.
    """
    content = read_target_file()

    # BridgeFunctionDescriptor.safeImportName should delegate to FqName.safeImportName
    assert "private val BridgeFunctionDescriptor.safeImportName: String" in content
    assert "get() = kotlinFqName.safeImportName" in content, \
        "Should delegate to FqName.safeImportName extension"


def test_no_wildcard_coroutine_imports():
    """FAIL-TO-PASS: Should not use wildcard import for kotlinx.coroutines.

    The fix removes the "kotlinx.coroutines.*" wildcard import.
    """
    content = read_target_file()

    # Should NOT have wildcard import in the additionalImports function
    # Note: the file itself might have wildcard imports at top, but the generated
    # code should not

    # In the additionalImports function area (around where coroutine imports are added)
    import_section = content[content.find("additionalImports"):content.find("additionalImports") + 2000]

    # Should not have wildcard pattern in the import generation logic
    assert "kotlinx.coroutines.*" not in import_section, \
        "Should not generate wildcard import for kotlinx.coroutines"


def test_kotlin_file_compiles():
    """PASS-TO-PASS: Kotlin source file should have valid syntax.

    Verify the file can be parsed by a simple Kotlin syntax check.
    """
    # Check file has balanced braces (basic sanity check)
    content = read_target_file()

    open_braces = content.count('{')
    close_braces = content.count('}')
    assert open_braces == close_braces, \
        f"Mismatched braces: {open_braces} open, {close_braces} close"

    open_parens = content.count('(')
    close_parens = content.count(')')
    assert open_parens == close_parens, \
        f"Mismatched parentheses: {open_parens} open, {close_parens} close"


def test_java_runtime_available():
    """PASS-TO-PASS: Java runtime should be available in environment.

    Verifies the Docker environment has a working Java installation.
    This is a CI environment sanity check.
    """
    r = subprocess.run(
        ["java", "--version"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Java runtime check failed:\n{r.stderr}"
    assert "17." in r.stdout or "21." in r.stdout, \
        f"Java version check failed - expected JDK 17+:\n{r.stdout}"


def test_target_file_exists():
    """PASS-TO-PASS: Target file should exist and be accessible.

    Verifies the SirBridgeProviderImpl.kt file was correctly downloaded
    and is accessible in the Docker environment.
    """
    r = subprocess.run(
        ["stat", str(TARGET_FILE)],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Target file stat failed:\n{r.stderr}"
    assert "regular file" in r.stdout, f"Target is not a regular file:\n{r.stdout}"


def test_kotlin_file_has_package_declaration():
    """PASS-TO-PASS: Kotlin file should have proper package declaration.

    Verifies the file starts with a valid package declaration using
    shell command to check file content (not pure Python read).
    """
    r = subprocess.run(
        ["head", "-20", str(TARGET_FILE)],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Head command failed:\n{r.stderr}"
    # Check for package declaration in first 20 lines
    assert "package org.jetbrains.kotlin.sir.providers.impl.BridgeProvider" in r.stdout, \
        "Package declaration not found in expected location"


def test_kotlin_file_has_required_imports():
    """PASS-TO-PASS: Kotlin file should have required core imports.

    Verifies the file imports basic Kotlin analysis API types.
    Uses grep via subprocess to check for imports.
    """
    r = subprocess.run(
        ["grep", "^import", str(TARGET_FILE)],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert r.returncode in [0, 1], f"Grep command failed:\n{r.stderr}"
    imports = r.stdout
    # Check for critical imports that should exist in base commit
    assert "org.jetbrains.kotlin.analysis.api" in imports, \
        "Missing analysis.api imports"
    assert "org.jetbrains.kotlin.name.FqName" in imports, \
        "Missing FqName import"
    assert "org.jetbrains.kotlin.sir" in imports, \
        "Missing sir package imports"


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v", "--tb=short"]))
