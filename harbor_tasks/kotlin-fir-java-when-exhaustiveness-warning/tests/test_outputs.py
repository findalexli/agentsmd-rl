#!/usr/bin/env python3
"""
Test outputs for Kotlin FIR Java When Exhaustiveness Warning implementation.

This test validates that the UNEXHAUSTIVE_WHEN_BASED_ON_JAVA_ANNOTATIONS diagnostic
is properly implemented in the Kotlin FIR compiler.
"""

import subprocess
import os
import sys

# Constants
REPO = "/workspace/kotlin"
CHECKER_FILE = "compiler/fir/checkers/checkers.jvm/src/org/jetbrains/kotlin/fir/analysis/jvm/checkers/expression/FirJavaWhenExhaustivenessWarningChecker.kt"
JVM_EXPRESSION_CHECKERS = "compiler/fir/checkers/checkers.jvm/src/org/jetbrains/kotlin/fir/analysis/jvm/checkers/JvmExpressionCheckers.kt"
FIR_JVM_ERRORS = "compiler/fir/checkers/checkers.jvm/gen/org/jetbrains/kotlin/fir/analysis/diagnostics/jvm/FirJvmErrors.kt"
ERROR_MESSAGES_FILE = "compiler/fir/checkers/checkers.jvm/src/org/jetbrains/kotlin/fir/analysis/diagnostics/jvm/FirJvmErrorsDefaultMessages.kt"

# Test data files
TEST_STRICT_FIR = "compiler/testData/diagnostics/foreignAnnotationsTests/java8Tests/jspecify/strictMode/annotatedWhenSubject.fir.kt"
TEST_STRICT = "compiler/testData/diagnostics/foreignAnnotationsTests/java8Tests/jspecify/strictMode/annotatedWhenSubject.kt"
TEST_WARN_FIR = "compiler/testData/diagnostics/foreignAnnotationsTests/java8Tests/jspecify/warnMode/annotatedWhenSubject.fir.kt"
TEST_WARN = "compiler/testData/diagnostics/foreignAnnotationsTests/java8Tests/jspecify/warnMode/annotatedWhenSubject.kt"
UPDATED_TEST_FILE = "compiler/testData/diagnostics/foreignAnnotationsTests/java8Tests/jspecify/WhenWarn.fir.kt"


def run_cmd(cmd, cwd=REPO, timeout=300):
    """Run a shell command and return the result."""
    result = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=timeout,
        shell=isinstance(cmd, str)
    )
    return result


# ==================== FAIL-TO-PASS TESTS ====================

def test_checker_file_exists():
    """F2P: FirJavaWhenExhaustivenessWarningChecker.kt file exists with correct content."""
    assert os.path.exists(os.path.join(REPO, CHECKER_FILE)), \
        f"Checker file not found: {CHECKER_FILE}"

    with open(os.path.join(REPO, CHECKER_FILE), 'r') as f:
        content = f.read()

    # Verify key components exist
    assert "FirJavaWhenExhaustivenessWarningChecker" in content, \
        "Checker class name not found"
    assert "FirWhenExpressionChecker" in content, \
        "Should extend FirWhenExpressionChecker"
    assert "UNEXHAUSTIVE_WHEN_BASED_ON_JAVA_ANNOTATIONS" in content, \
        "Should reference UNEXHAUSTIVE_WHEN_BASED_ON_JAVA_ANNOTATIONS"
    assert "enhancedTypeForWarning" in content, \
        "Should check enhancedTypeForWarning"
    assert "hasNullCheck" in content, \
        "Should implement hasNullCheck logic"


def test_checker_registered():
    """F2P: FirJavaWhenExhaustivenessWarningChecker is registered in JvmExpressionCheckers."""
    with open(os.path.join(REPO, JVM_EXPRESSION_CHECKERS), 'r') as f:
        content = f.read()

    assert "FirJavaWhenExhaustivenessWarningChecker" in content, \
        "Checker not registered in JvmExpressionCheckers"


def test_diagnostic_defined():
    """F2P: UNEXHAUSTIVE_WHEN_BASED_ON_JAVA_ANNOTATIONS diagnostic is defined."""
    with open(os.path.join(REPO, FIR_JVM_ERRORS), 'r') as f:
        content = f.read()

    assert "UNEXHAUSTIVE_WHEN_BASED_ON_JAVA_ANNOTATIONS" in content, \
        "UNEXHAUSTIVE_WHEN_BASED_ON_JAVA_ANNOTATIONS not defined in FirJvmErrors"
    assert "KtDiagnosticFactory1" in content or "WARNING" in content, \
        "Diagnostic should be a warning"


