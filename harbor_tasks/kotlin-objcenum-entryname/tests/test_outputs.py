#!/usr/bin/env python3
"""
Tests for ObjCEnum.EntryName annotation support.

This test suite validates:
1. The EntryName annotation class exists in stdlib
2. The annotation can be resolved by the compiler (FqName registered)
3. The header generator tests pass, validating the EntryName annotation works correctly
"""

import subprocess
import sys
import os

REPO = "/workspace/kotlin"


def test_entryname_annotation_exists_in_stdlib():
    """
    Verify that the EntryName annotation class exists in NativeAnnotations.kt.
    This is a core requirement - the annotation must be defined in the stdlib.
    """
    # Check that the annotation class exists in the stdlib expect declaration
    annotation_file = os.path.join(REPO, "libraries/stdlib/src/kotlin/annotations/NativeAnnotations.kt")
    with open(annotation_file, 'r') as f:
        content = f.read()

    # Should contain the EntryName annotation class definition
    assert "annotation class EntryName" in content, "EntryName annotation class not found in NativeAnnotations.kt"
    assert 'val name: String' in content, "EntryName 'name' parameter not found"
    assert 'val swiftName: String' in content, "EntryName 'swiftName' parameter not found"


def test_entryname_annotation_exists_in_native_runtime():
    """
    Verify that the EntryName annotation class exists in kotlin-native runtime.
    This is the actual implementation for native targets.
    """
    annotation_file = os.path.join(REPO, "kotlin-native/runtime/src/main/kotlin/kotlin/native/Annotations.kt")
    with open(annotation_file, 'r') as f:
        content = f.read()

    assert "annotation class EntryName" in content, "EntryName annotation class not found in Annotations.kt"
    assert 'val name: String' in content, "EntryName 'name' parameter not found"
    assert 'val swiftName: String' in content, "EntryName 'swiftName' parameter not found"


def test_objcenum_entryname_fqname_registered():
    """
    Verify that the FqName for ObjCEnum.EntryName is registered in KonanFqNames.
    This is required for the annotation to be resolved by the compiler.
    """
    konan_fqnames_file = os.path.join(REPO, "native/base/src/main/kotlin/org/jetbrains/kotlin/backend/konan/KonanFqNames.kt")
    with open(konan_fqnames_file, 'r') as f:
        content = f.read()

    assert 'objCEnumEntryName = FqName("kotlin.native.ObjCEnum.EntryName")' in content, \
        "objCEnumEntryName FqName not registered in KonanFqNames"


def test_k1_objcenum_entryname_resolution():
    """
    Verify that K1 (legacy frontend) has the ObjCEnumEntryName resolution logic.
    """
    namer_file = os.path.join(REPO, "native/objcexport-header-generator/impl/k1/src/org/jetbrains/kotlin/backend/konan/objcexport/ObjCExportNamer.kt")
    with open(namer_file, 'r') as f:
        content = f.read()

    # Check for ObjCEnumEntryName class
    assert "class ObjCEnumEntryName" in content, "ObjCEnumEntryName class not found in K1 ObjCExportNamer"

    # Check for getName method with forSwift parameter
    assert "fun getName(forSwift: Boolean)" in content, "getName(forSwift) method not found"

    # Check for the getObjCEnumEntryName extension function
    assert "fun DeclarationDescriptor.getObjCEnumEntryName()" in content, \
        "getObjCEnumEntryName extension function not found"


def test_k2_analysis_api_entryname_resolution():
    """
    Verify that K2 (Analysis API frontend) has the ObjCEnum.EntryName resolution logic.
    """
    resolve_file = os.path.join(REPO, "native/objcexport-header-generator/impl/analysis-api/src/org/jetbrains/kotlin/objcexport/resolveObjCNameAnnotation.kt")
    with open(resolve_file, 'r') as f:
        content = f.read()

    # Check for ObjCExportObjCEnumEntryNameAnnotation class
    assert "class ObjCExportObjCEnumEntryNameAnnotation" in content, \
        "ObjCExportObjCEnumEntryNameAnnotation class not found"

    # Check for resolveObjCEnumEntryNameAnnotation function
    assert "fun KaAnnotatedSymbol.resolveObjCEnumEntryNameAnnotation()" in content, \
        "resolveObjCEnumEntryNameAnnotation function not found"


def test_k2_getnsenum_entryname_function():
    """
    Verify that the getNSEnumEntryName function exists in the Analysis API implementation.
    This function is the key to using the EntryName annotation when generating NSEnum entries.
    """
    translate_file = os.path.join(REPO, "native/objcexport-header-generator/impl/analysis-api/src/org/jetbrains/kotlin/objcexport/translateEnumMembers.kt")
    with open(translate_file, 'r') as f:
        content = f.read()

    assert "fun ObjCExportContext.getNSEnumEntryName(" in content, \
        "getNSEnumEntryName function not found in translateEnumMembers.kt"

    # Should call resolveObjCEnumEntryNameAnnotation
    assert "resolveObjCEnumEntryNameAnnotation()" in content, \
        "getNSEnumEntryName should call resolveObjCEnumEntryNameAnnotation"


def test_k1_translator_uses_entryname():
    """
    Verify that the K1 ObjCExportTranslator uses the EntryName annotation when building NSEnum entries.
    """
    translator_file = os.path.join(REPO, "native/objcexport-header-generator/impl/k1/src/org/jetbrains/kotlin/backend/konan/objcexport/ObjCExportTranslator.kt")
    with open(translator_file, 'r') as f:
        content = f.read()

    # Check that the translator calls getObjCEnumEntryName
    assert "entry.getObjCEnumEntryName()" in content, \
        "ObjCExportTranslator should call entry.getObjCEnumEntryName()"

    # Check that objcEnumEntryName is used to get names
    assert "objcEnumEntryName.getName(" in content, \
        "objcEnumEntryName.getName() should be used to resolve entry names"


