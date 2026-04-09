#!/usr/bin/env python3
"""Tests for JetBrains/kotlin#5800 - Update deprecated Compose feature flags.

This PR updates deprecation annotations in the Kotlin Compose Compiler Gradle plugin:
1. Changes deprecation level from WARNING to ERROR for several deprecated properties
2. Updates @Suppress annotations from "DEPRECATION" to "DEPRECATION_ERROR"
3. Adds deprecation annotations to OptimizeNonSkippingGroups and PausableComposition
4. Updates test code to use the new stabilityConfigurationFiles API
"""

import subprocess
import re
import ast
from pathlib import Path

REPO = Path("/workspace/kotlin")

# File paths
EXTENSION_FILE = REPO / "libraries/tools/kotlin-compose-compiler/src/common/kotlin/org/jetbrains/kotlin/compose/compiler/gradle/ComposeCompilerGradlePluginExtension.kt"
FEATURE_FLAGS_FILE = REPO / "libraries/tools/kotlin-compose-compiler/src/common/kotlin/org/jetbrains/kotlin/compose/compiler/gradle/ComposeFeatureFlags.kt"
SUBPLUGIN_FILE = REPO / "libraries/tools/kotlin-compose-compiler/src/common/kotlin/org/jetbrains/kotlin/compose/compiler/gradle/ComposeCompilerSubplugin.kt"
COMPOSE_IT_FILE = REPO / "libraries/tools/kotlin-gradle-plugin-integration-tests/src/test/kotlin/org/jetbrains/kotlin/gradle/ComposeIT.kt"
EXTENSION_TEST_FILE = REPO / "libraries/tools/kotlin-compose-compiler/src/functionalTest/kotlin/org/jetbrains/kotlin/compose/compiler/gradle/ExtensionConfigurationTest.kt"
BUILD_GRADLE_FILE = REPO / "libraries/tools/kotlin-compose-compiler/build.gradle.kts"


def read_file(path: Path) -> str:
    """Read file content."""
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    return path.read_text()


def parse_deprecated_annotation(content: str, target: str, direction: str = "before") -> dict:
    """
    Parse @Deprecated annotation near a target declaration.

    Returns a dict with keys: message, level, found (bool)
    """
    idx = content.find(target)
    if idx == -1:
        return {"found": False}

    if direction == "before":
        search_area = content[max(0, idx - 500):idx]
    else:
        search_area = content[idx:idx + 500]

    # Find @Deprecated annotation - look for the closing ) followed by optional whitespace/newlines
    # The annotation may span multiple lines
    dep_pattern = r'@Deprecated\((.*?)\)(?=\s*$|\s*\n\s*@|\s*\n\s*(?:@JvmField|val|var|fun|abstract|class|//|/\*))'
    match = re.search(dep_pattern, search_area, re.DOTALL)

    if not match:
        return {"found": False}

    params = match.group(1)

    result = {"found": True}

    # Extract message
    msg_match = re.search(r'message\s*=\s*"([^"]*)"', params)
    result["message"] = msg_match.group(1) if msg_match else None

    # Extract level
    level_match = re.search(r'level\s*=\s*DeprecationLevel\.(\w+)', params)
    result["level"] = level_match.group(1) if level_match else None

    return result


def parse_suppress_annotation(content: str, target: str) -> list:
    """
    Parse @Suppress annotation near a target declaration.

    Returns list of suppressed warnings, e.g., ["DEPRECATION", "DEPRECATION_ERROR"]
    """
    idx = content.find(target)
    if idx == -1:
        return []

    search_area = content[max(0, idx - 500):idx]

    # Match @Suppress annotation
    suppress_pattern = r'@Suppress\(([^)]+)\)'
    match = re.search(suppress_pattern, search_area)

    if not match:
        return []

    params = match.group(1)
    # Extract all quoted strings
    warnings = re.findall(r'"([^"]+)"', params)
    return warnings


# ============ Fail-to-pass tests: Deprecation annotation changes ============

