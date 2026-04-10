"""
Test suite for KT-85257: Stop copying R8 output with AGP 9.1+

This test validates that the Compose compiler Gradle plugin correctly handles
R8 output files based on the AGP version:
- AGP 9.1+: AGP copies R8 output correctly, so we skip manual copying
- AGP < 9.1: Manual copying is still required (WithR8Outputs inner class)

Tests use subprocess.run() to compile the Kotlin code, which validates:
- Proper syntax and structure
- Correct class hierarchy (WithR8Outputs extends MergeMappingFileTask)
- Property existence (r8MappingFile replacing originalFile)
- Method visibility changes (open fun taskAction)
- Import resolution (AndroidGradlePluginVersion, InternalKotlinGradlePluginApi)
"""

import os
import subprocess
import sys

REPO = "/workspace/kotlin"
TARGET_FILE = os.path.join(
    REPO,
    "libraries/tools/kotlin-compose-compiler/src/common/kotlin/org/jetbrains/kotlin/compose/compiler/gradle/internal/ComposeAgpMappingFile.kt"
)

# Gradle module path for compilation
MODULE_DIR = os.path.join(
    REPO,
    "libraries/tools/kotlin-compose-compiler"
)


def _run_gradle_compile(timeout: int = 120) -> subprocess.CompletedProcess:
    """Compile the kotlin-compose-compiler module to validate Kotlin code."""
    return subprocess.run(
        ["./gradlew", ":kotlin-compose-compiler:compileKotlin", "--no-daemon", "-q"],
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=REPO,
    )


def test_kotlin_compiles():
    """Kotlin code compiles successfully (fail_to_pass: validates all structural changes)."""
    r = _run_gradle_compile(timeout=180)

    # Filter out download progress and non-error messages
    error_lines = [
        line for line in r.stderr.split('\n')
        if line and
           'Downloading' not in line and
           'Download ' not in line and
           'Progress' not in line and
           '%' not in line and
           '>' not in line and
           'watch-fs' not in line and
           'file system' not in line and
           'file-system' not in line
    ]
    filtered_stderr = '\n'.join(error_lines[-30:])  # Keep last 30 relevant lines

    assert r.returncode == 0, f"Kotlin compilation failed:\n{filtered_stderr}"


def test_task_class_structure():
    """MergeMappingFileTask has correct class structure with WithR8Outputs inner class."""
    content = open(TARGET_FILE).read()

    # Verify base class is no longer abstract with constructor injection
    # After fix, it should be: internal abstract class MergeMappingFileTask : DefaultTask()
    base_class_match = "internal abstract class MergeMappingFileTask : DefaultTask()" in content
    assert base_class_match, "Base MergeMappingFileTask should extend DefaultTask() directly without constructor injection"

    # Verify WithR8Outputs inner class exists and extends MergeMappingFileTask
    inner_class_pattern = "abstract class WithR8Outputs" in content and ": MergeMappingFileTask()" in content
    assert inner_class_pattern, "WithR8Outputs inner class should extend MergeMappingFileTask"

    # Verify taskAction is open for overriding
    assert "open fun taskAction()" in content, "taskAction should be open to allow override in WithR8Outputs"


def test_agp_version_detection():
    """AGP version check (>= 9.1) exists for conditional task registration."""
    content = open(TARGET_FILE).read()

    # Verify AndroidGradlePluginVersion import exists
    assert "AndroidGradlePluginVersion" in content, "Missing AndroidGradlePluginVersion import"

    # Verify version check logic exists
    version_check = "it.major >= 9 && it.minor >= 1" in content
    assert version_check, "Missing AGP version check (major >= 9 && minor >= 1)"

    # Verify conditional variable exists
    assert "agpCopiesR8Output" in content, "Missing agpCopiesR8Output variable"

    # Verify conditional task registration
    assert "if (agpCopiesR8Output)" in content, "Missing conditional task registration"


def test_property_renaming():
    """originalFile renamed to r8MappingFile and used correctly."""
    content = open(TARGET_FILE).read()

    # r8MappingFile property exists
    assert "r8MappingFile: RegularFileProperty" in content, "Missing r8MappingFile property"

    # originalFile should NOT exist as abstract property (it was renamed)
    assert "abstract val originalFile: RegularFileProperty" not in content, \
        "originalFile property should be renamed to r8MappingFile"

    # wiredWithFiles uses r8MappingFile
    assert "MergeMappingFileTask::r8MappingFile" in content, \
        "wiredWithFiles should use r8MappingFile instead of originalFile"


def test_r8_logic_separation():
    """R8 output copying logic properly separated into WithR8Outputs inner class."""
    content = open(TARGET_FILE).read()

    # Find the WithR8Outputs class position
    parts = content.split("abstract class WithR8Outputs")
    base_class = parts[0]

    # Base class should NOT have r8Outputs property
    base_has_r8outputs = "val r8Outputs" in base_class and "FileCollection" in base_class
    if base_has_r8outputs:
        # Check if it's in the right place - before WithR8Outputs
        base_lines = base_class.split('\n')
        r8outputs_lines = [l for l in base_lines if 'val r8Outputs' in l]
        assert len(r8outputs_lines) == 0, \
            "Base class should not have r8Outputs FileCollection - only WithR8Outputs should have it"

    # WithR8Outputs should have r8Outputs
    if len(parts) > 1:
        inner_class = parts[1]
        assert "r8Outputs" in inner_class, "WithR8Outputs should have r8Outputs FileCollection"
        assert "outputDir" in inner_class, "WithR8Outputs should have outputDir property"
        assert "deleteRecursively()" in inner_class, "WithR8Outputs should call deleteRecursively"
        assert "copyTo(" in inner_class, "WithR8Outputs should copy R8 output files"


def test_opt_in_annotation():
    """@OptIn annotation present for InternalKotlinGradlePluginApi usage."""
    content = open(TARGET_FILE).read()

    assert "@OptIn(InternalKotlinGradlePluginApi::class)" in content, \
        "Missing @OptIn annotation for InternalKotlinGradlePluginApi"
    assert "InternalKotlinGradlePluginApi" in content, \
        "Missing InternalKotlinGradlePluginApi import"


# ==================== Pass-to-Pass Tests (Repo Hygiene) ====================

def test_target_file_exists():
    """Target file exists and is readable."""
    assert os.path.exists(TARGET_FILE), f"Target file not found: {TARGET_FILE}"


def test_agp_version_import_exists():
    """AndroidGradlePluginVersion import exists."""
    content = open(TARGET_FILE).read()
    assert "import org.jetbrains.kotlin.gradle.plugin.AndroidGradlePluginVersion" in content, \
        "Missing AndroidGradlePluginVersion import"


def test_kotlin_syntax_valid():
    """Kotlin file has balanced braces (basic syntax check)."""
    content = open(TARGET_FILE).read()

    open_braces = content.count('{')
    close_braces = content.count('}')
    diff = abs(open_braces - close_braces)

    assert diff <= 1, \
        f"Unbalanced braces: {open_braces} open, {close_braces} close (diff={diff})"


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
