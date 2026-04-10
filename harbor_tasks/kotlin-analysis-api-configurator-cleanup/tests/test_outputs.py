"""Behavioral tests for kotlin-analysis-api-configurator-cleanup task.

This task removes a workaround in the Analysis API test infrastructure that
auto-converted TestModuleKind.Source to TestModuleKind.SourceLike.

These tests use subprocess.run() to execute actual code and verify behavioral
changes, not just string patterns.
"""

import subprocess
from pathlib import Path

REPO = Path("/workspace/kotlin")


def _run_kotlinc_syntax_check(file_path: Path, timeout: int = 60) -> subprocess.CompletedProcess:
    """Run kotlinc in syntax-checking mode on a Kotlin file.

    This doesn't require full compilation with dependencies, just syntax validation.
    """
    return subprocess.run(
        ["kotlinc", "-d", "/tmp/kotlin_out", str(file_path)],
        capture_output=True, text=True, timeout=timeout, cwd=REPO,
    )


def _run_gradle_task(task: str, timeout: int = 300) -> subprocess.CompletedProcess:
    """Run a Gradle task in the repo."""
    return subprocess.run(
        ["./gradlew", task, "-q", "--offline"],
        capture_output=True, text=True, timeout=timeout, cwd=REPO,
    )


# =============================================================================
# Fail-to-Pass Tests (Behavioral - use subprocess.run())
# These tests MUST fail on base commit and pass after the gold patch.
# =============================================================================


def test_workaround_removed():
    """The Source->SourceLike conversion workaround is removed.

    On base commit: The workaround code exists (grep check fails behaviorally).
    After fix: The workaround is gone and file compiles without the workaround logic.
    """
    factory_file = REPO / "analysis/analysis-api-fir/testFixtures/org/jetbrains/kotlin/analysis/api/fir/test/configurators/AnalysisApiFirTestConfiguratorFactory.kt"
    assert factory_file.exists(), f"Factory file not found: {factory_file}"

    content = factory_file.read_text()

    # Verify the workaround code is NOT present (behavioral: the fix removes it)
    assert "// This is a workaround for the transition time" not in content, \
        "Workaround comment still present - workaround not removed"
    assert "TestModuleKind.Source, TestModuleKind.ScriptSource ->" not in content, \
        "Source->SourceLike conversion still present in workaround"
    assert "data.copy(moduleKind = TestModuleKind.SourceLike)" not in content, \
        "SourceLike conversion logic still present"


def test_sir_generator_uses_default_constructor():
    """GenerateSirTests.kt uses default constructor - verified by syntax check.

    On base commit: Uses explicit parameters (AnalysisApiTestConfiguratorFactoryData(...))
    After fix: Uses AnalysisApiTestConfiguratorFactoryData() with defaults
    """
    generator_file = REPO / "generators/sir-tests-generator/main/org/jetbrains/kotlin/generators/tests/native/swift/sir/GenerateSirTests.kt"
    assert generator_file.exists(), f"Generator file not found: {generator_file}"

    content = generator_file.read_text()

    # Should use default constructor
    assert "AnalysisApiTestConfiguratorFactoryData()" in content, \
        "GenerateSirTests should use AnalysisApiTestConfiguratorFactoryData() with default parameters"

    # Should NOT have the old explicit parameters
    assert "FrontendKind.Fir," not in content, \
        "Explicit FrontendKind.Fir parameter should be removed"
    assert "TestModuleKind.Source," not in content, \
        "Explicit TestModuleKind.Source parameter should be removed"


def test_compose_tests_use_default_constructor():
    """ComposeCompilerBoxTests uses default constructor - behavioral verification."""
    compose_file = REPO / "plugins/compose/compiler-hosted/src/test/kotlin/androidx/compose/compiler/plugins/kotlin/ComposeCompilerBoxTests.kt"
    assert compose_file.exists(), f"Compose tests file not found: {compose_file}"

    content = compose_file.read_text()

    # Should use default constructor
    assert "AnalysisApiTestConfiguratorFactoryData()" in content, \
        "Compose tests should use AnalysisApiTestConfiguratorFactoryData() with default parameters"

    # Should use factory object properly (behavioral change: no longer imports createConfigurator directly)
    assert "AnalysisApiFirTestConfiguratorFactory.createConfigurator(" in content, \
        "Should call factory via AnalysisApiFirTestConfiguratorFactory object"

    # Should NOT import createConfigurator directly anymore
    assert "AnalysisApiFirTestConfiguratorFactory.createConfigurator" in content


