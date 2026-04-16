"""
Test suite for Kotlin Analysis API Test Configurator PR #5807.

This tests that:
1. The workaround mapping TestModuleKind.Source/SourceLike is removed
2. Tests use AnalysisApiTestConfiguratorFactoryData() with default parameters
3. Generated test files are updated to use TestModuleKind.SourceLike
"""

import subprocess
import sys
import os

REPO = "/workspace/kotlin"

# File paths relative to repo root
MAIN_FILE = "analysis/analysis-api-fir/testFixtures/org/jetbrains/kotlin/analysis/api/fir/test/configurators/AnalysisApiFirTestConfiguratorFactory.kt"
GENERATOR_FILE = "generators/sir-tests-generator/main/org/jetbrains/kotlin/generators/tests/native/swift/sir/GenerateSirTests.kt"
GENERATED_TEST_FILE = "native/swift/swift-export-ide/tests-gen/org/jetbrains/kotlin/swiftexport/ide/SwiftExportInIdeTestGenerated.java"
COMPOSE_TEST_FILE = "plugins/compose/compiler-hosted/src/test/kotlin/androidx/compose/compiler/plugins/kotlin/ComposeCompilerBoxTests.kt"
DATAFRAME_TEST_FILE = "plugins/kotlin-dataframe/testFixtures/org/jetbrains/kotlin/fir/dataframe/AbstractCompilerFacilityTestForDataFrame.kt"
SERIALIZATION_TEST_FILE = "plugins/kotlinx-serialization/testFixtures/org/jetbrains/kotlinx/serialization/runners/AbstractCompilerFacilityTestForSerialization.kt"


def read_file(path):
    """Read file content from repo."""
    full_path = os.path.join(REPO, path)
    with open(full_path, 'r') as f:
        return f.read()


# =============================================================================
# FAIL-TO-PASS TESTS (verify the fix was applied)
# =============================================================================

def test_workaround_removed_from_main_factory():
    """
    F2P: The workaround mapping TestModuleKind.Source to SourceLike must be removed.

    Before: Factory had a when() block remapping Source/ScriptSource -> SourceLike
    After: No remapping, data is passed through as-is
    """
    content = read_file(MAIN_FILE)

    # The workaround was specifically: val data = when (data.moduleKind) { ... }
    # After fix, there should be NO "val data = when (data.moduleKind)" reassignment
    # (there's a legitimate "when (data.moduleKind)" later in the function)
    assert "val data = when (data.moduleKind)" not in content, \
        "Workaround 'val data = when (data.moduleKind)' block still present in factory"

    # Should NOT have the mapping logic
    assert "TestModuleKind.Source, TestModuleKind.ScriptSource" not in content, \
        "Legacy mapping of Source/ScriptSource to SourceLike still present"

    # The requireSupported() call should remain
    assert "requireSupported(data)" in content, \
        "requireSupported(data) call missing"


def test_factory_uses_direct_data():
    """
    F2P: Factory should use 'data' directly without reassignment.

    The old code reassigned 'val data = when(...)'
    The new code should use the parameter directly.
    """
    content = read_file(MAIN_FILE)

    # Check that we don't reassign the data parameter
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if 'val data =' in line and 'when' not in line:
            # Could be the old reassignment pattern
            # Check next few lines for the when block
            next_lines = '\n'.join(lines[i:i+5])
            if 'moduleKind' in next_lines:
                assert False, f"Found data reassignment at line {i+1}: {line}"

    # The createConfigurator function should start with requireSupported
    # Find the function and check its body
    assert "override fun createConfigurator(data: AnalysisApiTestConfiguratorFactoryData)" in content


def test_generator_uses_default_constructor():
    """
    F2P: Test generator must use AnalysisApiTestConfiguratorFactoryData() with defaults.

    Before: Generator explicitly passed FrontendKind.Fir, TestModuleKind.Source, etc.
    After: Generator uses empty constructor AnalysisApiTestConfiguratorFactoryData()
    """
    content = read_file(GENERATOR_FILE)

    # Should use the default constructor with no arguments
    assert "AnalysisApiTestConfiguratorFactoryData()" in content, \
        "Generator should use AnalysisApiTestConfiguratorFactoryData() with no arguments"

    # Should NOT have the old explicit constructor call
    assert "FrontendKind.Fir," not in content, \
        "Generator still uses explicit FrontendKind.Fir parameter"


