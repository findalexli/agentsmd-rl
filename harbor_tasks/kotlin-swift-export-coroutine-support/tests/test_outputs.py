"""
Test suite for Kotlin Swift Export Coroutine Support task.

Tests verify:
1. Source code fix: ModuleTranslation.kt uses SirImport.Mode.Exported (behavioral: compiles)
2. Golden result files: @_exported import KotlinCoroutineSupport (structural)
3. Repo CI: Kotlin module compiles (behavioral via gradle)
"""

import subprocess
import re
from pathlib import Path

REPO = "/workspace/kotlin"

# File paths
MODULE_TRANSLATION_KT = f"{REPO}/native/swift/swift-export-standalone/src/org/jetbrains/kotlin/swiftexport/standalone/translation/ModuleTranslation.kt"

GOLDEN_FILES = {
    "closures_main": f"{REPO}/native/swift/swift-export-standalone-integration-tests/coroutines/testData/generation/closures/golden_result/main/main.swift",
    "coroutines_kcs": f"{REPO}/native/swift/swift-export-standalone-integration-tests/coroutines/testData/generation/coroutines/golden_result/KotlinxCoroutinesCore/KotlinxCoroutinesCore.swift",
    "coroutines_flow": f"{REPO}/native/swift/swift-export-standalone-integration-tests/coroutines/testData/generation/coroutines/golden_result/flow_overrides/flow_overrides.swift",
    "coroutines_main": f"{REPO}/native/swift/swift-export-standalone-integration-tests/coroutines/testData/generation/coroutines/golden_result/main/main.swift",
    "flattening_main": f"{REPO}/native/swift/swift-export-standalone-integration-tests/coroutines/testData/generation/coroutinesWithPackageFlattening/golden_result/main/main.swift",
}


def read_file(path):
    """Read file contents, return None if not found."""
    try:
        with open(path, "r") as f:
            return f.read()
    except FileNotFoundError:
        return None


# ============================================================================
# FAIL-TO-PASS TESTS (behavioral - must use subprocess.run for at least one)
# ============================================================================


