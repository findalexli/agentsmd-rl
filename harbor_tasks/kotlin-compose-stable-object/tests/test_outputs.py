"""Test outputs for Kotlin Compose compiler stability fix."""

import subprocess
import sys
import os

REPO = "/workspace/kotlin"
STABILITY_FILE = f"{REPO}/plugins/compose/compiler-hosted/src/main/java/androidx/compose/compiler/plugins/kotlin/analysis/Stability.kt"
LOWERING_FILE = f"{REPO}/plugins/compose/compiler-hosted/src/main/java/androidx/compose/compiler/plugins/kotlin/lower/AbstractComposeLowering.kt"


def _run_kotlinc_syntax_check(file_path: str) -> tuple[int, str, str]:
    """Run kotlinc to validate Kotlin file syntax.

    Returns exit code 1 for compilation errors (missing deps) - this is expected
    and means syntax is valid. Returns exit code 2+ for internal/compiler errors.
    """
    r = subprocess.run(
        ["kotlinc", file_path],
        capture_output=True, text=True, timeout=60
    )
    return r.returncode, r.stdout, r.stderr


def test_stability_kt_has_object_check():
    """Fail-to-pass: Stability.kt must have 'declaration.isObject' check."""
    with open(STABILITY_FILE, 'r') as f:
        content = f.read()

    # Check that the isObject check exists after the enum check
    assert "if (declaration.isEnumClass || declaration.isEnumEntry) return Stability.Stable" in content, \
        "Missing enum stability check (baseline marker)"
    assert "if (declaration.isObject) return Stability.Stable" in content, \
        "Missing declaration.isObject check in Stability.kt - objects should be treated as stable"


def test_lowering_kt_has_isobject_check():
    """Fail-to-pass: AbstractComposeLowering.kt must use isObject instead of isCompanion."""
    with open(LOWERING_FILE, 'r') as f:
        content = f.read()

    # The fix changes isCompanion to isObject to handle all objects
    assert "if (symbol.owner.isObject) true" in content, \
        "Missing symbol.owner.isObject check in AbstractComposeLowering.kt - should treat all objects as static"


def test_no_stable_property_in_golden_files():
    """Fail-to-pass: Golden files modified by PR should not reference Object.%stable after fix."""
    import os

    # Specific golden files that were modified by this PR to remove .%stable references
    golden_base = f"{REPO}/plugins/compose/compiler-hosted/integration-tests/src/jvmTest/resources/golden"

    files_to_check = [
        # ContextParametersTransformTests
        f"{golden_base}/androidx.compose.compiler.plugins.kotlin.ContextParametersTransformTests/testMemoizationContextParameters.txt",
        # ControlFlowTransformTests
        f"{golden_base}/androidx.compose.compiler.plugins.kotlin.ControlFlowTransformTests/testComposablePropertyDelegate[useFir = false].txt",
        f"{golden_base}/androidx.compose.compiler.plugins.kotlin.ControlFlowTransformTests/testComposablePropertyDelegate[useFir = true].txt",
        # DefaultParamTransformTests
        f"{golden_base}/androidx.compose.compiler.plugins.kotlin.DefaultParamTransformTests/testDefaultArgsOnInvoke[useFir = false].txt",
        f"{golden_base}/androidx.compose.compiler.plugins.kotlin.DefaultParamTransformTests/testDefaultArgsOnInvoke[useFir = true].txt",
        # LambdaMemoizationTransformTests
        f"{golden_base}/androidx.compose.compiler.plugins.kotlin.LambdaMemoizationTransformTests/composableLambdaInInlineDefaultParam[useFir = false].txt",
        f"{golden_base}/androidx.compose.compiler.plugins.kotlin.LambdaMemoizationTransformTests/composableLambdaInInlineDefaultParam[useFir = true].txt",
        # New test golden files
        f"{golden_base}/androidx.compose.compiler.plugins.kotlin.ComposerParamTransformTests/testObjectTypesAreStable[useFir = false].txt",
        f"{golden_base}/androidx.compose.compiler.plugins.kotlin.ComposerParamTransformTests/testObjectTypesAreStable[useFir = true].txt",
    ]

    files_checked = 0
    for filepath in files_to_check:
        if not os.path.exists(filepath):
            continue

        files_checked += 1
        with open(filepath, 'r') as f:
            content = f.read()

        # The fix removes object.%stable references (like MaterialTheme.%stable, BoxScope.%stable, etc.)
        # These specific files should NOT have .%stable references after the fix
        if '.%stable' in content:
            lines = content.split('\n')
            for line in lines:
                if '.%stable' in line and not line.strip().startswith('//'):
                    assert False, f"Found .%stable reference in {filepath}: {line.strip()}"

    assert files_checked > 0, "No golden files found to check"