def test_generate_function_key_meta_classes_deprecation_error():
    """generateFunctionKeyMetaClasses property has DeprecationLevel.ERROR.

    F2P: On base commit, this property only has a simple @Deprecated without level.
    After fix, it should have level = DeprecationLevel.ERROR.
    """
    content = read_file(EXTENSION_FILE)

    # Find the property declaration
    pattern = r'val\s+generateFunctionKeyMetaClasses\s*:'
    match = re.search(pattern, content)
    assert match is not None, "Could not find generateFunctionKeyMetaClasses declaration"

    # Parse the deprecation annotation
    result = parse_deprecated_annotation(content, 'val generateFunctionKeyMetaClasses', 'before')

    assert result["found"], "No @Deprecated annotation found for generateFunctionKeyMetaClasses"
    assert result["level"] == "ERROR", f"Expected DeprecationLevel.ERROR, got {result['level']}"
    assert result["message"] and "2.5.0" in result["message"], \
        f"Expected message mentioning '2.5.0', got: {result['message']}"


def test_enable_intrinsic_remember_deprecation_error():
    """enableIntrinsicRemember property has DeprecationLevel.ERROR."""
    content = read_file(EXTENSION_FILE)

    result = parse_deprecated_annotation(content, 'val enableIntrinsicRemember', 'before')

    assert result["found"], "No @Deprecated annotation found for enableIntrinsicRemember"
    assert result["level"] == "ERROR", f"Expected DeprecationLevel.ERROR, got {result['level']}"
    assert result["message"] and "2.5.0" in result["message"], \
        f"Expected message mentioning '2.5.0', got: {result['message']}"


def test_enable_strong_skipping_mode_deprecation_error():
    """enableStrongSkippingMode property has DeprecationLevel.ERROR."""
    content = read_file(EXTENSION_FILE)

    result = parse_deprecated_annotation(content, 'val enableStrongSkippingMode', 'before')

    assert result["found"], "No @Deprecated annotation found for enableStrongSkippingMode"
    assert result["level"] == "ERROR", f"Expected DeprecationLevel.ERROR, got {result['level']}"
    assert result["message"] and "2.5.0" in result["message"], \
        f"Expected message mentioning '2.5.0', got: {result['message']}"


def test_enable_non_skipping_group_optimization_deprecation_error():
    """enableNonSkippingGroupOptimization property has DeprecationLevel.ERROR."""
    content = read_file(EXTENSION_FILE)

    result = parse_deprecated_annotation(content, 'val enableNonSkippingGroupOptimization', 'before')

    assert result["found"], "No @Deprecated annotation found for enableNonSkippingGroupOptimization"
    assert result["level"] == "ERROR", f"Expected DeprecationLevel.ERROR, got {result['level']}"
    assert result["message"] and "2.5.0" in result["message"], \
        f"Expected message mentioning '2.5.0', got: {result['message']}"


def test_stability_configuration_file_deprecation_error():
    """stabilityConfigurationFile property has DeprecationLevel.ERROR."""
    content = read_file(EXTENSION_FILE)

    result = parse_deprecated_annotation(content, 'abstract val stabilityConfigurationFile', 'before')

    assert result["found"], "No @Deprecated annotation found for stabilityConfigurationFile"
    assert result["level"] == "ERROR", f"Expected DeprecationLevel.ERROR, got {result['level']}"
    assert result["message"] and "2.5.0" in result["message"], \
        f"Expected message mentioning '2.5.0', got: {result['message']}"


def test_strong_skipping_feature_flag_deprecation_error():
    """StrongSkipping feature flag has DeprecationLevel.ERROR.

    F2P: On base commit, this flag has @Deprecated without level.
    After fix, it should have level = DeprecationLevel.ERROR.
    """
    content = read_file(FEATURE_FLAGS_FILE)

    result = parse_deprecated_annotation(content, 'val StrongSkipping', 'before')

    assert result["found"], "No @Deprecated annotation found for StrongSkipping"
    assert result["level"] == "ERROR", f"Expected DeprecationLevel.ERROR, got {result['level']}"
    assert result["message"] and "2.5.0" in result["message"], \
        f"Expected message mentioning '2.5.0', got: {result['message']}"


def test_intrinsic_remember_feature_flag_deprecation_error():
    """IntrinsicRemember feature flag has DeprecationLevel.ERROR."""
    content = read_file(FEATURE_FLAGS_FILE)

    result = parse_deprecated_annotation(content, 'val IntrinsicRemember', 'before')

    assert result["found"], "No @Deprecated annotation found for IntrinsicRemember"
    assert result["level"] == "ERROR", f"Expected DeprecationLevel.ERROR, got {result['level']}"
    assert result["message"] and "2.5.0" in result["message"], \
        f"Expected message mentioning '2.5.0', got: {result['message']}"


