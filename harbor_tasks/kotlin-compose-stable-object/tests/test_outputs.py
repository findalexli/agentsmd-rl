"""Test outputs for Kotlin Compose compiler stability fix."""

import subprocess
import sys

REPO = "/workspace/kotlin"
STABILITY_FILE = f"{REPO}/plugins/compose/compiler-hosted/src/main/java/androidx/compose/compiler/plugins/kotlin/analysis/Stability.kt"
LOWERING_FILE = f"{REPO}/plugins/compose/compiler-hosted/src/main/java/androidx/compose/compiler/plugins/kotlin/lower/AbstractComposeLowering.kt"


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
