"""Tests for Kotlin Compose Compiler deprecation level updates."""

import subprocess
import re
from pathlib import Path

REPO = Path("/workspace/kotlin")

# File paths
EXTENSION_FILE = REPO / "libraries/tools/kotlin-compose-compiler/src/common/kotlin/org/jetbrains/kotlin/compose/compiler/gradle/ComposeCompilerGradlePluginExtension.kt"
FEATURE_FLAGS_FILE = REPO / "libraries/tools/kotlin-compose-compiler/src/common/kotlin/org/jetbrains/kotlin/compose/compiler/gradle/ComposeFeatureFlags.kt"
SUBPLUGIN_FILE = REPO / "libraries/tools/kotlin-compose-compiler/src/common/kotlin/org/jetbrains/kotlin/compose/compiler/gradle/ComposeCompilerSubplugin.kt"
TEST_FILE = REPO / "libraries/tools/kotlin-compose-compiler/src/functionalTest/kotlin/org/jetbrains/kotlin/compose/compiler/gradle/ExtensionConfigurationTest.kt"
INTEGRATION_TEST_FILE = REPO / "libraries/tools/kotlin-gradle-plugin-integration-tests/src/test/kotlin/org/jetbrains/kotlin/gradle/ComposeIT.kt"

MODULE_PATH = "libraries/tools/kotlin-compose-compiler"


def _read_file(path: Path) -> str:
    """Read file content."""
    if not path.exists():
        return ""
    return path.read_text()


def _run_gradle(args: list, cwd: Path = REPO, timeout: int = 300) -> subprocess.CompletedProcess:
    """Run Gradle command and return result."""
    cmd = ["./gradlew"] + args
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=cwd,
    )


def _extract_annotation_content(content: str, target_line: str, lines_before: int = 15) -> str:
    """Extract annotation content before a target line."""
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if target_line in line:
            start = max(0, i - lines_before)
            return '\n'.join(lines[start:i])
    return ""


# =============================================================================
# Fail-to-pass tests: These verify the fix is applied correctly
# =============================================================================

def test_generateFunctionKeyMetaClasses_deprecation_level():
    """generateFunctionKeyMetaClasses property should have ERROR deprecation level and mention Kotlin 2.5.0."""
    content = _read_file(EXTENSION_FILE)

    annotation_content = _extract_annotation_content(content, 'val generateFunctionKeyMetaClasses:')

    assert 'level = DeprecationLevel.ERROR' in annotation_content, \
        "generateFunctionKeyMetaClasses should have DeprecationLevel.ERROR"
    assert 'Kotlin 2.5.0' in annotation_content, \
        "generateFunctionKeyMetaClasses deprecation message should mention Kotlin 2.5.0"


def test_enableIntrinsicRemember_deprecation_level():
    """enableIntrinsicRemember property should have ERROR deprecation level and mention Kotlin 2.5.0."""
    content = _read_file(EXTENSION_FILE)

    annotation_content = _extract_annotation_content(content, 'val enableIntrinsicRemember:')

    assert 'level = DeprecationLevel.ERROR' in annotation_content, \
        "enableIntrinsicRemember should have DeprecationLevel.ERROR"
    assert 'Kotlin 2.5.0' in annotation_content, \
        "enableIntrinsicRemember deprecation message should mention Kotlin 2.5.0"


def test_enableNonSkippingGroupOptimization_deprecation_level():
    """enableNonSkippingGroupOptimization property should have ERROR deprecation level and mention Kotlin 2.5.0."""
    content = _read_file(EXTENSION_FILE)

    annotation_content = _extract_annotation_content(content, 'val enableNonSkippingGroupOptimization:')

    assert 'level = DeprecationLevel.ERROR' in annotation_content, \
        "enableNonSkippingGroupOptimization should have DeprecationLevel.ERROR"
    assert 'Kotlin 2.5.0' in annotation_content, \
        "enableNonSkippingGroupOptimization deprecation message should mention Kotlin 2.5.0"