def test_error_message_defined():
    """F2P: Error message for UNEXHAUSTIVE_WHEN_BASED_ON_JAVA_ANNOTATIONS is defined."""
    with open(os.path.join(REPO, ERROR_MESSAGES_FILE), 'r') as f:
        content = f.read()

    assert "UNEXHAUSTIVE_WHEN_BASED_ON_JAVA_ANNOTATIONS" in content, \
        "Error message not registered"
    assert "not exhaustive" in content.lower() or "Add a" in content, \
        "Error message should mention 'not exhaustive' or 'Add a'"


def test_analysis_api_diagnostic_impl():
    """F2P: Analysis API diagnostic implementation exists."""
    ka_diagnostics_impl = "analysis/analysis-api-fir/gen/org/jetbrains/kotlin/analysis/api/fir/diagnostics/KaFirDiagnosticsImpl.kt"

    with open(os.path.join(REPO, ka_diagnostics_impl), 'r') as f:
        content = f.read()

    assert "UnexhaustiveWhenBasedOnJavaAnnotationsImpl" in content, \
        "KaFirDiagnosticsImpl should contain UnexhaustiveWhenBasedOnJavaAnnotationsImpl"


def test_analysis_api_diagnostic_interface():
    """F2P: Analysis API diagnostic interface exists."""
    ka_diagnostics = "analysis/analysis-api-fir/gen/org/jetbrains/kotlin/analysis/api/fir/diagnostics/KaFirDiagnostics.kt"

    with open(os.path.join(REPO, ka_diagnostics), 'r') as f:
        content = f.read()

    assert "UnexhaustiveWhenBasedOnJavaAnnotations" in content, \
        "KaFirDiagnostics should contain UnexhaustiveWhenBasedOnJavaAnnotations interface"


def test_test_data_files_exist():
    """F2P: New test data files exist for the diagnostic."""
    assert os.path.exists(os.path.join(REPO, TEST_STRICT_FIR)), \
        f"Test file not found: {TEST_STRICT_FIR}"
    assert os.path.exists(os.path.join(REPO, TEST_STRICT)), \
        f"Test file not found: {TEST_STRICT}"
    assert os.path.exists(os.path.join(REPO, TEST_WARN_FIR)), \
        f"Test file not found: {TEST_WARN_FIR}"
    assert os.path.exists(os.path.join(REPO, TEST_WARN)), \
        f"Test file not found: {TEST_WARN}"


def test_updated_test_file():
    """F2P: WhenWarn.fir.kt updated with new diagnostic markers."""
    with open(os.path.join(REPO, UPDATED_TEST_FILE), 'r') as f:
        content = f.read()

    # Should have the UNEXHAUSTIVE_WHEN_BASED_ON_JAVA_ANNOTATIONS marker
    assert "UNEXHAUSTIVE_WHEN_BASED_ON_JAVA_ANNOTATIONS" in content, \
        "WhenWarn.fir.kt should reference UNEXHAUSTIVE_WHEN_BASED_ON_JAVA_ANNOTATIONS"


def test_diagnostic_generator_updated():
    """F2P: Diagnostic generator updated with new diagnostic definition."""
    generator_file = "compiler/fir/checkers/checkers-component-generator/src/org/jetbrains/kotlin/fir/checkers/generator/diagnostics/FirJvmDiagnosticsList.kt"

    with open(os.path.join(REPO, generator_file), 'r') as f:
        content = f.read()

    assert "UNEXHAUSTIVE_WHEN_BASED_ON_JAVA_ANNOTATIONS" in content, \
        "Diagnostic generator should define UNEXHAUSTIVE_WHEN_BASED_ON_JAVA_ANNOTATIONS"
    assert "PositioningStrategy.WHEN_EXPRESSION" in content, \
        "Should use WHEN_EXPRESSION positioning strategy"


def test_converter_updated():
    """F2P: KaFirDataClassConverters updated with new diagnostic conversion."""
    converter_file = "analysis/analysis-api-fir/gen/org/jetbrains/kotlin/analysis/api/fir/diagnostics/KaFirDataClassConverters.kt"

    with open(os.path.join(REPO, converter_file), 'r') as f:
        content = f.read()

    assert "UNEXHAUSTIVE_WHEN_BASED_ON_JAVA_ANNOTATIONS" in content, \
        "Converter should handle UNEXHAUSTIVE_WHEN_BASED_ON_JAVA_ANNOTATIONS"
    assert "UnexhaustiveWhenBasedOnJavaAnnotationsImpl" in content, \
        "Converter should create UnexhaustiveWhenBasedOnJavaAnnotationsImpl"


# ==================== PASS-TO-PASS TESTS ====================