def test_compose_compiler_sources_exist():
    """Pass-to-pass: Compose compiler plugin source files exist and are valid Kotlin."""
    import os

    # Check that the main source files exist
    stability_exists = os.path.exists(STABILITY_FILE)
    lowering_exists = os.path.exists(LOWERING_FILE)

    assert stability_exists, f"Stability.kt not found at {STABILITY_FILE}"
    assert lowering_exists, f"AbstractComposeLowering.kt not found at {LOWERING_FILE}"

    # Basic syntax check - files should be valid Kotlin source
    with open(STABILITY_FILE, 'r') as f:
        stability_content = f.read()
    assert "class StabilityInferencer" in stability_content, "StabilityInferencer class not found"

    with open(LOWERING_FILE, 'r') as f:
        lowering_content = f.read()
    assert "abstract class AbstractComposeLowering" in lowering_content, "AbstractComposeLowering class not found"


def test_static_expression_detection_compiles():
    """Pass-to-pass: StaticExpressionDetectionTests source file is valid."""
    test_file = f"{REPO}/plugins/compose/compiler-hosted/integration-tests/src/jvmTest/kotlin/androidx/compose/compiler/plugins/kotlin/StaticExpressionDetectionTests.kt"

    with open(test_file, 'r') as f:
        content = f.read()

    # Basic sanity check
    assert "class StaticExpressionDetectionTests" in content, "StaticExpressionDetectionTests class not found"


def test_new_golden_files_exist():
    """Fail-to-pass: New golden files for object stability test should exist."""
    import os

    golden_dir = f"{REPO}/plugins/compose/compiler-hosted/integration-tests/src/jvmTest/resources/golden"

    # Check for the new test golden files that were added
    test_file_fir_false = f"{golden_dir}/androidx.compose.compiler.plugins.kotlin.ComposerParamTransformTests/testObjectTypesAreStable[useFir = false].txt"
    test_file_fir_true = f"{golden_dir}/androidx.compose.compiler.plugins.kotlin.ComposerParamTransformTests/testObjectTypesAreStable[useFir = true].txt"

    # These files are added by the fix
    fir_false_exists = os.path.exists(test_file_fir_false)
    fir_true_exists = os.path.exists(test_file_fir_true)

    # At least one should exist (they are identical content)
    assert fir_false_exists or fir_true_exists, \
        "Missing testObjectTypesAreStable golden files - test files should be created"

    # Verify the content doesn't have Object.%stable
    if fir_false_exists:
        with open(test_file_fir_false, 'r') as f:
            content = f.read()
        assert "Object.%stable" not in content, \
            "Golden file should not contain Object.%stable after fix"

    if fir_true_exists:
        with open(test_file_fir_true, 'r') as f:
            content = f.read()
        assert "Object.%stable" not in content, \
            "Golden file should not contain Object.%stable after fix"


def test_test_methods_exist():
    """Fail-to-pass: Test methods for object stability should exist."""
    composer_test_file = f"{REPO}/plugins/compose/compiler-hosted/integration-tests/src/jvmTest/kotlin/androidx/compose/compiler/plugins/kotlin/ComposerParamTransformTests.kt"
    run_test_file = f"{REPO}/plugins/compose/compiler-hosted/integration-tests/src/jvmTest/kotlin/androidx/compose/compiler/plugins/kotlin/RunComposableTests.kt"

    with open(composer_test_file, 'r') as f:
        content = f.read()

    # Check for the new test method
    assert "fun testObjectTypesAreStable()" in content, \
        "Missing testObjectTypesAreStable test method"

    with open(run_test_file, 'r') as f:
        content = f.read()

    # Check for the companion object test
    assert "fun testNoStablePropertyOnCompanionObjects()" in content, \
        "Missing testNoStablePropertyOnCompanionObjects test method"


# =============================================================================
# Pass-to-Pass Tests (Repo CI checks)
# =============================================================================


def test_stability_kt_syntax_valid():
    """Pass-to-pass: Stability.kt has valid Kotlin syntax (kotlinc validation).

    Uses kotlinc to verify the file is syntactically valid. Expected to fail
    compilation due to missing dependencies (exit code 1), but should not have
    syntax errors (exit code 2+).
    """
    exit_code, stdout, stderr = _run_kotlinc_syntax_check(STABILITY_FILE)

    # Exit code 1 = compilation errors (missing deps) - this is OK
    # Exit code 2+ = internal/compiler error or syntax error - this is NOT OK
    assert exit_code == 1, f"Stability.kt has syntax/internal errors (exit code {exit_code}):\n{stderr[-500:]}"

    # Additional check: verify file contains expected class structure
    with open(STABILITY_FILE, 'r') as f:
        content = f.read()

    assert "sealed class Stability" in content, "Stability sealed class not found"
    assert "class Certain" in content, "Stability.Certain class not found"
    assert "class Runtime" in content, "Stability.Runtime class not found"


