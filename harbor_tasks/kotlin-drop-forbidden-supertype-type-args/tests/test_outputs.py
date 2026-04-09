#!/usr/bin/env python3
"""
Test script for Kotlin PR #5737: Drop ForbidUsingSupertypesWithInaccessibleContentInTypeArguments

This tests that the language feature is properly removed from:
1. LanguageVersionSettings.kt - enum entry removed
2. FirMissingDependencyStorage.kt - TypeWithOrigin and SupertypeOrigin removed
3. FirMissingDependencySupertypeUtils.kt - TYPE_ARGUMENT origin check removed
4. Test data files updated to remove feature flags
"""

import subprocess
import re
import os

REPO = "/workspace/kotlin"


def test_language_feature_removed():
    """Fail-to-pass: LanguageFeature.ForbidUsingSupertypesWithInaccessibleContentInTypeArguments must be removed"""
    settings_file = f"{REPO}/core/language.version-settings/src/org/jetbrains/kotlin/config/LanguageVersionSettings.kt"
    with open(settings_file, 'r') as f:
        content = f.read()

    # The feature should NOT exist anymore
    assert "ForbidUsingSupertypesWithInaccessibleContentInTypeArguments" not in content, \
        "LanguageFeature.ForbidUsingSupertypesWithInaccessibleContentInTypeArguments still exists in LanguageVersionSettings.kt"


def test_api_file_updated():
    """Fail-to-pass: API file must not contain the removed feature"""
    api_file = f"{REPO}/core/language.version-settings/api/language.version-settings.api"
    with open(api_file, 'r') as f:
        content = f.read()

    # The feature should NOT exist in the API file
    assert "ForbidUsingSupertypesWithInaccessibleContentInTypeArguments" not in content, \
        "API file still contains ForbidUsingSupertypesWithInaccessibleContentInTypeArguments"


def test_type_with_origin_removed():
    """Fail-to-pass: TypeWithOrigin data class must be removed from FirMissingDependencyStorage"""
    storage_file = f"{REPO}/compiler/fir/providers/src/org/jetbrains/kotlin/fir/types/FirMissingDependencyStorage.kt"
    with open(storage_file, 'r') as f:
        content = f.read()

    # TypeWithOrigin class should NOT exist
    assert "data class TypeWithOrigin" not in content, \
        "TypeWithOrigin data class still exists"
    assert "TypeWithOrigin" not in content, \
        "TypeWithOrigin reference still exists in FirMissingDependencyStorage.kt"


def test_supertype_origin_enum_removed():
    """Fail-to-pass: SupertypeOrigin enum must be removed"""
    storage_file = f"{REPO}/compiler/fir/providers/src/org/jetbrains/kotlin/fir/types/FirMissingDependencyStorage.kt"
    with open(storage_file, 'r') as f:
        content = f.read()

    # SupertypeOrigin enum should NOT exist
    assert "enum class SupertypeOrigin" not in content, \
        "SupertypeOrigin enum still exists"
    assert "SupertypeOrigin.TYPE_ARGUMENT" not in content, \
        "SupertypeOrigin.TYPE_ARGUMENT still referenced"
    assert "SupertypeOrigin.OTHER" not in content, \
        "SupertypeOrigin.OTHER still referenced"


def test_storage_uses_cone_kotlin_type_directly():
    """Fail-to-pass: getMissingSuperTypes should return Set<ConeKotlinType> directly"""
    storage_file = f"{REPO}/compiler/fir/providers/src/org/jetbrains/kotlin/fir/types/FirMissingDependencyStorage.kt"
    with open(storage_file, 'r') as f:
        content = f.read()

    # The return type should be Set<ConeKotlinType>, not Set<TypeWithOrigin>
    assert "Set<ConeKotlinType>" in content, \
        "getMissingSuperTypes should return Set<ConeKotlinType>"

    # Check the function signature
    match = re.search(r'fun getMissingSuperTypes\([^)]*\):\s*(\S+)', content)
    if match:
        return_type = match.group(1)
        assert "ConeKotlinType" in return_type, \
            f"getMissingSuperTypes return type should be ConeKotlinType, got: {return_type}"