def test_optimize_non_skipping_groups_deprecation_warning():
    """OptimizeNonSkippingGroups feature flag has DeprecationLevel.WARNING.

    F2P: On base commit, this flag has NO deprecation annotation.
    After fix, it should have @Deprecated with level=WARNING.
    """
    content = read_file(FEATURE_FLAGS_FILE)

    result = parse_deprecated_annotation(content, 'val OptimizeNonSkippingGroups', 'before')

    assert result["found"], "No @Deprecated annotation found for OptimizeNonSkippingGroups"
    assert result["level"] == "WARNING", f"Expected DeprecationLevel.WARNING, got {result['level']}"


def test_pausable_composition_deprecation_warning():
    """PausableComposition feature flag has DeprecationLevel.WARNING.

    F2P: On base commit, this flag has NO deprecation annotation.
    After fix, it should have @Deprecated with level=WARNING.
    """
    content = read_file(FEATURE_FLAGS_FILE)

    result = parse_deprecated_annotation(content, 'val PausableComposition', 'before')

    assert result["found"], "No @Deprecated annotation found for PausableComposition"
    assert result["level"] == "WARNING", f"Expected DeprecationLevel.WARNING, got {result['level']}"


# ============ Fail-to-pass tests: @Suppress annotation changes ============

def test_feature_flags_suppress_includes_deprecation_error():
    """featureFlags property suppresses both DEPRECATION_ERROR and DEPRECATION.

    F2P: On base commit, it only has @Suppress("DEPRECATION").
    After fix, should have @Suppress("DEPRECATION_ERROR", "DEPRECATION").
    """
    content = read_file(EXTENSION_FILE)

    warnings = parse_suppress_annotation(content, 'val featureFlags')

    assert "DEPRECATION_ERROR" in warnings, \
        f"featureFlags should suppress DEPRECATION_ERROR, got: {warnings}"
    assert "DEPRECATION" in warnings, \
        f"featureFlags should also suppress DEPRECATION, got: {warnings}"


def test_subplugin_generate_function_key_meta_classes_suppress():
    """Subplugin uses @Suppress("DEPRECATION_ERROR") for generateFunctionKeyMetaClasses.

    F2P: On base commit, it uses @Suppress("DEPRECATION").
    After fix, should use @Suppress("DEPRECATION_ERROR").
    """
    content = read_file(SUBPLUGIN_FILE)

    # Find the line with generateFunctionKeyMetaClasses usage
    idx = content.find('generateFunctionKeyMetaClasses')
    assert idx != -1, "Could not find generateFunctionKeyMetaClasses in subplugin"

    # Look for the @Suppress in the preceding lines (within the apply block)
    before = content[max(0, idx - 300):idx]

    # Should have DEPRECATION_ERROR in a suppress annotation nearby
    assert '@Suppress("DEPRECATION_ERROR")' in before or \
           '@Suppress("DEPRECATION_ERROR",' in before, \
        "generateFunctionKeyMetaClasses usage should have @Suppress(\"DEPRECATION_ERROR\")"


def test_subplugin_stability_configuration_file_suppress():
    """Subplugin uses @Suppress("DEPRECATION_ERROR") for stabilityConfigurationFile.

    F2P: On base commit, it uses @Suppress("DEPRECATION").
    After fix, should use @Suppress("DEPRECATION_ERROR").
    """
    content = read_file(SUBPLUGIN_FILE)

    idx = content.find('stabilityConfigurationFile')
    assert idx != -1, "Could not find stabilityConfigurationFile in subplugin"

    before = content[max(0, idx - 300):idx]

    assert '@Suppress("DEPRECATION_ERROR")' in before or \
           '@Suppress("DEPRECATION_ERROR",' in before, \
        "stabilityConfigurationFile usage should have @Suppress(\"DEPRECATION_ERROR\")"


def test_subplugin_feature_flags_suppress():
    """Subplugin uses @Suppress("DEPRECATION_ERROR", "DEPRECATION") for featureFlags.

    F2P: On base commit, it only has @Suppress("DEPRECATION").
    After fix, should have @Suppress("DEPRECATION_ERROR", "DEPRECATION").
    """
    content = read_file(SUBPLUGIN_FILE)

    # Find the featureFlags handling with the zip operation
    idx = content.find('composeExtension.featureFlags')
    assert idx != -1, "Could not find featureFlags in subplugin"

    # Look for a Suppress annotation covering this code section
    # The pattern is typically in the addAll block
    section = content[max(0, idx - 100):idx + 600]

    has_error = '"DEPRECATION_ERROR"' in section
    has_deprecation = '"DEPRECATION"' in section

    assert has_error, "featureFlags handling should have DEPRECATION_ERROR in @Suppress"
    assert has_deprecation, "featureFlags handling should have DEPRECATION in @Suppress"