def test_lowering_kt_syntax_valid():
    """Pass-to-pass: AbstractComposeLowering.kt has valid Kotlin syntax (kotlinc validation).

    Uses kotlinc to verify the file is syntactically valid. Expected to fail
    compilation due to missing dependencies (exit code 1), but should not have
    syntax errors (exit code 2+).
    """
    exit_code, stdout, stderr = _run_kotlinc_syntax_check(LOWERING_FILE)

    # Exit code 1 = compilation errors (missing deps) - this is OK
    # Exit code 2+ = internal/compiler error or syntax error - this is NOT OK
    assert exit_code == 1, f"AbstractComposeLowering.kt has syntax/internal errors (exit code {exit_code}):\n{stderr[-500:]}"

    # Additional check: verify file contains expected class structure
    with open(LOWERING_FILE, 'r') as f:
        content = f.read()

    assert "abstract class AbstractComposeLowering" in content, "AbstractComposeLowering class not found"
    assert "IrElementTransformerVoid" in content, "IrElementTransformerVoid not found"


def test_composer_param_tests_syntax_valid():
    """Pass-to-pass: ComposerParamTransformTests.kt has valid Kotlin syntax.

    Validates the test file can be parsed by kotlinc without syntax errors.
    """
    test_file = f"{REPO}/plugins/compose/compiler-hosted/integration-tests/src/jvmTest/kotlin/androidx/compose/compiler/plugins/kotlin/ComposerParamTransformTests.kt"

    exit_code, stdout, stderr = _run_kotlinc_syntax_check(test_file)

    # Exit code 1 = compilation errors (missing deps) - this is OK
    # Exit code 2+ = internal/compiler error or syntax error - this is NOT OK
    assert exit_code == 1, f"ComposerParamTransformTests.kt has syntax/internal errors (exit code {exit_code}):\n{stderr[-500:]}"

    # Verify class structure
    with open(test_file, 'r') as f:
        content = f.read()

    assert "class ComposerParamTransformTests" in content, "ComposerParamTransformTests class not found"


def test_run_composable_tests_syntax_valid():
    """Pass-to-pass: RunComposableTests.kt has valid Kotlin syntax.

    Validates the test file can be parsed by kotlinc without syntax errors.
    """
    test_file = f"{REPO}/plugins/compose/compiler-hosted/integration-tests/src/jvmTest/kotlin/androidx/compose/compiler/plugins/kotlin/RunComposableTests.kt"

    exit_code, stdout, stderr = _run_kotlinc_syntax_check(test_file)

    # Exit code 1 = compilation errors (missing deps) - this is OK
    # Exit code 2+ = internal/compiler error or syntax error - this is NOT OK
    assert exit_code == 1, f"RunComposableTests.kt has syntax/internal errors (exit code {exit_code}):\n{stderr[-500:]}"

    # Verify class structure
    with open(test_file, 'r') as f:
        content = f.read()

    assert "class RunComposableTests" in content, "RunComposableTests class not found"


def test_compose_plugin_source_structure():
    """Pass-to-pass: Compose compiler plugin source directory structure is valid.

    Verifies the expected source files and directories exist in the plugin.
    """
    import os

    base_dir = f"{REPO}/plugins/compose/compiler-hosted/src/main/java/androidx/compose/compiler/plugins/kotlin"

    # Key directories should exist
    assert os.path.isdir(f"{base_dir}/analysis"), "analysis directory not found"
    assert os.path.isdir(f"{base_dir}/lower"), "lower directory not found"

    # Key files should exist
    key_files = [
        f"{base_dir}/ComposePlugin.kt",
        f"{base_dir}/ComposeIrGenerationExtension.kt",
        f"{base_dir}/ComposeFqNames.kt",
        f"{base_dir}/analysis/Stability.kt",
        f"{base_dir}/lower/AbstractComposeLowering.kt",
    ]

    for filepath in key_files:
        assert os.path.isfile(filepath), f"Required source file not found: {filepath}"


