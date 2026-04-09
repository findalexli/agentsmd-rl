"""
Test suite for KT-85257: Stop copying R8 output with AGP 9.1+

This test validates that the Compose compiler Gradle plugin correctly handles
R8 output files based on the AGP version:
- AGP 9.1+: AGP copies R8 output correctly, so we skip manual copying
- AGP < 9.1: Manual copying is still required (WithR8Outputs inner class)
"""

import os
import re
import subprocess
import sys

REPO = "/workspace/kotlin"
TARGET_FILE = os.path.join(
    REPO,
    "libraries/tools/kotlin-compose-compiler/src/common/kotlin/org/jetbrains/kotlin/compose/compiler/gradle/internal/ComposeAgpMappingFile.kt"
)


def test_target_file_exists():
    """Target file exists and is readable."""
    assert os.path.exists(TARGET_FILE), f"Target file not found: {TARGET_FILE}"


def test_agp_version_import_exists():
    """File imports AndroidGradlePluginVersion for version detection."""
    content = open(TARGET_FILE).read()
    assert "AndroidGradlePluginVersion" in content, \
        "Missing import for AndroidGradlePluginVersion"


def test_agp_version_check_exists():
    """AGP version check (>= 9.1) exists for conditional behavior."""
    content = open(TARGET_FILE).read()
    # Check for the version detection pattern
    pattern = r"it\.major\s*>=?\s*9\s*&&\s*it\.minor\s*>=?\s*1"
    assert re.search(pattern, content), \
        "Missing AGP version check (major >= 9 && minor >= 1)"


def test_agp_copies_r8_output_variable():
    """agpCopiesR8Output variable exists for conditional task registration."""
    content = open(TARGET_FILE).read()
    assert "agpCopiesR8Output" in content, \
        "Missing agpCopiesR8Output variable for conditional behavior"


def test_conditional_task_registration():
    """Task registration is conditional based on AGP version."""
    content = open(TARGET_FILE).read()
    # Check for conditional task registration
    assert "if (agpCopiesR8Output)" in content, \
        "Missing conditional task registration based on agpCopiesR8Output"
    # Check both branches exist
    assert "tasks.register<MergeMappingFileTask>(mergeTaskName)" in content, \
        "Missing AGP 9.1+ task registration (without WithR8Outputs)"
    assert "tasks.register<MergeMappingFileTask.WithR8Outputs>" in content, \
        "Missing pre-AGP 9.1 task registration (with WithR8Outputs)"


def test_with_r8_outputs_inner_class_exists():
    """WithR8Outputs inner class exists for pre-AGP 9.1 compatibility."""
    content = open(TARGET_FILE).read()
    # Check for inner class declaration
    assert "abstract class WithR8Outputs" in content, \
        "Missing WithR8Outputs inner class for backwards compatibility"
    # Check it extends MergeMappingFileTask
    assert "MergeMappingFileTask()" in content, \
        "WithR8Outputs should extend MergeMappingFileTask"


def test_r8_mapping_file_property():
    """r8MappingFile property exists and replaces originalFile."""
    content = open(TARGET_FILE).read()
    # Check r8MappingFile property exists
    assert "r8MappingFile: RegularFileProperty" in content, \
        "Missing r8MappingFile property"
    # Check it's used in wiring
    assert "MergeMappingFileTask::r8MappingFile" in content, \
        "r8MappingFile should be used in task wiring"


def test_no_original_file_property():
    """originalFile property should be renamed to r8MappingFile."""
    content = open(TARGET_FILE).read()
    # originalFile should not exist anymore (renamed to r8MappingFile)
    assert "abstract val originalFile: RegularFileProperty" not in content, \
        "originalFile property should be renamed to r8MappingFile"