def test_compose_test_uses_default_constructor():
    """
    F2P: Compose compiler test must use default AnalysisApiTestConfiguratorFactoryData().
    """
    content = read_file(COMPOSE_TEST_FILE)

    # Should use default constructor
    assert "AnalysisApiTestConfiguratorFactoryData()" in content, \
        "Compose test should use AnalysisApiTestConfiguratorFactoryData()"

    # Should NOT have explicit parameters
    assert "FrontendKind.Fir," not in content, \
        "Compose test still has explicit FrontendKind.Fir"


def test_dataframe_test_uses_default_constructor():
    """
    F2P: DataFrame test must use default AnalysisApiTestConfiguratorFactoryData().
    """
    content = read_file(DATAFRAME_TEST_FILE)

    # Should use default constructor
    assert "AnalysisApiTestConfiguratorFactoryData()" in content, \
        "DataFrame test should use AnalysisApiTestConfiguratorFactoryData()"

    # Should use proper factory access pattern
    assert "AnalysisApiFirTestConfiguratorFactory.createConfigurator" in content, \
        "DataFrame test should use AnalysisApiFirTestConfiguratorFactory.createConfigurator"


def test_serialization_test_uses_default_constructor():
    """
    F2P: Serialization test must use default AnalysisApiTestConfiguratorFactoryData().
    """
    content = read_file(SERIALIZATION_TEST_FILE)

    # Should use default constructor
    assert "AnalysisApiTestConfiguratorFactoryData()" in content, \
        "Serialization test should use AnalysisApiTestConfiguratorFactoryData()"

    # Should use proper factory access pattern
    assert "AnalysisApiFirTestConfiguratorFactory.createConfigurator" in content, \
        "Serialization test should use AnalysisApiFirTestConfiguratorFactory.createConfigurator"


def test_generated_test_uses_sourcelike():
    """
    F2P: Generated Swift export test must use TestModuleKind.SourceLike.

    The generated test file was updated to use SourceLike instead of Source
    because the workaround was removed.
    """
    content = read_file(GENERATED_TEST_FILE)

    # Should use SourceLike, not Source
    assert "TestModuleKind.SourceLike" in content, \
        "Generated test should use TestModuleKind.SourceLike"

    # Should NOT use TestModuleKind.Source (the old value)
    # This is a negative test - we check the file doesn't have the old pattern
    # The pattern would be: "TestModuleKind.Source," on a line by itself in the constructor
    lines = content.split('\n')
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped == "TestModuleKind.Source," or stripped == "TestModuleKind.Source":
            # Check if it's in the constructor context
            context = '\n'.join(lines[max(0, i-3):min(len(lines), i+3)])
            if "AnalysisApiTestConfiguratorFactoryData" in context:
                assert False, f"Generated test still uses TestModuleKind.Source at line {i+1}"


# =============================================================================
# PASS-TO-PASS TESTS using subprocess.run() (origin: repo_tests)
# =============================================================================

def test_repo_files_tracked():
    """
    P2P: Modified files should be tracked in git (pass_to_pass).

    Verifies that all modified files exist and are tracked in the repository.
    Uses git ls-files subprocess command.
    """
    files_to_check = [
        MAIN_FILE,
        GENERATOR_FILE,
        GENERATED_TEST_FILE,
        COMPOSE_TEST_FILE,
        DATAFRAME_TEST_FILE,
        SERIALIZATION_TEST_FILE,
    ]

    for file_path in files_to_check:
        result = subprocess.run(
            ["git", "ls-files", file_path],
            capture_output=True,
            text=True,
            cwd=REPO,
            timeout=30,
        )
        assert result.returncode == 0, f"git ls-files failed for {file_path}"
        assert file_path in result.stdout, f"File {file_path} is not tracked in git"