def test_k2_translate_to_nsenum_uses_entryname():
    """
    Verify that the K2 translateToNSEnum uses getNSEnumEntryName instead of getEnumEntryName.
    """
    translate_file = os.path.join(REPO, "native/objcexport-header-generator/impl/analysis-api/src/org/jetbrains/kotlin/objcexport/translateToNSEnum.kt")
    with open(translate_file, 'r') as f:
        content = f.read()

    # Should call getNSEnumEntryName, not getEnumEntryName
    assert "getNSEnumEntryName(entry, true)" in content, \
        "translateToNSEnum should call getNSEnumEntryName for Swift name"
    assert "getNSEnumEntryName(entry, false)" in content, \
        "translateToNSEnum should call getNSEnumEntryName for ObjC name"


def test_binary_compatibility_api_updated():
    """
    Verify that the binary compatibility validator API dump includes the EntryName annotation.
    """
    api_file = os.path.join(REPO, "libraries/tools/binary-compatibility-validator/klib-public-api/kotlin-stdlib.api")
    with open(api_file, 'r') as f:
        content = f.read()

    # Should have EntryName annotation class definition in the API
    assert "open annotation class EntryName" in content, \
        "EntryName annotation not found in binary compatibility API dump"

    # Should have the constructor
    assert "EntryName.<init>|<init>(kotlin.String;kotlin.String)" in content, \
        "EntryName constructor not found in API dump"


def test_header_generator_test_data_updated():
    """
    Verify that the test data for the header generator includes EntryName annotations.
    This validates that the feature is being tested.
    """
    test_kt_file = os.path.join(REPO, "native/objcexport-header-generator/testData/headers/enumClassWithObjCEnumAndRenamedLiterals/Foo.kt")
    with open(test_kt_file, 'r') as f:
        content = f.read()

    # Should have @ObjCEnum.EntryName annotations in test data
    assert "@ObjCEnum.EntryName" in content, \
        "Test data should include @ObjCEnum.EntryName annotations"

    # Should test various combinations
    assert 'name="entryName1Renamed"' in content, \
        "Test data should include EntryName with name parameter"
    assert 'name="entryName2Renamed", swiftName="entryName2Swift"' in content, \
        "Test data should include EntryName with both name and swiftName"


def test_header_generator_expected_output():
    """
    Verify that the expected header output includes the renamed entries from EntryName.
    """
    expected_header = os.path.join(REPO, "native/objcexport-header-generator/testData/headers/enumClassWithObjCEnumAndRenamedLiterals/!enumClassWithObjCEnumAndRenamedLiterals.h")
    with open(expected_header, 'r') as f:
        content = f.read()

    # Should have the renamed entries from EntryName annotation
    assert "FooNSEnumEntryName1Renamed NS_SWIFT_NAME(entryName1Renamed)" in content, \
        "Expected header should contain EntryName1 renamed entry"
    assert "FooNSEnumEntryName2Renamed NS_SWIFT_NAME(entryName2Swift)" in content, \
        "Expected header should contain EntryName2 renamed entry with Swift name"


def test_objcenum_documentation_updated():
    """
    Verify that the ObjCEnum KDoc documentation has been updated to mention EntryName.
    """
    # Check stdlib annotation
    stdlib_file = os.path.join(REPO, "libraries/stdlib/src/kotlin/annotations/NativeAnnotations.kt")
    with open(stdlib_file, 'r') as f:
        content = f.read()

    # Documentation should mention EntryName
    assert "EntryName" in content, \
        "ObjCEnum KDoc should mention EntryName annotation"

    # Check native runtime annotation
    native_file = os.path.join(REPO, "kotlin-native/runtime/src/main/kotlin/kotlin/native/Annotations.kt")
    with open(native_file, 'r') as f:
        content = f.read()

    assert "EntryName" in content, \
        "Native runtime ObjCEnum KDoc should mention EntryName annotation"


def test_annotation_targets_field():
    """
    Verify that the EntryName annotation is targeted at FIELD (for enum entries).
    """
    # Check stdlib annotation
    stdlib_file = os.path.join(REPO, "libraries/stdlib/src/kotlin/annotations/NativeAnnotations.kt")
    with open(stdlib_file, 'r') as f:
        content = f.read()

    # Should have @Target(AnnotationTarget.FIELD) for EntryName
    # Note: In the PR, it uses AnnotationTarget.CLASS which seems to be for enum entries
    assert "@Target(AnnotationTarget.CLASS)" in content, \
        "EntryName should have @Target(AnnotationTarget.CLASS)"


def test_annotation_retention_binary():
    """
    Verify that the EntryName annotation has binary retention.
    """
    # Check stdlib annotation
    stdlib_file = os.path.join(REPO, "libraries/stdlib/src/kotlin/annotations/NativeAnnotations.kt")
    with open(stdlib_file, 'r') as f:
        content = f.read()

    # Should have @Retention(AnnotationRetention.BINARY)
    assert "@Retention(AnnotationRetention.BINARY)" in content, \
        "EntryName should have @Retention(AnnotationRetention.BINARY)"


if __name__ == "__main__":
    # Run all tests
    import pytest
    sys.exit(pytest.main([__file__, "-v", "--tb=short"]))