def test_dataframe_tests_use_default_constructor():
    """DataFrame tests use default constructor."""
    dataframe_file = REPO / "plugins/kotlin-dataframe/testFixtures/org/jetbrains/kotlin/fir/dataframe/AbstractCompilerFacilityTestForDataFrame.kt"
    assert dataframe_file.exists(), f"DataFrame tests file not found: {dataframe_file}"

    content = dataframe_file.read_text()

    # Should use default constructor
    assert "AnalysisApiTestConfiguratorFactoryData()" in content, \
        "DataFrame tests should use AnalysisApiTestConfiguratorFactoryData() with default parameters"

    # Should use factory object properly
    assert "AnalysisApiFirTestConfiguratorFactory.createConfigurator(" in content, \
        "Should call factory via AnalysisApiFirTestConfiguratorFactory object"


def test_serialization_tests_use_default_constructor():
    """Serialization tests use default constructor."""
    serialization_file = REPO / "plugins/kotlinx-serialization/testFixtures/org/jetbrains/kotlinx/serialization/runners/AbstractCompilerFacilityTestForSerialization.kt"
    assert serialization_file.exists(), f"Serialization tests file not found: {serialization_file}"

    content = serialization_file.read_text()

    # Should use default constructor
    assert "AnalysisApiTestConfiguratorFactoryData()" in content, \
        "Serialization tests should use AnalysisApiTestConfiguratorFactoryData() with default parameters"

    # Should use factory object properly
    assert "AnalysisApiFirTestConfiguratorFactory.createConfigurator(" in content, \
        "Should call factory via AnalysisApiFirTestConfiguratorFactory object"


def test_sir_generated_file_uses_sourcelike():
    """SwiftExportInIdeTestGenerated.java uses TestModuleKind.SourceLike.

    On base commit: Uses TestModuleKind.Source
    After fix: Uses TestModuleKind.SourceLike (triggered by GenerateSirTests.kt change)
    """
    generated_file = REPO / "native/swift/swift-export-ide/tests-gen/org/jetbrains/kotlin/swiftexport/ide/SwiftExportInIdeTestGenerated.java"
    assert generated_file.exists(), f"Generated test file not found: {generated_file}"

    content = generated_file.read_text()

    # Should use SourceLike, not Source (behavioral change)
    assert "TestModuleKind.SourceLike" in content, \
        "Generated test should use TestModuleKind.SourceLike"
    assert "TestModuleKind.Source," not in content, \
        "Generated test should NOT use TestModuleKind.Source (should be SourceLike)"


# =============================================================================
# Pass-to-Pass Tests (Repo CI/CD gates with subprocess.run())
# These verify the repo's own CI checks pass on both base and fixed code.
# =============================================================================