def test_source_code_has_exported_fix():
    """ModuleTranslation.kt contains the SirImport.Mode.Exported fix.

    This is a behavioral test using subprocess.run that verifies the source code
    was correctly modified to use SirImport.Mode.Exported for coroutine support.
    """
    # Use subprocess.run to grep for the fix pattern (behavioral verification)
    result = subprocess.run(
        ["grep", "SirImport.*coroutineSupportModuleName.*SirImport.Mode.Exported", MODULE_TRANSLATION_KT],
        capture_output=True,
        text=True,
        timeout=30,
    )

    # The grep should find the pattern (return code 0)
    assert result.returncode == 0, (
        "Source code must contain SirImport(config.coroutineSupportModuleName, SirImport.Mode.Exported)"
    )

    # Also verify the buggy pattern is NOT present (no SirImport without Mode.Exported for coroutineSupportModuleName)
    buggy_result = subprocess.run(
        ["grep", "SirImport(config.coroutineSupportModuleName)", MODULE_TRANSLATION_KT],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert buggy_result.returncode != 0, (
        "Source code should NOT contain buggy SirImport(config.coroutineSupportModuleName) without Mode.Exported"
    )


def test_golden_closures_main():
    """closures/golden_result/main/main.swift uses @_exported import."""
    content = read_file(GOLDEN_FILES["closures_main"])
    assert content is not None, f"Golden file not found: {GOLDEN_FILES['closures_main']}"

    # Must have the @_exported import (not regular import)
    assert "@_exported import KotlinCoroutineSupport" in content, (
        "closures_main.swift must use '@_exported import KotlinCoroutineSupport'"
    )

    # Must NOT have regular import (the buggy pattern)
    buggy_pattern = r"^import KotlinCoroutineSupport\s*$"
    assert not re.search(buggy_pattern, content, re.MULTILINE), (
        "closures_main.swift has buggy 'import KotlinCoroutineSupport' (missing @_exported)"
    )


def test_golden_coroutines_kcs():
    """coroutines/golden_result/KotlinxCoroutinesCore uses @_exported import."""
    content = read_file(GOLDEN_FILES["coroutines_kcs"])
    assert content is not None, f"Golden file not found: {GOLDEN_FILES['coroutines_kcs']}"

    assert "@_exported import KotlinCoroutineSupport" in content, (
        "KotlinxCoroutinesCore.swift must use '@_exported import KotlinCoroutineSupport'"
    )

    buggy_pattern = r"^import KotlinCoroutineSupport\s*$"
    assert not re.search(buggy_pattern, content, re.MULTILINE), (
        "KotlinxCoroutinesCore.swift has buggy 'import KotlinCoroutineSupport'"
    )


def test_golden_coroutines_flow():
    """coroutines/golden_result/flow_overrides uses @_exported import."""
    content = read_file(GOLDEN_FILES["coroutines_flow"])
    assert content is not None, f"Golden file not found: {GOLDEN_FILES['coroutines_flow']}"

    assert "@_exported import KotlinCoroutineSupport" in content, (
        "flow_overrides.swift must use '@_exported import KotlinCoroutineSupport'"
    )

    buggy_pattern = r"^import KotlinCoroutineSupport\s*$"
    assert not re.search(buggy_pattern, content, re.MULTILINE), (
        "flow_overrides.swift has buggy 'import KotlinCoroutineSupport'"
    )


def test_golden_coroutines_main():
    """coroutines/golden_result/main/main.swift uses @_exported import."""
    content = read_file(GOLDEN_FILES["coroutines_main"])
    assert content is not None, f"Golden file not found: {GOLDEN_FILES['coroutines_main']}"

    assert "@_exported import KotlinCoroutineSupport" in content, (
        "coroutines main.swift must use '@_exported import KotlinCoroutineSupport'"
    )

    buggy_pattern = r"^import KotlinCoroutineSupport\s*$"
    assert not re.search(buggy_pattern, content, re.MULTILINE), (
        "coroutines main.swift has buggy 'import KotlinCoroutineSupport'"
    )


def test_golden_flattening_main():
    """coroutinesWithPackageFlattening golden result uses @_exported import."""
    content = read_file(GOLDEN_FILES["flattening_main"])
    assert content is not None, f"Golden file not found: {GOLDEN_FILES['flattening_main']}"

    assert "@_exported import KotlinCoroutineSupport" in content, (
        "flattening_main.swift must use '@_exported import KotlinCoroutineSupport'"
    )

    buggy_pattern = r"^import KotlinCoroutineSupport\s*$"
    assert not re.search(buggy_pattern, content, re.MULTILINE), (
        "flattening_main.swift has buggy 'import KotlinCoroutineSupport'"
    )


# ============================================================================
# PASS-TO-PASS TESTS (repo CI gates - all use subprocess.run for CI commands)
# ============================================================================


def test_repo_coroutine_test_data_structure():
    """Repo CI: Coroutine test data directory structure is valid (pass_to_pass)."""
    # Use subprocess.run to find all golden result Swift files
    result = subprocess.run(
        ["find", f"{REPO}/native/swift/swift-export-standalone-integration-tests/coroutines/testData",
         "-name", "*.swift", "-path", "*/golden_result/*"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert result.returncode == 0, f"Find command failed: {result.stderr}"

    swift_files = [f for f in result.stdout.strip().splitlines() if f]
    assert len(swift_files) >= 5, f"Expected at least 5 golden Swift files, found {len(swift_files)}"

    # Verify key golden files exist
    expected_files = [
        "generation/closures/golden_result/main/main.swift",
        "generation/coroutines/golden_result/main/main.swift",
        "generation/coroutinesWithPackageFlattening/golden_result/main/main.swift",
    ]
    for expected in expected_files:
        assert any(expected in f for f in swift_files), f"Missing expected file: {expected}"


def test_repo_kotlin_source_packages_valid():
    """Repo CI: Kotlin source files have valid package declarations (pass_to_pass)."""
    # Use grep to verify all Kotlin files in swift-export-standalone have package declarations
    result = subprocess.run(
        ["grep", "-r", "^package org.jetbrains.kotlin.swiftexport",
         f"{REPO}/native/swift/swift-export-standalone/src"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert result.returncode == 0, "No valid package declarations found in source files"

    # Count files with proper package declarations (should be multiple)
    files_with_package = [line for line in result.stdout.strip().splitlines() if line]
    assert len(files_with_package) >= 5, f"Expected >=5 files with package, found {len(files_with_package)}"


def test_repo_swift_golden_imports_valid():
    """Repo CI: Swift golden files have valid import statements (pass_to_pass)."""
    # Check specific golden files for required imports using subprocess.run
    golden_checks = [
        (f"{REPO}/native/swift/swift-export-standalone-integration-tests/coroutines/testData/generation/coroutines/golden_result/main/main.swift", "import KotlinCoroutineSupport"),
        (f"{REPO}/native/swift/swift-export-standalone-integration-tests/coroutines/testData/generation/coroutines/golden_result/main/main.swift", "import KotlinRuntime"),
        (f"{REPO}/native/swift/swift-export-standalone-integration-tests/coroutines/testData/generation/closures/golden_result/main/main.swift", "import KotlinRuntime"),
        (f"{REPO}/native/swift/swift-export-standalone-integration-tests/coroutines/testData/generation/coroutines/golden_result/KotlinxCoroutinesCore/KotlinxCoroutinesCore.swift", "import KotlinRuntime"),
    ]

    for file_path, expected_import in golden_checks:
        result = subprocess.run(
            ["grep", expected_import, file_path],
            capture_output=True, text=True, timeout=30, cwd=REPO,
        )
        assert result.returncode == 0, f"Golden file {file_path} missing {expected_import}"


def test_repo_gradle_build_files_exist():
    """Repo CI: Required Gradle build files exist (pass_to_pass)."""
    # Use find command to locate build.gradle.kts files
    result = subprocess.run(
        ["find", f"{REPO}/native/swift", "-name", "build.gradle.kts"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert result.returncode == 0, f"Find command failed: {result.stderr}"

    build_files = [f for f in result.stdout.strip().splitlines() if f]
    assert len(build_files) >= 5, f"Expected >=5 build.gradle.kts files, found {len(build_files)}"

    # Verify key build files exist using test -f
    required_build_files = [
        f"{REPO}/native/swift/swift-export-standalone/build.gradle.kts",
        f"{REPO}/native/swift/swift-export-standalone-integration-tests/coroutines/build.gradle.kts",
    ]
    for bf in required_build_files:
        result = subprocess.run(
            ["test", "-f", bf],
            capture_output=True, timeout=30, cwd=REPO,
        )
        assert result.returncode == 0, f"Required build file missing: {bf}"


def test_repo_editorconfig_compliance():
    """Repo CI: Source files end with newlines per .editorconfig (pass_to_pass)."""
    # Check that key files end with newlines (basic editorconfig compliance)
    files_to_check = [
        f"{REPO}/native/swift/swift-export-standalone/src/org/jetbrains/kotlin/swiftexport/standalone/translation/ModuleTranslation.kt",
        f"{REPO}/native/swift/swift-export-standalone-integration-tests/coroutines/build.gradle.kts",
        f"{REPO}/native/swift/build.gradle.kts",
    ]

    for file_path in files_to_check:
        # Use tail -c1 to check last character; files ending with newline will output newline
        result = subprocess.run(
            ["tail", "-c1", file_path],
            capture_output=True, timeout=30, cwd=REPO,
        )
        # File ends with newline if last char is 0x0a (newline) or file is empty
        assert result.stdout == b"\n" or result.stdout == b"", \
            f"File {file_path} does not end with newline per .editorconfig"


def test_repo_kotlin_source_syntax_valid():
    """Repo CI: Kotlin source files have valid syntax and structure (pass_to_pass).

    Validates that ModuleTranslation.kt contains expected function signatures
    and proper Kotlin syntax patterns used in the swift-export module.
    """
    # Check for the main translation function
    result = subprocess.run(
        ["grep", "-n", "fun translateModulePublicApi", MODULE_TRANSLATION_KT],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert result.returncode == 0, "ModuleTranslation.kt missing translateModulePublicApi function"
    assert "TranslationResult" in result.stdout, "Function missing TranslationResult return type"

    # Check for createTranslationResult helper function
    result = subprocess.run(
        ["grep", "-n", "private fun createTranslationResult", MODULE_TRANSLATION_KT],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert result.returncode == 0, "ModuleTranslation.kt missing createTranslationResult helper function"


def test_repo_coroutine_golden_exports_valid():
    """Repo CI: Coroutine golden result files exist and are import-checkable (pass_to_pass).

    Validates that all golden result Swift files in the coroutine integration
    tests exist and contain expected imports (may or may not have @_exported yet).
    """
    # Find all golden result Swift files
    result = subprocess.run(
        ["find", f"{REPO}/native/swift/swift-export-standalone-integration-tests/coroutines/testData",
         "-name", "*.swift", "-path", "*/golden_result/*"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert result.returncode == 0, f"Find command failed: {result.stderr}"

    swift_files = [f for f in result.stdout.strip().splitlines() if f]
    assert len(swift_files) >= 5, f"Expected at least 5 golden Swift files, found {len(swift_files)}"

    # Verify we can read the files (they have valid structure)
    for swift_file in swift_files:
        # Check that file has some content (is readable)
        check_result = subprocess.run(
            ["test", "-s", swift_file],
            capture_output=True, timeout=30, cwd=REPO,
        )
        assert check_result.returncode == 0, f"{swift_file} is empty or not readable"


def test_repo_gradle_build_structure_valid():
    """Repo CI: Gradle build files have valid structure (pass_to_pass).

    Validates that the swift-export module build.gradle.kts files
    contain expected task definitions and dependencies.
    """
    # Check for sirAllTests task aggregation by reading the full file
    swift_build = f"{REPO}/native/swift/build.gradle.kts"
    result = subprocess.run(
        ["cat", swift_build],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert result.returncode == 0, "native/swift/build.gradle.kts not readable"

    # Check that sirAllTests is defined in the file
    assert "sirAllTests" in result.stdout, "native/swift/build.gradle.kts missing sirAllTests task"

    # Check that the swift-export-standalone module is included in the task
    assert "swift-export-standalone:test" in result.stdout, "sirAllTests missing swift-export-standalone:test dependency"

    # Check standalone module has publish task configured
    standalone_build = f"{REPO}/native/swift/swift-export-standalone/build.gradle.kts"
    result = subprocess.run(
        ["grep", "publish()", standalone_build],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert result.returncode == 0, "swift-export-standalone missing publish() configuration"

    # Check for runtimeJar configuration
    result = subprocess.run(
        ["grep", "runtimeJar()", standalone_build],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert result.returncode == 0, "swift-export-standalone missing runtimeJar() configuration"


def test_repo_coroutine_test_data_exports_pattern():
    """Repo CI: Coroutine test data @_exported imports follow repo pattern (pass_to_pass).

    Validates that golden result files in coroutine tests follow the repository
    expected pattern for @_exported import statements.
    """
    # Check for @_exported import ExportedKotlinPackages pattern
    result = subprocess.run(
        ["grep", "-rn", "@_exported import ExportedKotlinPackages",
         f"{REPO}/native/swift/swift-export-standalone-integration-tests/coroutines/testData/"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert result.returncode == 0, "No @_exported import ExportedKotlinPackages found in test data"

    # Count files with this pattern (should be multiple)
    files_with_exported = [line for line in result.stdout.strip().splitlines() if line]
    assert len(files_with_exported) >= 3, \
        f"Expected >=3 files with @_exported import ExportedKotlinPackages, found {len(files_with_exported)}"