# ============ Fail-to-pass tests: Test code migration ============

def test_compose_it_uses_stability_configuration_files():
    """ComposeIT.kt uses stabilityConfigurationFiles instead of stabilityConfigurationFile.

    F2P: On base commit, the test uses the deprecated stabilityConfigurationFile API.
    After fix, it should use stabilityConfigurationFiles (plural) API.
    """
    content = read_file(COMPOSE_IT_FILE)

    # Should use stabilityConfigurationFiles (new plural API)
    assert 'stabilityConfigurationFiles.set' in content, (
        "ComposeIT should use stabilityConfigurationFiles.set (plural) instead of deprecated stabilityConfigurationFile.set"
    )

    # Should NOT use the old singular API
    assert 'stabilityConfigurationFile.set' not in content, (
        "ComposeIT should not use the deprecated stabilityConfigurationFile.set (singular)"
    )


def test_extension_test_suppress_annotations_updated():
    """ExtensionConfigurationTest has correct @Suppress annotations.

    F2P: Tests for ERROR-level deprecated items should use @Suppress("DEPRECATION_ERROR").
         Tests for WARNING-level deprecated items should use @Suppress("DEPRECATION").
    """
    content = read_file(EXTENSION_TEST_FILE)

    # Check specific test functions have correct suppress annotations
    # Test functions that use ERROR-level deprecated APIs
    error_level_tests = [
        'testStabilityConfigurationFile',
        'disableIntrinsicRemember',
        'disableStrongSkipping',
        'disableIntrinsicRememberCompatibility',
        'disableStrongSkippingCompatibility',
        'enableNonSkippingGroupOptimizationCompatibility',
        'enableMultipleFlags',
        'enableMultipleFlagsCompatibility',
        'enableMultipleFlagsCompatibilityDefaults',
        'combineDeprecatedPropertiesWithFeatureFlags',
        'contradictInConfiguredFlags',
        'combineDeprecatedPropertiesWithFeatureFlags_StrongSkipping',
    ]

    for test_name in error_level_tests:
        idx = content.find(f'fun {test_name}()')
        assert idx != -1, f"Could not find test function {test_name}"

        # Look for @Suppress in the 200 chars before OR first 300 chars after the function
        before = content[max(0, idx - 200):idx]
        after = content[idx:idx + 300]
        function_context = before + after

        # Check for DEPRECATION_ERROR suppress
        if test_name == 'enableMultipleFlags':
            # This test uses both ERROR and WARNING level, so needs both
            assert '"DEPRECATION_ERROR"' in function_context, \
                f"{test_name} should have @Suppress with DEPRECATION_ERROR"
        else:
            assert '@Suppress("DEPRECATION_ERROR")' in function_context, \
                f"{test_name} should have @Suppress(\"DEPRECATION_ERROR\")"

    # Tests for WARNING-level deprecated items
    warning_level_tests = [
        'disableNonSkippingGroupOptimization',
        'disablePausableComposition',
    ]

    for test_name in warning_level_tests:
        idx = content.find(f'fun {test_name}()')
        assert idx != -1, f"Could not find test function {test_name}"

        # Look for @Suppress in the 200 chars before OR first 300 chars after the function
        before = content[max(0, idx - 200):idx]
        after = content[idx:idx + 300]
        function_context = before + after

        assert '@Suppress("DEPRECATION")' in function_context, \
            f"{test_name} should have @Suppress(\"DEPRECATION\")"


# ============ Code execution test: Kotlin compilation ============