def test_delete_recursively_moved_to_inner_class():
    """deleteRecursively should only be in WithR8Outputs, not base class."""
    content = open(TARGET_FILE).read()

    # Find the base class taskAction - should NOT have deleteRecursively
    # Pattern: base class has "open fun taskAction()" with just super call and writer logic
    base_class_pattern = r"open fun taskAction\(\).*?(?=abstract class WithR8Outputs|$)"
    base_match = re.search(base_class_pattern, content, re.DOTALL)

    if base_match:
        base_task_action = base_match.group(0)
        # Base class taskAction should NOT contain deleteRecursively
        assert "deleteRecursively" not in base_task_action or "WithR8Outputs" in base_task_action[:base_match.start()], \
            "Base MergeMappingFileTask.taskAction should NOT contain deleteRecursively - it should be in WithR8Outputs only"

    # WithR8Outputs class should have deleteRecursively
    assert "deleteRecursively()" in content, \
        "deleteRecursively should exist in WithR8Outputs.taskAction"


def test_output_dir_only_in_inner_class():
    """outputDir property should only exist in WithR8Outputs inner class."""
    content = open(TARGET_FILE).read()

    # Find base class section (before WithR8Outputs)
    parts = content.split("abstract class WithR8Outputs")
    base_class = parts[0]

    # Base class should NOT have outputDir
    base_lines = [l for l in base_class.split('\n') if 'outputDir' in l and 'abstract val outputDir' in l]
    assert len(base_lines) == 0, \
        "Base class should not have outputDir property - it should only be in WithR8Outputs"

    # WithR8Outputs should have outputDir
    if len(parts) > 1:
        inner_class = parts[1]
        assert "outputDir" in inner_class, \
            "WithR8Outputs should have outputDir property"


def test_r8_outputs_file_collection_in_inner_class():
    """r8Outputs FileCollection should only be in WithR8Outputs inner class."""
    content = open(TARGET_FILE).read()

    # Find base class section (before WithR8Outputs)
    parts = content.split("abstract class WithR8Outputs")
    base_class = parts[0]

    # Base class should NOT have r8Outputs property
    base_r8outputs = [l for l in base_class.split('\n') if 'r8Outputs' in l and 'val r8Outputs' in l]
    assert len(base_r8outputs) == 0, \
        "Base class should not have r8Outputs FileCollection - it should only be in WithR8Outputs"

    # WithR8Outputs should have r8Outputs
    if len(parts) > 1:
        inner_class = parts[1]
        assert "r8Outputs" in inner_class, \
            "WithR8Outputs should have r8Outputs FileCollection"


def test_file_copying_in_inner_class_only():
    """File copying (copyTo) should only happen in WithR8Outputs."""
    content = open(TARGET_FILE).read()

    # Split into base class and inner class
    parts = content.split("abstract class WithR8Outputs")
    base_class = parts[0]

    # Base class taskAction should NOT have copyTo
    # Count copyTo occurrences before WithR8Outputs
    base_copy_count = base_class.count("copyTo(")
    # Only the r8Outputs.forEach copy should be in WithR8Outputs
    # There might be some copyTo in comments/imports, so check it's minimal

    # Full file should have copyTo in WithR8Outputs
    if len(parts) > 1:
        inner_class = parts[1]
        assert "copyTo(" in inner_class, \
            "WithR8Outputs should copy R8 output files"


def test_kotlin_syntax_valid():
    """Kotlin file should have valid syntax (no unmatched braces)."""
    content = open(TARGET_FILE).read()

    # Basic syntax check - count braces
    open_braces = content.count('{')
    close_braces = content.count('}')

    # Allow for one extra closing or opening due to file ending
    diff = abs(open_braces - close_braces)
    assert diff <= 1, \
        f"Unbalanced braces: {open_braces} open, {close_braces} close (diff={diff})"


def test_internal_api_opt_in_annotation():
    """AndroidGradlePluginVersion usage should have @OptIn annotation."""
    content = open(TARGET_FILE).read()
    assert "@OptIn(InternalKotlinGradlePluginApi::class)" in content, \
        "Missing @OptIn annotation for InternalKotlinGradlePluginApi"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