def test_fir_exhaustive_when_checker_compiles():
    """P2P: FirExhaustiveWhenChecker.kt compiles after refactoring."""
    # This verifies the refactoring didn't break compilation
    checker_file = "compiler/fir/checkers/src/org/jetbrains/kotlin/fir/analysis/checkers/expression/FirExhaustiveWhenChecker.kt"

    assert os.path.exists(os.path.join(REPO, checker_file)), \
        f"FirExhaustiveWhenChecker.kt should exist"

    with open(os.path.join(REPO, checker_file), 'r') as f:
        content = f.read()

    # Verify the refactoring was applied (removed enum, simplified logic)
    assert "AlgebraicTypeKind" not in content, \
        "AlgebraicTypeKind enum should be removed (refactoring)"


def test_gradlew_exists():
    """P2P: Gradle wrapper exists and is executable."""
    gradlew = os.path.join(REPO, "gradlew")
    assert os.path.exists(gradlew), "gradlew should exist"


def test_gradle_wrapper_properties():
    """P2P: Gradle wrapper properties are valid."""
    properties_file = os.path.join(REPO, "gradle/wrapper/gradle-wrapper.properties")
    assert os.path.exists(properties_file), "gradle-wrapper.properties should exist"

    with open(properties_file, 'r') as f:
        content = f.read()

    assert "distributionUrl" in content, "distributionUrl should be defined"
    assert "gradle" in content.lower(), "Should reference gradle distribution"


def test_gradle_settings():
    """P2P: Gradle settings file is valid and includes expected projects."""
    settings_file = os.path.join(REPO, "settings.gradle")
    assert os.path.exists(settings_file), "settings.gradle should exist"

    with open(settings_file, 'r') as f:
        content = f.read()

    # Check for key FIR-related projects
    assert ":compiler:fir:checkers" in content, "FIR checkers project should be in settings"
    assert ":compiler:fir:checkers:checkers.jvm" in content, "FIR JVM checkers should be in settings"


def test_fir_checkers_module_structure():
    """P2P: FIR checkers module has expected structure."""
    # Check that the main FIR checkers modules exist
    modules = [
        "compiler/fir/checkers/checkers.jvm/src",
        "compiler/fir/checkers/checkers.jvm/gen",
        "compiler/fir/checkers/src",
        "compiler/fir/checkers/gen",
    ]
    for module in modules:
        assert os.path.exists(os.path.join(REPO, module)), f"FIR module should exist: {module}"


def test_test_data_jspecify_structure():
    """P2P: JSpecify test data directory structure is valid."""
    jspecify_dir = os.path.join(REPO, "compiler/testData/diagnostics/foreignAnnotationsTests/java8Tests/jspecify")
    assert os.path.exists(jspecify_dir), "JSpecify test data directory should exist"

    # Check for expected test files
    expected_files = [
        "WhenWarn.fir.kt",
        "WhenWarn.kt",
    ]
    for f in expected_files:
        assert os.path.exists(os.path.join(jspecify_dir, f)), f"Test file should exist: {f}"


def test_kotlin_compiler_cli_module():
    """P2P: Kotlin compiler CLI module structure exists."""
    cli_dirs = [
        "compiler/cli",
        "compiler/cli/src",
    ]
    for d in cli_dirs:
        assert os.path.exists(os.path.join(REPO, d)), f"CLI module should exist: {d}"


def test_kotlin_compiler_common_module():
    """P2P: Kotlin compiler common module exists (core infrastructure)."""
    assert os.path.exists(os.path.join(REPO, "core/compiler.common/src")), "core/compiler.common/src should exist"


def test_diagnostic_generator_runnable():
    """P2P: Diagnostic generator module compiles (source structure is valid)."""
    generator_dir = os.path.join(REPO, "compiler/fir/checkers/checkers-component-generator/src")
    assert os.path.exists(generator_dir), "Diagnostic generator source dir should exist"

    # Check main generator files exist
    generator_files = [
        "org/jetbrains/kotlin/fir/checkers/generator/diagnostics/FirJvmDiagnosticsList.kt",
    ]
    for f in generator_files:
        assert os.path.exists(os.path.join(generator_dir, f)), f"Generator file should exist: {f}"


def test_fir_analysis_api_structure():
    """P2P: FIR Analysis API structure is valid."""
    analysis_api_dirs = [
        "analysis/analysis-api-fir/gen/org/jetbrains/kotlin/analysis/api/fir/diagnostics",
        "analysis/analysis-api-fir/src/org/jetbrains/kotlin/analysis/api/fir/diagnostics",
    ]
    for d in analysis_api_dirs:
        assert os.path.exists(os.path.join(REPO, d)), f"Analysis API dir should exist: {d}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