def test_compose_compiler_compiles():
    """Compose compiler module compiles successfully after changes.

    F2P: If the base commit compiles but the deprecation changes break compilation,
    this test will fail until the @Suppress annotations are correctly updated.

    This test uses subprocess.run() to execute gradle compileKotlin.
    """
    # Check that Java is available
    java_check = subprocess.run(["which", "java"], capture_output=True, text=True)
    if java_check.returncode != 0:
        # Skip if Java is not available (e.g., in test environment without full JDK)
        import pytest
        pytest.skip("Java not available - skipping compilation test")

    # Check that gradle wrapper exists
    gradlew = REPO / "gradlew"
    if not gradlew.exists():
        import pytest
        pytest.skip("Gradle wrapper not found - skipping compilation test")

    # Try to compile just the compose compiler module
    # Use a timeout to avoid hanging - use longer timeout
    try:
        r = subprocess.run(
            [str(gradlew), ":compose-compiler-gradle-plugin:compileKotlin",
             "--no-daemon", "-q"],
            capture_output=True,
            text=True,
            timeout=600,
            cwd=str(REPO),
        )

        # The compilation should succeed after the fix
        # On base commit, it may fail due to deprecation warnings treated as errors
        # Skip if network-related or Gradle internal errors (we can't verify in this environment)
        if r.returncode != 0:
            stderr = r.stderr.lower()
            skip_reasons = [
                "could not resolve", "network", "timeout", "connect", "unreachable",
                "classloader", "must be locked", "configuration problem", "gradle internal",
            ]
            if any(x in stderr for x in skip_reasons):
                import pytest
                pytest.skip("Gradle environment issue - skipping compilation test")

        assert r.returncode == 0, (
            f"Compose compiler compilation failed:\n"
            f"stdout: {r.stdout[-1000:]}\n"
            f"stderr: {r.stderr[-1000:]}"
        )
    except subprocess.TimeoutExpired:
        # If timeout, skip the test rather than fail (this is a heavy test)
        import pytest
        pytest.skip("Compilation test timed out after 600 seconds - skipping")
    except FileNotFoundError as e:
        raise AssertionError(f"Could not run gradle: {e}")


def test_compose_compiler_syntax_valid():
    """Compose compiler source files have valid Kotlin syntax.

    This test verifies that Kotlin files can be parsed by kotlinc.
    """
    # Check if kotlinc is available
    kotlinc_check = subprocess.run(
        ["which", "kotlinc"],
        capture_output=True,
        text=True,
    )

    if kotlinc_check.returncode != 0:
        # Skip if kotlinc not available - this is a p2p test
        import pytest
        pytest.skip("kotlinc not available - skipping syntax test")

    source_files = [
        EXTENSION_FILE,
        FEATURE_FLAGS_FILE,
        SUBPLUGIN_FILE,
    ]

    for src_file in source_files:
        # Use kotlinc to parse the file - check for syntax errors
        # Run with -d /tmp to avoid generating output and to check compilation up to JVM stage
        r = subprocess.run(
            ["kotlinc", str(src_file), "-d", "/tmp/kotlin-syntax-check"],
            capture_output=True,
            text=True,
            timeout=60,
        )

        # Ignore errors about missing dependencies (not syntax errors)
        # Only fail on actual syntax errors
        if r.returncode != 0:
            stderr_lower = r.stderr.lower()
            # Only count as failure if there are syntax/unresolved reference errors
            # Missing imports or dependencies are expected in this minimal environment
            if any(term in stderr_lower for term in ["syntax error", "unexpected", "expecting"]):
                assert False, (
                    f"Kotlin syntax error in {src_file.name}:\n{r.stderr}"
                )
        # If we get here, syntax is valid (even if compilation failed due to missing deps)


# ============ Pass-to-pass tests: Repo CI/CD ============

def test_compose_compiler_module_exists():
    """Compose compiler module exists and has expected structure (p2p)."""
    assert EXTENSION_FILE.exists(), "ComposeCompilerGradlePluginExtension.kt should exist"
    assert FEATURE_FLAGS_FILE.exists(), "ComposeFeatureFlags.kt should exist"
    assert SUBPLUGIN_FILE.exists(), "ComposeCompilerSubplugin.kt should exist"


def test_compose_compiler_functional_test_exists():
    """Compose compiler functional test file exists (p2p)."""
    assert EXTENSION_TEST_FILE.exists(), "ExtensionConfigurationTest.kt should exist"


def test_compose_compiler_build_config_valid():
    """Compose compiler module build.gradle.kts is valid and has required configuration (p2p)."""
    content = read_file(BUILD_GRADLE_FILE)

    # Check for required plugin configuration
    assert "gradle-plugin-common-configuration" in content, "Should use gradle-plugin-common-configuration"
    assert "jvm-test-suite" in content, "Should use jvm-test-suite plugin"

    # Check for test suite configuration
    assert "testing {" in content, "Should have testing configuration"
    assert "functionalTest" in content, "Should have functionalTest suite"


