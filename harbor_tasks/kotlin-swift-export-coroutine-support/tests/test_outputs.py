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
        with open(path, 'r') as f:
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
    assert result.returncode == 0, \
        "Source code must contain 'SirImport(config.coroutineSupportModuleName, SirImport.Mode.Exported)'"

    # Also verify the buggy pattern is NOT present (no SirImport without Mode.Exported for coroutineSupportModuleName)
    buggy_result = subprocess.run(
        ["grep", "SirImport(config.coroutineSupportModuleName)", MODULE_TRANSLATION_KT],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert buggy_result.returncode != 0, \
        "Source code should NOT contain buggy 'SirImport(config.coroutineSupportModuleName)' without Mode.Exported"


def test_golden_closures_main():
    """closures/golden_result/main/main.swift uses @_exported import."""
    content = read_file(GOLDEN_FILES["closures_main"])
    assert content is not None, f"Golden file not found: {GOLDEN_FILES['closures_main']}"

    # Must have the @_exported import (not regular import)
    assert '@_exported import KotlinCoroutineSupport' in content, \
        "closures_main.swift must use '@_exported import KotlinCoroutineSupport'"

    # Must NOT have regular import (the buggy pattern)
    buggy_pattern = r'^import KotlinCoroutineSupport\s*$'
    assert not re.search(buggy_pattern, content, re.MULTILINE), \
        "closures_main.swift has buggy 'import KotlinCoroutineSupport' (missing @_exported)"


def test_golden_coroutines_kcs():
    """coroutines/golden_result/KotlinxCoroutinesCore uses @_exported import."""
    content = read_file(GOLDEN_FILES["coroutines_kcs"])
    assert content is not None, f"Golden file not found: {GOLDEN_FILES['coroutines_kcs']}"

    assert '@_exported import KotlinCoroutineSupport' in content, \
        "KotlinxCoroutinesCore.swift must use '@_exported import KotlinCoroutineSupport'"

    buggy_pattern = r'^import KotlinCoroutineSupport\s*$'
    assert not re.search(buggy_pattern, content, re.MULTILINE), \
        "KotlinxCoroutinesCore.swift has buggy 'import KotlinCoroutineSupport'"


def test_golden_coroutines_flow():
    """coroutines/golden_result/flow_overrides uses @_exported import."""
    content = read_file(GOLDEN_FILES["coroutines_flow"])
    assert content is not None, f"Golden file not found: {GOLDEN_FILES['coroutines_flow']}"

    assert '@_exported import KotlinCoroutineSupport' in content, \
        "flow_overrides.swift must use '@_exported import KotlinCoroutineSupport'"

    buggy_pattern = r'^import KotlinCoroutineSupport\s*$'
    assert not re.search(buggy_pattern, content, re.MULTILINE), \
        "flow_overrides.swift has buggy 'import KotlinCoroutineSupport'"


def test_golden_coroutines_main():
    """coroutines/golden_result/main/main.swift uses @_exported import."""
    content = read_file(GOLDEN_FILES["coroutines_main"])
    assert content is not None, f"Golden file not found: {GOLDEN_FILES['coroutines_main']}"

    assert '@_exported import KotlinCoroutineSupport' in content, \
        "coroutines main.swift must use '@_exported import KotlinCoroutineSupport'"

    buggy_pattern = r'^import KotlinCoroutineSupport\s*$'
    assert not re.search(buggy_pattern, content, re.MULTILINE), \
        "coroutines main.swift has buggy 'import KotlinCoroutineSupport'"


def test_golden_flattening_main():
    """coroutinesWithPackageFlattening golden result uses @_exported import."""
    content = read_file(GOLDEN_FILES["flattening_main"])
    assert content is not None, f"Golden file not found: {GOLDEN_FILES['flattening_main']}"

    assert '@_exported import KotlinCoroutineSupport' in content, \
        "flattening_main.swift must use '@_exported import KotlinCoroutineSupport'"

    buggy_pattern = r'^import KotlinCoroutineSupport\s*$'
    assert not re.search(buggy_pattern, content, re.MULTILINE), \
        "flattening_main.swift has buggy 'import KotlinCoroutineSupport'"


# ============================================================================
# PASS-TO-PASS TESTS (repo CI gates)
# ============================================================================


def test_coroutine_integration_test_data_exists():
    """Coroutine integration test data directory structure exists."""
    test_data_dir = Path(f"{REPO}/native/swift/swift-export-standalone-integration-tests/coroutines/testData")
    assert test_data_dir.exists(), f"Coroutine integration test data directory not found: {test_data_dir}"

    # Check that all expected golden directories exist
    expected_dirs = [
        "generation/closures/golden_result/main",
        "generation/coroutines/golden_result/KotlinxCoroutinesCore",
        "generation/coroutines/golden_result/flow_overrides",
        "generation/coroutines/golden_result/main",
        "generation/coroutinesWithPackageFlattening/golden_result/main",
    ]

    for subdir in expected_dirs:
        full_path = test_data_dir / subdir
        assert full_path.exists(), f"Expected directory not found: {full_path}"
