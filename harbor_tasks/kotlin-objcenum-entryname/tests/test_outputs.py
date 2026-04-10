#!/usr/bin/env python3
"""
Tests for ObjCEnum.EntryName annotation support.
"""

import subprocess
import sys
import os

REPO = "/workspace/kotlin"

def test_objcenum_entryname_compilation_and_behavior():
    """
    Compiles and runs a test verifying the new EntryName API.
    Injects a test file into the native/objcexport-header-generator test suite
    to ensure that the code compiles (verifying KonanFqNames) and executes
    correctly (verifying ObjCEnumEntryName logic).
    """
    test_file_path = os.path.join(REPO, "native/objcexport-header-generator/test/org/jetbrains/kotlin/backend/konan/tests/AgentBehaviorTest.kt")
    
    kotlin_code = """
package org.jetbrains.kotlin.backend.konan.tests

import org.jetbrains.kotlin.backend.konan.KonanFqNames
import org.jetbrains.kotlin.backend.konan.objcexport.ObjCEnumEntryName
import org.junit.jupiter.api.Test
import kotlin.test.assertEquals
import kotlin.test.assertNull

class AgentBehaviorTest {
    @Test
    fun testEntryNameExists() {
        val fqName = KonanFqNames.objCEnumEntryName
        assertEquals("kotlin.native.ObjCEnum.EntryName", fqName.asString())
    }

    @Test
    fun testEntryNameResolution() {
        val entry = ObjCEnumEntryName("objc", "swift")
        assertEquals("swift", entry.getName(true))
        assertEquals("objc", entry.getName(false))
        
        val entryEmpty = ObjCEnumEntryName("", "")
        assertNull(entryEmpty.getName(true))
        assertNull(entryEmpty.getName(false))
    }
}
"""
    try:
        with open(test_file_path, "w") as f:
            f.write(kotlin_code)
            
        r = subprocess.run(
            ["./gradlew", ":native:objcexport-header-generator:test", "--tests", "*AgentBehaviorTest*"],
            cwd=REPO, capture_output=True, text=True, timeout=600
        )
        assert r.returncode == 0, f"Compilation or test failed:\n{r.stderr}\n{r.stdout}"
    finally:
        if os.path.exists(test_file_path):
            os.remove(test_file_path)

def test_repo_tests_pass():
    """
    Repo's own test suite passes (pass_to_pass gate).
    Runs the header generator tests to ensure we haven't broken existing functionality.
    """
    r = subprocess.run(
        ["./gradlew", ":native:objcexport-header-generator:test", "--tests", "*ObjCExportHeaderGeneratorTest*"],
        cwd=REPO, capture_output=True, text=True, timeout=600
    )
    assert r.returncode == 0, f"Repo tests failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"

def test_binary_compatibility_api_updated():
    """Verify that the binary compatibility validator API dump includes the EntryName annotation."""
    api_file = os.path.join(REPO, "libraries/tools/binary-compatibility-validator/klib-public-api/kotlin-stdlib.api")
    with open(api_file, 'r') as f:
        content = f.read()

    assert "open annotation class EntryName" in content, "EntryName annotation not found in binary compatibility API dump"
    assert "EntryName.<init>|<init>(kotlin.String;kotlin.String)" in content, "EntryName constructor not found in API dump"

def test_objcenum_documentation_updated():
    """Verify that the ObjCEnum KDoc documentation has been updated to mention EntryName."""
    stdlib_file = os.path.join(REPO, "libraries/stdlib/src/kotlin/annotations/NativeAnnotations.kt")
    with open(stdlib_file, 'r') as f:
        content = f.read()
    assert "EntryName" in content, "ObjCEnum KDoc should mention EntryName annotation"

def test_annotation_targets_field():
    """Verify that the EntryName annotation is targeted at CLASS (for enum entries)."""
    stdlib_file = os.path.join(REPO, "libraries/stdlib/src/kotlin/annotations/NativeAnnotations.kt")
    with open(stdlib_file, 'r') as f:
        content = f.read()
    assert "@Target(AnnotationTarget.CLASS)" in content, "EntryName should have @Target(AnnotationTarget.CLASS)"

def test_annotation_retention_binary():
    """Verify that the EntryName annotation has binary retention."""
    stdlib_file = os.path.join(REPO, "libraries/stdlib/src/kotlin/annotations/NativeAnnotations.kt")
    with open(stdlib_file, 'r') as f:
        content = f.read()
    assert "@Retention(AnnotationRetention.BINARY)" in content, "EntryName should have @Retention(AnnotationRetention.BINARY)"

if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v", "--tb=short"]))