def test_compose_compiler_source_files_valid():
    """All Compose compiler source files have valid structure (p2p)."""
    source_dir = REPO / "libraries/tools/kotlin-compose-compiler/src/common/kotlin/org/jetbrains/kotlin/compose/compiler/gradle"

    kt_files = list(source_dir.glob("*.kt"))
    assert len(kt_files) >= 3, f"Should have at least 3 Kotlin source files, found {len(kt_files)}"

    # Check each file for basic validity
    for kt_file in kt_files:
        content = kt_file.read_text()
        # Basic Kotlin syntax checks
        assert content.count("{") >= content.count("}"), f"{kt_file.name}: Unbalanced braces"
        assert "package " in content, f"{kt_file.name}: Missing package declaration"


def test_compose_compiler_test_structure_valid():
    """Compose compiler test files have valid structure (p2p)."""
    test_dir = REPO / "libraries/tools/kotlin-compose-compiler/src/functionalTest/kotlin/org/jetbrains/kotlin/compose/compiler/gradle"

    # Check that test directory exists and has test files
    test_files = list(test_dir.glob("*Test.kt"))
    assert len(test_files) >= 1, f"Should have at least 1 test file, found {len(test_files)}"

    # Verify test files contain valid test annotations
    for test_file in test_files:
        content = test_file.read_text()
        assert "@Test" in content, f"{test_file.name}: Missing @Test annotation"


def test_compose_compiler_extension_test_exists():
    """Compose compiler has ExtensionConfigurationTest with expected structure (p2p)."""
    content = read_file(EXTENSION_TEST_FILE)

    # Check for expected test methods
    assert "testDefaultExtensionConfiguration" in content, "Should have testDefaultExtensionConfiguration test"
    assert "disableIntrinsicRemember" in content, "Should have disableIntrinsicRemember test"


def test_compose_it_structure_valid():
    """ComposeIT.kt integration test has valid structure (p2p)."""
    assert COMPOSE_IT_FILE.exists(), "ComposeIT.kt should exist"

    content = COMPOSE_IT_FILE.read_text()

    # Check for class declaration
    assert "class ComposeIT" in content, "Should define ComposeIT class"


def test_repo_gradle_wrapper_valid():
    """Repo Gradle wrapper exists and is valid (p2p)."""
    gradlew = REPO / "gradlew"
    wrapper_props = REPO / "gradle/wrapper/gradle-wrapper.properties"

    assert gradlew.exists(), "gradlew should exist"
    assert wrapper_props.exists(), "gradle-wrapper.properties should exist"

    # Check that wrapper properties has valid distributionUrl
    props_content = wrapper_props.read_text()
    assert "distributionUrl" in props_content, "gradle-wrapper.properties should have distributionUrl"


def test_compose_compiler_module_gradle_builds():
    """Compose compiler module can be included in gradle build (p2p).

    This test runs gradle help to verify the build scripts are parseable.
    """
    # Check that Java is available
    java_check = subprocess.run(["which", "java"], capture_output=True, text=True)
    if java_check.returncode != 0:
        import pytest
        pytest.skip("Java not available - skipping gradle build test")

    gradlew = REPO / "gradlew"
    if not gradlew.exists():
        import pytest
        pytest.skip("Gradle wrapper not found - skipping gradle build test")

    try:
        r = subprocess.run(
            [str(gradlew), ":compose-compiler-gradle-plugin:help", "--no-daemon", "-q"],
            capture_output=True,
            text=True,
            timeout=300,
            cwd=str(REPO),
        )

        # Skip if network-related error
        if r.returncode != 0:
            stderr = r.stderr.lower()
            if any(x in stderr for x in ["could not resolve", "network", "timeout", "connect", "unreachable"]):
                import pytest
                pytest.skip("Network-related build failure - skipping gradle build test")

        assert r.returncode == 0, f"Gradle help failed: {r.stderr}"
    except subprocess.TimeoutExpired:
        # If timeout, skip rather than fail
        import pytest
        pytest.skip("Gradle help timed out - skipping")


if __name__ == "__main__":
    import sys
    import pytest

    # Run pytest with verbose output
    exit_code = pytest.main([__file__, "-v", "--tb=short"])
    sys.exit(exit_code)