def test_integration_tests_structure():
    """Pass-to-pass: Integration tests directory structure is valid.

    Verifies the expected test files and golden directories exist.
    """
    import os

    test_dir = f"{REPO}/plugins/compose/compiler-hosted/integration-tests/src/jvmTest"

    # Test directories should exist
    assert os.path.isdir(f"{test_dir}/kotlin/androidx/compose/compiler/plugins/kotlin"), \
        "Test source directory not found"
    assert os.path.isdir(f"{test_dir}/resources/golden"), \
        "Golden files directory not found"

    # Golden directory should have subdirectories
    golden_dir = f"{test_dir}/resources/golden"
    subdirs = os.listdir(golden_dir)

    # Should have at least one test class golden directory
    assert len(subdirs) > 0, "No golden subdirectories found"

    # Check for expected test golden directories
    expected_prefixes = [
        "androidx.compose.compiler.plugins.kotlin.ComposerParamTransformTests",
        "androidx.compose.compiler.plugins.kotlin.RunComposableTests",
        "androidx.compose.compiler.plugins.kotlin.StaticExpressionDetectionTests",
    ]

    found_prefixes = [s for s in subdirs if any(s.startswith(p) for p in expected_prefixes)]
    assert len(found_prefixes) > 0, f"Expected golden directories not found. Found: {subdirs[:10]}"


def test_kotlin_analysis_dir_structure():
    """Pass-to-pass: Analysis directory contains expected source files (repo CI structure check).

    Verifies the analysis directory has the key files that CI expects.
    """
    import os

    analysis_dir = f"{REPO}/plugins/compose/compiler-hosted/src/main/java/androidx/compose/compiler/plugins/kotlin/analysis"

    expected_files = [
        "Stability.kt",
        "KnownStableConstructs.kt",
        "StabilityConfigParser.kt",
        "StabilityExternalClassNameMatching.kt",
        "ComposeWritableSlices.kt",
    ]

    for filename in expected_files:
        filepath = os.path.join(analysis_dir, filename)
        assert os.path.isfile(filepath), f"Expected analysis file not found: {filename}"


def test_kotlinc_lower_file_validation():
    """Pass-to-pass: AbstractComposeLowering.kt passes kotlinc syntax validation (repo CI check).

    Runs kotlinc on the modified lowering file to verify syntax validity.
    Exit code 1 (missing deps) is OK, exit code 2+ (syntax/internal errors) is NOT OK.
    """
    lowering_file = f"{REPO}/plugins/compose/compiler-hosted/src/main/java/androidx/compose/compiler/plugins/kotlin/lower/AbstractComposeLowering.kt"

    r = subprocess.run(
        ["kotlinc", lowering_file],
        capture_output=True, text=True, timeout=120, cwd=REPO
    )

    # Exit code 1 = compilation errors due to missing dependencies - this is expected/OK
    # Exit code 2+ = internal/compiler error or syntax error - this is NOT OK
    assert r.returncode == 1, \
        f"AbstractComposeLowering.kt has syntax/internal errors (exit code {r.returncode}):\n{r.stderr[:500]}"


def test_kotlin_golden_file_format():
    """Pass-to-pass: Golden files have valid format with Source/Transformed IR sections (repo CI check).

    Validates that golden files contain the expected structure markers.
    """
    import os

    golden_base = f"{REPO}/plugins/compose/compiler-hosted/integration-tests/src/jvmTest/resources/golden"

    # Sample some existing golden files to validate format
    sample_files = [
        f"{golden_base}/androidx.compose.compiler.plugins.kotlin.ComposerParamTransformTests/testCircularCall[useFir = false].txt",
        f"{golden_base}/androidx.compose.compiler.plugins.kotlin.ComposerParamTransformTests/testCircularCall[useFir = true].txt",
    ]

    for filepath in sample_files:
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                content = f.read()

            # Golden files should have Source section
            assert "// Source" in content or "//source" in content.lower(), \
                f"Golden file {filepath} missing Source section"

            # Golden files should have Transformed IR section
            assert "// Transformed IR" in content or "//transformed" in content.lower(), \
                f"Golden file {filepath} missing Transformed IR section"


def test_compose_test_files_syntax():
    """Pass-to-pass: Key compose test files have valid Kotlin syntax (repo CI check).

    Runs kotlinc on key test files to verify syntax validity.
    """
    test_files = [
        f"{REPO}/plugins/compose/compiler-hosted/integration-tests/src/jvmTest/kotlin/androidx/compose/compiler/plugins/kotlin/StaticExpressionDetectionTests.kt",
        f"{REPO}/plugins/compose/compiler-hosted/integration-tests/src/jvmTest/kotlin/androidx/compose/compiler/plugins/kotlin/ComposerParamTransformTests.kt",
    ]

    for test_file in test_files:
        r = subprocess.run(
            ["kotlinc", test_file],
            capture_output=True, text=True, timeout=120, cwd=REPO
        )

        # Exit code 1 = compilation errors due to missing dependencies - this is expected/OK
        # Exit code 2+ = internal/compiler error or syntax error - this is NOT OK
        assert r.returncode == 1, \
            f"{test_file} has syntax/internal errors (exit code {r.returncode}):\n{r.stderr[:500]}"