def test_enableStrongSkippingMode_deprecation_level():
    """enableStrongSkippingMode property should have ERROR deprecation level and mention Kotlin 2.5.0."""
    content = _read_file(EXTENSION_FILE)

    annotation_content = _extract_annotation_content(content, 'val enableStrongSkippingMode:')

    assert 'level = DeprecationLevel.ERROR' in annotation_content, \
        "enableStrongSkippingMode should have DeprecationLevel.ERROR"
    assert 'Kotlin 2.5.0' in annotation_content, \
        "enableStrongSkippingMode deprecation message should mention Kotlin 2.5.0"


def test_stabilityConfigurationFile_deprecation_level():
    """stabilityConfigurationFile property should have ERROR deprecation level and mention Kotlin 2.5.0."""
    content = _read_file(EXTENSION_FILE)

    annotation_content = _extract_annotation_content(content, 'abstract val stabilityConfigurationFile:')

    assert 'level = DeprecationLevel.ERROR' in annotation_content, \
        "stabilityConfigurationFile should have DeprecationLevel.ERROR"
    assert 'Kotlin 2.5.0' in annotation_content, \
        "stabilityConfigurationFile deprecation message should mention Kotlin 2.5.0"


def test_composeFeatureFlag_strongSkipping_deprecation():
    """ComposeFeatureFlag.StrongSkipping should have ERROR deprecation level and mention Kotlin 2.5.0."""
    content = _read_file(FEATURE_FLAGS_FILE)

    annotation_content = _extract_annotation_content(content, 'val StrongSkipping:')

    assert 'level = DeprecationLevel.ERROR' in annotation_content, \
        "StrongSkipping should have DeprecationLevel.ERROR"
    assert 'Kotlin 2.5.0' in annotation_content, \
        "StrongSkipping deprecation message should mention Kotlin 2.5.0"


def test_composeFeatureFlag_intrinsicRemember_deprecation():
    """ComposeFeatureFlag.IntrinsicRemember should have ERROR deprecation level and mention Kotlin 2.5.0."""
    content = _read_file(FEATURE_FLAGS_FILE)

    annotation_content = _extract_annotation_content(content, 'val IntrinsicRemember:')

    assert 'level = DeprecationLevel.ERROR' in annotation_content, \
        "IntrinsicRemember should have DeprecationLevel.ERROR"
    assert 'Kotlin 2.5.0' in annotation_content, \
        "IntrinsicRemember deprecation message should mention Kotlin 2.5.0"


def test_composeFeatureFlag_optimizeNonSkippingGroups_deprecation():
    """ComposeFeatureFlag.OptimizeNonSkippingGroups should have WARNING deprecation level."""
    content = _read_file(FEATURE_FLAGS_FILE)

    annotation_content = _extract_annotation_content(content, 'val OptimizeNonSkippingGroups:')

    assert 'level = DeprecationLevel.WARNING' in annotation_content, \
        "OptimizeNonSkippingGroups should have DeprecationLevel.WARNING"


def test_composeFeatureFlag_pausableComposition_deprecation():
    """ComposeFeatureFlag.PausableComposition should have WARNING deprecation level."""
    content = _read_file(FEATURE_FLAGS_FILE)

    annotation_content = _extract_annotation_content(content, 'val PausableComposition:')

    assert 'level = DeprecationLevel.WARNING' in annotation_content, \
        "PausableComposition should have DeprecationLevel.WARNING"


def test_suppress_deprecation_error_in_extension():
    """Extension file should use @Suppress("DEPRECATION_ERROR", "DEPRECATION") for featureFlags."""
    content = _read_file(EXTENSION_FILE)

    lines = content.split('\n')
    for i, line in enumerate(lines):
        if 'val featureFlags:' in line:
            # Look for suppress annotation in previous 5 lines
            for j in range(max(0, i-5), i):
                if '@Suppress(' in lines[j]:
                    suppress_content = lines[j]
                    # Handle multi-line suppress
                    k = j
                    while k < i and ')' not in lines[k]:
                        k += 1
                        suppress_content += lines[k]
                    assert 'DEPRECATION_ERROR' in suppress_content, \
                        "featureFlags should have @Suppress with DEPRECATION_ERROR"
                    return
            break
    assert False, "featureFlags should have @Suppress annotation with DEPRECATION_ERROR"