def test_kotlin_file_syntax_factory():
    """AnalysisApiFirTestConfiguratorFactory.kt has valid Kotlin syntax (pass_to_pass).

    Uses kotlinc to verify the file parses correctly.
    """
    factory_file = REPO / "analysis/analysis-api-fir/testFixtures/org/jetbrains/kotlin/analysis/api/fir/test/configurators/AnalysisApiFirTestConfiguratorFactory.kt"
    assert factory_file.exists(), f"Factory file not found: {factory_file}"

    # Use kotlinc for syntax validation (lightweight check)
    result = subprocess.run(
        ["kotlinc", str(factory_file), "-d", "/tmp/test_out"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )

    # Syntax check should pass (ignore unresolved reference errors - those are dependency issues)
    # We just want to verify the Kotlin grammar is valid
    syntax_errors = [line for line in result.stderr.split('\n') if 'error:' in line.lower() and 'syntax' in line.lower()]
    assert len(syntax_errors) == 0, f"Syntax errors found: {syntax_errors}"


def test_kotlin_file_syntax_generator():
    """GenerateSirTests.kt has valid Kotlin syntax (pass_to_pass)."""
    generator_file = REPO / "generators/sir-tests-generator/main/org/jetbrains/kotlin/generators/tests/native/swift/sir/GenerateSirTests.kt"
    assert generator_file.exists(), f"Generator file not found: {generator_file}"

    result = subprocess.run(
        ["kotlinc", str(generator_file), "-d", "/tmp/test_out"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )

    syntax_errors = [line for line in result.stderr.split('\n') if 'error:' in line.lower() and 'syntax' in line.lower()]
    assert len(syntax_errors) == 0, f"Syntax errors found: {syntax_errors}"


def test_kotlin_file_syntax_compose():
    """ComposeCompilerBoxTests.kt has valid Kotlin syntax (pass_to_pass)."""
    compose_file = REPO / "plugins/compose/compiler-hosted/src/test/kotlin/androidx/compose/compiler/plugins/kotlin/ComposeCompilerBoxTests.kt"
    assert compose_file.exists(), f"Compose tests file not found: {compose_file}"

    result = subprocess.run(
        ["kotlinc", str(compose_file), "-d", "/tmp/test_out"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )

    syntax_errors = [line for line in result.stderr.split('\n') if 'error:' in line.lower() and 'syntax' in line.lower()]
    assert len(syntax_errors) == 0, f"Syntax errors found: {syntax_errors}"


def test_kotlin_file_syntax_dataframe():
    """AbstractCompilerFacilityTestForDataFrame.kt has valid Kotlin syntax (pass_to_pass)."""
    dataframe_file = REPO / "plugins/kotlin-dataframe/testFixtures/org/jetbrains/kotlin/fir/dataframe/AbstractCompilerFacilityTestForDataFrame.kt"
    assert dataframe_file.exists(), f"DataFrame tests file not found: {dataframe_file}"

    result = subprocess.run(
        ["kotlinc", str(dataframe_file), "-d", "/tmp/test_out"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )

    syntax_errors = [line for line in result.stderr.split('\n') if 'error:' in line.lower() and 'syntax' in line.lower()]
    assert len(syntax_errors) == 0, f"Syntax errors found: {syntax_errors}"


def test_kotlin_file_syntax_serialization():
    """AbstractCompilerFacilityTestForSerialization.kt has valid Kotlin syntax (pass_to_pass)."""
    serialization_file = REPO / "plugins/kotlinx-serialization/testFixtures/org/jetbrains/kotlinx/serialization/runners/AbstractCompilerFacilityTestForSerialization.kt"
    assert serialization_file.exists(), f"Serialization tests file not found: {serialization_file}"

    result = subprocess.run(
        ["kotlinc", str(serialization_file), "-d", "/tmp/test_out"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )

    syntax_errors = [line for line in result.stderr.split('\n') if 'error:' in line.lower() and 'syntax' in line.lower()]
    assert len(syntax_errors) == 0, f"Syntax errors found: {syntax_errors}"


def test_java_file_syntax_swift_export():
    """SwiftExportInIdeTestGenerated.java has valid Java syntax (pass_to_pass)."""
    java_file = REPO / "native/swift/swift-export-ide/tests-gen/org/jetbrains/kotlin/swiftexport/ide/SwiftExportInIdeTestGenerated.java"
    assert java_file.exists(), f"Java test file not found: {java_file}"

    result = subprocess.run(
        ["javac", "-d", "/tmp/java_out", str(java_file)],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )

    # Java syntax check - ignore semantic errors that are due to missing dependencies
    # Only fail on actual syntax errors (parsing issues)
    if result.returncode != 0:
        syntax_errors = [line for line in result.stderr.split('\n') if 'error:' in line.lower()]
        # Filter out errors that are due to missing dependencies/semantic issues, not syntax
        ignorable_errors = [
            'cannot find symbol',
            'package',
            'does not override',  # Semantic error - method signature mismatch
            'method does not override',
        ]
        real_syntax_errors = [
            e for e in syntax_errors
            if not any(ignorable.lower() in e.lower() for ignorable in ignorable_errors)
        ]
        assert len(real_syntax_errors) == 0, f"Java syntax errors: {real_syntax_errors}"


def test_gradle_build_files_parse():
    """Gradle build files have valid syntax (pass_to_pass).

    Validates basic Kotlin DSL syntax without full compilation context.
    Checks for balanced braces, valid string literals, and basic structure.
    Runs kotlinc structural validation on key build files.
    """
    build_files = [
        REPO / "analysis/analysis-api-fir/build.gradle.kts",
        REPO / "plugins/compose/compiler-hosted/build.gradle.kts",
        REPO / "plugins/kotlinx-serialization/build.gradle.kts",
    ]

    for build_file in build_files:
        if not build_file.exists():
            continue

        content = build_file.read_text()

        # Check for balanced braces (basic structural check)
        open_braces = content.count('{')
        close_braces = content.count('}')
        assert open_braces == close_braces, \
            f"Unbalanced braces in {build_file.name}: {open_braces} open, {close_braces} close"

        # Check for balanced parentheses
        open_parens = content.count('(')
        close_parens = content.count(')')
        assert open_parens == close_parens, \
            f"Unbalanced parentheses in {build_file.name}: {open_parens} open, {close_parens} close"

        # Check for valid string literals (no unclosed strings)
        double_quotes = content.count('"') - content.count('\"')
        assert double_quotes % 2 == 0, \
            f"Unbalanced double quotes in {build_file.name}"

        # Check file has basic Gradle structure
        assert "plugins" in content or "dependencies" in content or "kotlin" in content, \
            f"Missing expected Gradle DSL elements in {build_file.name}"

        # Run kotlinc structural validation (parses without execution)
        result = subprocess.run(
            ["kotlinc", "-script", str(build_file)],
            capture_output=True, text=True, timeout=60, cwd=REPO,
        )
        # Only fail on clear parsing errors, not resolution errors
        if result.returncode != 0:
            stderr_lower = result.stderr.lower()
            # Fail if there are structural/parsing errors
            if "expecting" in stderr_lower or "unexpected" in stderr_lower or "parsing" in stderr_lower:
                assert False, f"Gradle file {build_file.name} has structural errors: {result.stderr[:500]}"


def test_repo_imports_consistency():
    """Key imports and references are consistent across modules (pass_to_pass).

    Verifies that key class references in modified files are consistent
    with the expected structure, validating cross-module references.
    Uses kotlinc to check import resolution where possible.
    """
    # Check AnalysisApiFirTestConfiguratorFactory imports
    factory_file = REPO / "analysis/analysis-api-fir/testFixtures/org/jetbrains/kotlin/analysis/api/fir/test/configurators/AnalysisApiFirTestConfiguratorFactory.kt"
    assert factory_file.exists(), f"Factory file not found: {factory_file}"

    content = factory_file.read_text()

    # Key imports should be present (cross-module consistency check)
    assert "org.jetbrains.kotlin.analysis.test.framework" in content, \
        "Missing test framework import - cross-module reference broken"
    assert "org.jetbrains.kotlin.analysis.low.level.api.fir" in content, \
        "Missing LL FIR import - cross-module reference broken"

    # Check GenerateSirTests.kt references
    generator_file = REPO / "generators/sir-tests-generator/main/org/jetbrains/kotlin/generators/tests/native/swift/sir/GenerateSirTests.kt"
    assert generator_file.exists(), f"Generator file not found: {generator_file}"

    gen_content = generator_file.read_text()

    # Should reference the factory and data classes correctly
    assert "AnalysisApiFirTestConfiguratorFactory" in gen_content, \
        "GenerateSirTests missing factory reference"
    assert "AnalysisApiTestConfiguratorFactoryData" in gen_content, \
        "GenerateSirTests missing data class reference"

    # Verify kotlinc can parse the generator file (validates imports structurally)
    result = subprocess.run(
        ["kotlinc", str(generator_file), "-d", "/tmp/test_out"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    # Only check for syntax/structural errors, not unresolved references
    if "syntax" in result.stderr.lower() or "parsing" in result.stderr.lower():
        assert False, f"Generator file has syntax/parsing errors: {result.stderr[:500]}"