def test_checker_simplified():
    """Fail-to-pass: FirMissingDependencySupertypeUtils must not check TYPE_ARGUMENT origin"""
    checker_file = f"{REPO}/compiler/fir/checkers/src/org/jetbrains/kotlin/fir/analysis/checkers/FirMissingDependencySupertypeUtils.kt"
    with open(checker_file, 'r') as f:
        content = f.read()

    # Should NOT check for TYPE_ARGUMENT origin anymore
    assert "SupertypeOrigin.TYPE_ARGUMENT" not in content, \
        "SupertypeOrigin.TYPE_ARGUMENT check still exists in checker"

    # Should NOT emit MISSING_DEPENDENCY_SUPERCLASS_IN_TYPE_ARGUMENT anymore
    assert "MISSING_DEPENDENCY_SUPERCLASS_IN_TYPE_ARGUMENT" not in content, \
        "MISSING_DEPENDENCY_SUPERCLASS_IN_TYPE_ARGUMENT diagnostic still emitted"

    # The iteration should be simplified: for (superType in missingSuperTypes)
    assert "for (superType in missingSuperTypes)" in content, \
        "Missing simplified iteration pattern 'for (superType in missingSuperTypes)'"


def test_collect_super_types_simplified():
    """Fail-to-pass: collectSuperTypes should not track origin parameter"""
    storage_file = f"{REPO}/compiler/fir/providers/src/org/jetbrains/kotlin/fir/types/FirMissingDependencyStorage.kt"
    with open(storage_file, 'r') as f:
        content = f.read()

    # collect function should not take origin parameter
    func_pattern = r'fun collect\([^)]*\)'
    match = re.search(func_pattern, content)
    if match:
        func_sig = match.group(0)
        assert "origin" not in func_sig, \
            f"collect function should not have origin parameter: {func_sig}"


def test_no_missing_dependency_superclass_in_type_argument_anywhere():
    """Fail-to-pass: MISSING_DEPENDENCY_SUPERCLASS_IN_TYPE_ARGUMENT should not exist anywhere in codebase"""
    # Search for any remaining references to this diagnostic in the checker
    checker_file = f"{REPO}/compiler/fir/checkers/src/org/jetbrains/kotlin/fir/analysis/checkers/FirMissingDependencySupertypeUtils.kt"
    with open(checker_file, 'r') as f:
        content = f.read()
    assert "MISSING_DEPENDENCY_SUPERCLASS_IN_TYPE_ARGUMENT" not in content, \
        "MISSING_DEPENDENCY_SUPERCLASS_IN_TYPE_ARGUMENT still exists in checker code"


def test_storage_no_type_with_origin_references():
    """Fail-to-pass: TypeWithOrigin should not be referenced anywhere in storage"""
    storage_file = f"{REPO}/compiler/fir/providers/src/org/jetbrains/kotlin/fir/types/FirMissingDependencyStorage.kt"
    with open(storage_file, 'r') as f:
        content = f.read()

    # Check that all references to TypeWithOrigin are gone
    assert "TypeWithOrigin" not in content, \
        "TypeWithOrigin still referenced in FirMissingDependencyStorage.kt"


def test_code_simplifications_correct():
    """Fail-to-pass: Verify all code simplifications are correctly applied"""
    # Check FirMissingDependencyStorage has simplified iteration
    storage_file = f"{REPO}/compiler/fir/providers/src/org/jetbrains/kotlin/fir/types/FirMissingDependencyStorage.kt"
    with open(storage_file, 'r') as f:
        content = f.read()

    # Should have for (superTypeRef in symbol.resolvedSuperTypeRefs) without origin tracking
    assert "result.add(superType)" in content, \
        "Simplified result.add(superType) not found - origin tracking still present"

    # Check filterTo uses simple predicate without destructuring
    assert "filterTo(mutableSetOf()) { type ->" in content, \
        "Simplified filterTo with type parameter not found"