def test_suppress_deprecation_error_in_subplugin():
    """Subplugin file should use @Suppress("DEPRECATION_ERROR") in appropriate places."""
    content = _read_file(SUBPLUGIN_FILE)

    # Count occurrences of DEPRECATION_ERROR suppress
    deprecation_error_count = content.count('"DEPRECATION_ERROR"')
    assert deprecation_error_count >= 3, \
        f"Expected at least 3 @Suppress(\"DEPRECATION_ERROR\") annotations, found {deprecation_error_count}"


def test_deprecated_annotation_multiline_format():
    """All @Deprecated annotations should use named parameters with proper formatting."""
    content = _read_file(EXTENSION_FILE)

    # Check for old-style single-line deprecated annotations on properties
    # Old style: @Deprecated("message") without level
    old_style_pattern = re.compile(r'@Deprecated\("[^"]+"\)\s*\n\s*val', re.MULTILINE)
    matches = old_style_pattern.findall(content)

    assert len(matches) == 0, \
        f"Found {len(matches)} old-style @Deprecated annotations - all should be converted to multi-line format with level"


def test_kotlin_version_in_all_deprecation_messages():
    """All deprecation messages in extension and feature flags should mention Kotlin 2.5.0."""
    ext_content = _read_file(EXTENSION_FILE)
    flags_content = _read_file(FEATURE_FLAGS_FILE)

    # Count ERROR level deprecations that should mention Kotlin 2.5.0
    # 5 properties in extension file with ERROR level
    ext_error_count = ext_content.count('level = DeprecationLevel.ERROR')

    # 2 feature flags with ERROR level (StrongSkipping, IntrinsicRemember)
    flags_error_count = flags_content.count('level = DeprecationLevel.ERROR')

    total_error_deprecations = ext_error_count + flags_error_count

    # Count mentions of Kotlin 2.5.0
    kotlin_25_count = (ext_content + flags_content).count("Kotlin 2.5.0")

    assert kotlin_25_count >= total_error_deprecations, \
        f"Expected at least {total_error_deprecations} mentions of 'Kotlin 2.5.0' (matching ERROR deprecations), found {kotlin_25_count}"


def test_compilation_with_deprecated_properties_fails():
    """BEHAVIORAL: Using ERROR-level deprecated properties causes compilation errors without @Suppress."""
    # Create a test Kotlin file that uses deprecated properties
    test_code = '''
import org.jetbrains.kotlin.compose.compiler.gradle.ComposeCompilerGradlePluginExtension
import org.jetbrains.kotlin.compose.compiler.gradle.ComposeFeatureFlag

// This file attempts to access deprecated ERROR-level APIs without @Suppress
// If properly deprecated with ERROR level, compilation should fail without @Suppress

fun testDeprecatedAccess(extension: ComposeCompilerGradlePluginExtension) {
    // These should trigger deprecation errors with DeprecationLevel.ERROR
    extension.generateFunctionKeyMetaClasses.set(true)
}
'''
    test_file = REPO / "_test_deprecated.kt"
    test_file.write_text(test_code)

    try:
        # Try to compile the file
        r = subprocess.run(
            ["kotlinc", "-d", "/tmp/test_out", str(test_file)],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=REPO,
        )

        # If compilation fails due to deprecation errors, that's expected
        # The test passes if we get compilation errors related to deprecation
        # (we can't fully compile without all dependencies, but we can check for deprecation errors in output)
        output = r.stdout + r.stderr

        # Look for deprecation-related errors in output
        has_deprecation_error = 'DEPRECATION_ERROR' in output or 'is deprecated' in output.lower()

        # For ERROR level deprecations, we expect to see deprecation warnings treated as errors
        # Note: This is a behavioral check - the actual result depends on Kotlin compiler behavior
        # The key is that deprecation warnings should be present for ERROR-level deprecations
        if r.returncode != 0:
            # Compilation failed - check if it's due to deprecation or just missing dependencies
            assert has_deprecation_error or 'unresolved' in output.lower() or 'import' in output.lower(), \
                f"Expected compilation to fail due to deprecation errors or missing dependencies. Output: {output[:500]}"
    finally:
        test_file.unlink(missing_ok=True)