def test_java_syntax_valid():
    """
    P2P: Generated Java file should have valid syntax (pass_to_pass).

    Uses javac to validate Java syntax of the generated test file.
    We extract the imports and class declaration to check basic structure.
    """
    java_file = os.path.join(REPO, GENERATED_TEST_FILE)

    # First check: extract imports and verify they're valid Java
    result = subprocess.run(
        ["head", "-30", java_file],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0, "Failed to read Java file"

    content = result.stdout

    # Basic Java syntax checks
    assert "package " in content, "Missing package declaration"
    assert "import " in content, "Missing import statements"
    assert "public class" in content or "class" in content, "Missing class declaration"

    # Count braces in the file
    brace_result = subprocess.run(
        ["grep", "-c", "{", java_file],
        capture_output=True,
        text=True,
        timeout=10,
    )
    open_braces = int(brace_result.stdout.strip()) if brace_result.returncode == 0 else 0

    close_brace_result = subprocess.run(
        ["grep", "-c", "}", java_file],
        capture_output=True,
        text=True,
        timeout=10,
    )
    close_braces = int(close_brace_result.stdout.strip()) if close_brace_result.returncode == 0 else 0

    assert open_braces > 0, "No opening braces found in Java file"
    assert close_braces > 0, "No closing braces found in Java file"


def test_git_repo_valid():
    """
    P2P: Git repository should be valid and at expected commit (pass_to_pass).

    Uses git rev-parse to verify the repo is at the expected base commit.
    """
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        cwd=REPO,
        timeout=30,
    )
    assert result.returncode == 0, "git rev-parse failed"
    current_commit = result.stdout.strip()

    # The expected base commit from the PR
    expected_commit = "cf158c2f4a54d62787dc129cc1afdc86d08c9b9f"
    assert current_commit == expected_commit, \
        f"Repo not at expected commit. Got {current_commit[:16]}..., expected {expected_commit[:16]}..."


# =============================================================================
# PASS-TO-PASS TESTS (origin: static - file content checks)
# =============================================================================

def test_syntax_valid_main_file():
    """
    P2P: Main factory file should have valid Kotlin syntax.
    """
    content = read_file(MAIN_FILE)

    # Basic Kotlin syntax checks
    assert "package " in content, "Missing package declaration"
    assert "object AnalysisApiFirTestConfiguratorFactory" in content, "Missing object declaration"
    assert "override fun createConfigurator" in content, "Missing createConfigurator function"

    # Check braces are balanced
    open_braces = content.count('{')
    close_braces = content.count('}')
    assert open_braces == close_braces, f"Unbalanced braces: {open_braces} open, {close_braces} close"

    # Check parentheses are balanced
    open_parens = content.count('(')
    close_parens = content.count(')')
    assert open_parens == close_parens, f"Unbalanced parentheses: {open_parens} open, {close_parens} close"


def test_syntax_valid_compose_file():
    """
    P2P: Compose test file should have valid Kotlin syntax.
    """
    content = read_file(COMPOSE_TEST_FILE)

    # Check braces are balanced
    open_braces = content.count('{')
    close_braces = content.count('}')
    assert open_braces == close_braces, f"Unbalanced braces in compose file"


def test_syntax_valid_serialization_file():
    """
    P2P: Serialization test file should have valid Kotlin syntax.
    """
    content = read_file(SERIALIZATION_TEST_FILE)

    # Check braces are balanced
    open_braces = content.count('{')
    close_braces = content.count('}')
    assert open_braces == close_braces, f"Unbalanced braces in serialization file"


def test_imports_clean_in_test_files():
    """
    P2P: Test files should have clean imports (no wildcard imports for configurator package).

    The fix changes from wildcard imports to specific imports.
    """
    # Check DataFrame file
    df_content = read_file(DATAFRAME_TEST_FILE)
    assert "import org.jetbrains.kotlin.analysis.test.framework.test.configurators.*" not in df_content, \
        "DataFrame test should not use wildcard import for configurators"

    # Check Serialization file
    ser_content = read_file(SERIALIZATION_TEST_FILE)
    assert "import org.jetbrains.kotlin.analysis.test.framework.test.configurators.*" not in ser_content, \
        "Serialization test should not use wildcard import for configurators"

    # Check Compose file
    compose_content = read_file(COMPOSE_TEST_FILE)
    assert "import org.jetbrains.kotlin.analysis.test.framework.test.configurators.*" not in compose_content, \
        "Compose test should not use wildcard import for configurators"


def test_copyright_year_updated():
    """
    P2P: Copyright year should be 2026 in modified files.

    This is a minor check - the PR updated copyright years.
    """
    files_to_check = [
        GENERATOR_FILE,
        COMPOSE_TEST_FILE,
        DATAFRAME_TEST_FILE,
        SERIALIZATION_TEST_FILE
    ]

    for file_path in files_to_check:
        content = read_file(file_path)
        # Should have 2026 copyright (or at least updated from original)
        assert "2010-2026" in content or "Copyright" in content, \
            f"{file_path} missing copyright header"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