def test_supertype_origin_completely_removed():
    """Fail-to-pass: SupertypeOrigin enum and all references removed"""
    # Check both storage and checker files
    storage_file = f"{REPO}/compiler/fir/providers/src/org/jetbrains/kotlin/fir/types/FirMissingDependencyStorage.kt"
    checker_file = f"{REPO}/compiler/fir/checkers/src/org/jetbrains/kotlin/fir/analysis/checkers/FirMissingDependencySupertypeUtils.kt"

    with open(storage_file, 'r') as f:
        storage_content = f.read()
    with open(checker_file, 'r') as f:
        checker_content = f.read()

    # SupertypeOrigin should not exist in either file
    assert "SupertypeOrigin" not in storage_content, \
        "SupertypeOrigin still referenced in storage"
    assert "SupertypeOrigin" not in checker_content, \
        "SupertypeOrigin still referenced in checker"


def test_test_data_no_feature_flag():
    """Fail-to-pass: Test data files should not contain the feature flag"""
    test_files = [
        "compiler/testData/diagnostics/tests/multimodule/FalsePositiveInaccessibleTypeInDefaultArg.kt",
        "compiler/testData/diagnostics/tests/multimodule/InaccessibleTypeEagerCheck.kt",
        "compiler/testData/diagnostics/tests/multimodule/InaccessibleTypeEagerCheckForbidden.kt",
        "compiler/testData/diagnostics/tests/multimodule/InaccessibleTypeEagerCheckJava.kt",
        "compiler/testData/diagnostics/tests/multimodule/SupertypesWithInaccessibleTypeArguments.kt",
        "compiler/testData/diagnostics/tests/multimodule/inaccessibleSupertypeVariousExperimental.kt",
        "compiler/testData/diagnostics/tests/multimodule/inaccessibleSupertypeVariousExperimentalEnabled.kt",
    ]

    for test_file in test_files:
        full_path = f"{REPO}/{test_file}"
        if os.path.exists(full_path):
            with open(full_path, 'r') as f:
                content = f.read()
            assert "ForbidUsingSupertypesWithInaccessibleContentInTypeArguments" not in content, \
                f"Test file {test_file} still contains feature flag"


def test_supertypes_test_data_no_diagnostic():
    """Fail-to-pass: SupertypesWithInaccessibleTypeArguments.kt should not have MISSING_DEPENDENCY_SUPERCLASS_IN_TYPE_ARGUMENT markers"""
    test_file = f"{REPO}/compiler/testData/diagnostics/tests/multimodule/SupertypesWithInaccessibleTypeArguments.kt"
    if os.path.exists(test_file):
        with open(test_file, 'r') as f:
            content = f.read()

        # Should NOT have the diagnostic marker
        assert "MISSING_DEPENDENCY_SUPERCLASS_IN_TYPE_ARGUMENT" not in content, \
            "SupertypesWithInaccessibleTypeArguments.kt still has MISSING_DEPENDENCY_SUPERCLASS_IN_TYPE_ARGUMENT diagnostic markers"


def test_inaccessible_supertype_test_data_updated():
    """Fail-to-pass: inaccessibleSupertypeVariousExperimental.kt BoxedDependencyInheritor should not have diagnostic"""
    test_file = f"{REPO}/compiler/testData/diagnostics/tests/multimodule/inaccessibleSupertypeVariousExperimental.kt"
    if os.path.exists(test_file):
        with open(test_file, 'r') as f:
            content = f.read()

        # Look for the line with BoxedDependencyInheritor - should NOT have the diagnostic marker
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'BoxedDependencyInheritor()' in line:
                assert 'MISSING_DEPENDENCY_SUPERCLASS_IN_TYPE_ARGUMENT' not in line, \
                    f"BoxedDependencyInheritor() at line {i+1} still has MISSING_DEPENDENCY_SUPERCLASS_IN_TYPE_ARGUMENT diagnostic"