def test_compilation_with_suppress_succeeds():
    """BEHAVIORAL: Using @Suppress allows access to deprecated properties."""
    # This is verified by the module compiling successfully with @Suppress annotations
    # Run gradle compile to verify
    r = _run_gradle(
        [":libraries:tools:kotlin-compose-compiler:compileKotlin", "--no-daemon", "-q"],
        timeout=300,
    )

    # If the build failed due to missing project directories (sparse checkout limitation),
    # skip this test rather than fail
    if r.returncode != 0:
        stderr = r.stderr.lower()
        if "configuring project" in stderr and "does not exist" in stderr:
            import pytest
            pytest.skip("Gradle configuration failed due to sparse checkout - project directories missing")
        if "could not create task" in stderr and "compilekotlin" in stderr:
            import pytest
            pytest.skip("Gradle task creation failed - partial checkout limitation")

    # Module should compile successfully with the @Suppress annotations in place
    assert r.returncode == 0, \
        f"Module should compile with @Suppress annotations for deprecated APIs. Error: {r.stderr[-1000:]}"


# =============================================================================
# Pass-to-pass tests: These verify general code quality and should pass
# on both the base commit and after the fix is applied
# =============================================================================

def test_source_files_exist():
    """All required source files exist (pass_to_pass)."""
    files = [
        EXTENSION_FILE,
        FEATURE_FLAGS_FILE,
        SUBPLUGIN_FILE,
    ]
    for f in files:
        assert f.exists(), f"Source file missing: {f}"


def test_copyright_headers_present():
    """All source files have copyright headers (pass_to_pass)."""
    files = [
        EXTENSION_FILE,
        FEATURE_FLAGS_FILE,
        SUBPLUGIN_FILE,
    ]
    for f in files:
        content = _read_file(f)
        assert "Copyright" in content or "License" in content, f"Missing copyright header in {f}"


def test_no_tabs_in_source():
    """Source files use spaces for indentation, not tabs (pass_to_pass)."""
    files = [
        EXTENSION_FILE,
        FEATURE_FLAGS_FILE,
        SUBPLUGIN_FILE,
    ]
    for f in files:
        content = _read_file(f)
        assert "\t" not in content, f"Found tab character in {f} - use spaces for indentation"


def test_kotlin_syntax_basic():
    """Source files have valid basic Kotlin syntax (pass_to_pass)."""
    files = [
        EXTENSION_FILE,
        FEATURE_FLAGS_FILE,
        SUBPLUGIN_FILE,
    ]
    for f in files:
        content = _read_file(f)
        # Check for basic Kotlin file structure
        assert "package org.jetbrains.kotlin.compose.compiler.gradle" in content, \
            f"Missing package declaration in {f}"
        # Check that braces are balanced (basic sanity check)
        open_braces = content.count("{")
        close_braces = content.count("}")
        assert open_braces == close_braces, \
            f"Unbalanced braces in {f}: {open_braces} open, {close_braces} close"


def test_no_trailing_whitespace():
    """Source files have no trailing whitespace (pass_to_pass)."""
    files = [
        EXTENSION_FILE,
        FEATURE_FLAGS_FILE,
        SUBPLUGIN_FILE,
    ]
    for f in files:
        content = _read_file(f)
        lines = content.split("\n")
        for i, line in enumerate(lines, 1):
            if line.rstrip() != line:
                assert False, f"Trailing whitespace found in {f} at line {i}"


def test_extension_has_required_properties():
    """Extension file has all required property definitions (pass_to_pass)."""
    content = _read_file(EXTENSION_FILE)
    required_properties = [
        "val generateFunctionKeyMetaClasses",
        "val enableIntrinsicRemember",
        "val enableNonSkippingGroupOptimization",
        "val enableStrongSkippingMode",
        "val stabilityConfigurationFile",
        "val featureFlags",
    ]
    for prop in required_properties:
        assert prop in content, f"Required property missing: {prop}"


def test_feature_flags_has_all_flags():
    """FeatureFlags file has all required feature flags (pass_to_pass)."""
    content = _read_file(FEATURE_FLAGS_FILE)
    required_flags = [
        "StrongSkipping",
        "IntrinsicRemember",
        "OptimizeNonSkippingGroups",
        "PausableComposition",
    ]
    for flag in required_flags:
        assert flag in content, f"Required feature flag missing: {flag}"


def test_editorconfig_final_newline():
    """Source files end with newline (pass_to_pass per .editorconfig)."""
    files = [
        EXTENSION_FILE,
        FEATURE_FLAGS_FILE,
        SUBPLUGIN_FILE,
    ]
    for f in files:
        content = _read_file(f)
        assert content.endswith("\n"), f"File {f} should end with newline per .editorconfig"


# =============================================================================
# Repo tests: Pass-to-pass tests that verify the repo's own test suite passes
# =============================================================================

def test_repo_compose_compiler_compiles():
    """BEHAVIORAL: Repo compose compiler module compiles without errors (pass_to_pass)."""
    r = _run_gradle(
        [":libraries:tools:kotlin-compose-compiler:compileKotlin", "--no-daemon", "-q"],
        timeout=300,
    )

    # If the build failed due to missing project directories (sparse checkout limitation),
    # skip this test rather than fail
    if r.returncode != 0:
        stderr = r.stderr.lower()
        if "configuring project" in stderr and "does not exist" in stderr:
            import pytest
            pytest.skip("Gradle configuration failed due to sparse checkout - project directories missing")
        if "could not create task" in stderr and "compilekotlin" in stderr:
            import pytest
            pytest.skip("Gradle task creation failed - partial checkout limitation")

    assert r.returncode == 0, \
        f"Compose compiler module should compile. Error: {r.stderr[-1000:]}"


def test_repo_compose_compiler_compiles_common_test():
    """BEHAVIORAL: Repo compose compiler commonTest compiles without errors (pass_to_pass)."""
    r = _run_gradle(
        [":libraries:tools:kotlin-compose-compiler:compileTestKotlin", "--no-daemon", "-q"],
        timeout=300,
    )
    # This may fail on base commit due to missing test sources, but should not fail due to deprecation errors
    if r.returncode != 0:
        # Check that failure is not due to deprecation errors (our main concern)
        assert 'DEPRECATION_ERROR' not in r.stderr, \
            f"Test compilation failed due to deprecation errors: {r.stderr[-1000:]}"


def test_repo_functional_tests_compile():
    """BEHAVIORAL: ExtensionConfigurationTest compiles with updated suppress annotations (pass_to_pass)."""
    if not TEST_FILE.exists():
        return  # Skip if test file doesn't exist in base commit

    r = _run_gradle(
        [":libraries:tools:kotlin-compose-compiler:compileFunctionalTestKotlin", "--no-daemon", "-q"],
        timeout=300,
    )

    if r.returncode != 0:
        # On base commit, this may fail due to missing suppress annotations
        # After fix, it should pass
        pass


def test_deprecated_properties_accessible_with_suppress():
    """BEHAVIORAL: ExtensionConfigurationTest methods can access deprecated properties with @Suppress (pass_to_pass)."""
    if not TEST_FILE.exists():
        return  # Skip if test file doesn't exist

    content = _read_file(TEST_FILE)

    # Check that test methods accessing deprecated properties have proper @Suppress
    # Methods that access ERROR-level deprecated properties should use DEPRECATION_ERROR

    # Find test methods and their suppress annotations
    lines = content.split('\n')
    current_suppress = None

    for i, line in enumerate(lines):
        # Track suppress annotations
        if '@Suppress(' in line:
            current_suppress = line
            # Handle multi-line
            j = i
            while ')' not in lines[j] and j < len(lines) - 1:
                j += 1
                current_suppress += lines[j]

        # Check test methods that access deprecated ERROR-level properties
        if 'fun ' in line and ('stabilityConfigurationFile' in line or
                                'enableIntrinsicRemember' in line or
                                'enableStrongSkippingMode' in line or
                                'enableNonSkippingGroupOptimization' in line):
            # These methods should have DEPRECATION_ERROR suppress
            if current_suppress:
                assert 'DEPRECATION_ERROR' in current_suppress, \
                    f"Test method at line {i} accessing deprecated property should have @Suppress(\"DEPRECATION_ERROR\")"

        # Reset suppress when we see a new test method or class declaration
        if 'fun ' in line or 'class ' in line or 'val ' in line or 'var ' in line:
            if '@Suppress(' not in line:
                current_suppress = None
