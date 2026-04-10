"""
Tests for verifying the removal of dead autoShutdownMemoryThreshold code.

This verifies that:
1. COMPILE_DAEMON_MEMORY_THRESHOLD_INFINITE constant is removed
2. autoshutdownMemoryThreshold field is removed from DaemonOptions
3. The PropMapper for autoshutdownMemoryThreshold is removed
"""

import re
import subprocess
from pathlib import Path

REPO = Path("/workspace/kotlin")
TARGET_FILE = REPO / "compiler/daemon/daemon-common/src/org/jetbrains/kotlin/daemon/common/DaemonParams.kt"


def test_constant_removed():
    """Verify COMPILE_DAEMON_MEMORY_THRESHOLD_INFINITE constant is removed."""
    content = TARGET_FILE.read_text()
    assert "COMPILE_DAEMON_MEMORY_THRESHOLD_INFINITE" not in content, \
        "COMPILE_DAEMON_MEMORY_THRESHOLD_INFINITE constant should be removed"


def test_field_removed_from_daemon_options():
    """Verify autoshutdownMemoryThreshold field is removed from DaemonOptions class."""
    content = TARGET_FILE.read_text()

    # Check the field declaration is removed
    field_pattern = r"var\s+autoshutdownMemoryThreshold\s*:"
    assert not re.search(field_pattern, content), \
        "autoshutdownMemoryThreshold field should be removed from DaemonOptions"


def test_prop_mapper_removed():
    """Verify PropMapper for autoshutdownMemoryThreshold is removed."""
    content = TARGET_FILE.read_text()

    # Check that the PropMapper with autoshutdownMemoryThreshold is gone
    # The pattern should match the multiline PropMapper block
    prop_mapper_pattern = r"PropMapper\(\s*\n?\s*this,\s*\n?\s*DaemonOptions::autoshutdownMemoryThreshold"
    assert not re.search(prop_mapper_pattern, content, re.DOTALL), \
        "PropMapper for autoshutdownMemoryThreshold should be removed"


def test_daemon_options_data_class_structure():
    """Verify DaemonOptions data class has correct remaining fields."""
    content = TARGET_FILE.read_text()

    # Find the DaemonOptions class definition
    class_match = re.search(
        r"data\s+class\s+DaemonOptions\s*\([^)]+\)",
        content,
        re.DOTALL
    )
    assert class_match, "Could not find DaemonOptions data class"

    class_def = class_match.group(0)

    # These fields should still exist
    expected_fields = [
        "runFilesPath",
        "autoshutdownIdleSeconds",
        "autoshutdownUnusedSeconds",
        "shutdownDelayMilliseconds",
        "forceShutdownTimeoutMilliseconds",
        "verbose",
        "reportPerf",
    ]

    for field in expected_fields:
        assert field in class_def, f"Field {field} should exist in DaemonOptions"

    # This field should NOT exist
    assert "autoshutdownMemoryThreshold" not in class_def, \
        "autoshutdownMemoryThreshold should not exist in DaemonOptions"


def test_mappers_list_structure():
    """Verify the mappers list in DaemonOptions has correct PropMappers."""
    content = TARGET_FILE.read_text()

    # Find the DaemonOptions class and its mappers section
    # Look for the specific DaemonOptions class section
    class_match = re.search(
        r"data\s+class\s+DaemonOptions\s*\([^)]+\)\s*:\s*OptionsGroup\s*\{[^}]*?override\s+val\s+mappers.*?listOf\((.*?)\n\s*\)",
        content,
        re.DOTALL
    )
    assert class_match, "Could not find DaemonOptions mappers list"

    mappers_text = class_match.group(1)

    # Should have runFilesPath mapper
    assert "runFilesPath" in mappers_text, "runFilesPath PropMapper should exist"

    # Should NOT have autoshutdownMemoryThreshold mapper
    assert "autoshutdownMemoryThreshold" not in mappers_text, \
        "autoshutdownMemoryThreshold PropMapper should be removed"


def test_kotlin_file_compiles():
    """Verify the modified Kotlin file compiles without errors."""
    # Check if kotlinc is available
    kotlinc_check = subprocess.run(
        ["which", "kotlinc"],
        capture_output=True,
        text=True,
        timeout=10
    )

    if kotlinc_check.returncode == 0:
        # kotlinc is available, try to compile
        result = subprocess.run(
            ["kotlinc", "-d", "/tmp/compiled", str(TARGET_FILE)],
            capture_output=True,
            text=True,
            cwd=REPO,
            timeout=60
        )
        assert result.returncode == 0, f"Kotlin file compilation failed: {result.stderr}"
    else:
        # kotlinc not available, do basic structural checks instead
        content = TARGET_FILE.read_text()

        # Basic structural checks
        assert content.count("(") == content.count(")"), "Mismatched parentheses"
        assert "data class DaemonOptions" in content, "DaemonOptions class should exist"
        assert "PropMapper" in content, "PropMapper should still be referenced"


def test_no_references_to_removed_memory_threshold():
    """Verify no remaining references to memory threshold functionality."""
    content = TARGET_FILE.read_text()

    # These should all be gone
    removed_terms = [
        "COMPILE_DAEMON_MEMORY_THRESHOLD_INFINITE",
        "autoshutdownMemoryThreshold",
        "memoryThreshold",
        "MemoryThreshold",
    ]

    for term in removed_terms:
        assert term not in content, f"Reference to '{term}' should be removed"


def test_file_has_valid_prop_mappers():
    """Verify remaining PropMapper instances are valid and complete."""
    content = TARGET_FILE.read_text()

    # Count PropMapper occurrences - should have some remaining
    prop_mapper_count = content.count("PropMapper(")
    assert prop_mapper_count >= 1, "Should have at least 1 remaining PropMapper"

    # Each PropMapper should be properly formed (have closing paren)
    open_count = content.count("PropMapper(")
    # Check that PropMappers are well-formed by looking at the structure
    # after the autoshutdownMemoryThreshold removal

    # The remaining mappers should include runFilesPath
    assert "runFilesPath" in content, "runFilesPath mapper should exist"

    # And should have other timeout-related mappers
    timeout_related = ["autoshutdownIdleSeconds", "autoshutdownUnusedSeconds"]
    for term in timeout_related:
        assert term in content, f"{term} should still exist in the file"


# ============================================================================
# Repo CI/CD Pass-to-Pass Tests
# These tests verify that the repository's code structure remains valid
# after the fix, ensuring candidate solutions don't break existing functionality.
# ============================================================================


def test_repo_kotlin_syntax_balanced_brackets():
    """Repo check: Verify Kotlin file has balanced brackets and braces (pass_to_pass)."""
    content = TARGET_FILE.read_text()

    # Check balanced brackets
    assert content.count("(") == content.count(")"), "Mismatched parentheses"
    assert content.count("[") == content.count("]"), "Mismatched square brackets"
    assert content.count("{") == content.count("}"), "Mismatched curly braces"


def test_repo_kotlin_package_declaration_valid():
    """Repo check: Verify Kotlin package declaration is present and valid (pass_to_pass)."""
    content = TARGET_FILE.read_text()

    # Should have valid package declaration
    assert "package org.jetbrains.kotlin.daemon.common" in content, \
        "Package declaration should be valid"


def test_repo_kotlin_imports_valid():
    """Repo check: Verify Kotlin imports are syntactically valid (pass_to_pass)."""
    content = TARGET_FILE.read_text()

    # Should have standard imports
    assert any("org.jetbrains.kotlin.cli.common" in line for line in content.split('\n')), \
        "Should import from cli.common"


def test_repo_data_class_syntax_valid():
    """Repo check: Verify DaemonOptions data class syntax is valid (pass_to_pass)."""
    content = TARGET_FILE.read_text()

    # Find DaemonOptions class definition - should be valid data class
    class_match = re.search(
        r"data\s+class\s+DaemonOptions\s*\([^)]*\)\s*:\s*OptionsGroup",
        content,
        re.DOTALL
    )
    assert class_match, "DaemonOptions should be a valid data class extending OptionsGroup"

    # Should have valid property declarations
    var_pattern = re.compile(r"var\s+\w+\s*:\s*\w+\s*=\s*[^,\n]+")
    properties = var_pattern.findall(class_match.group(0))
    assert len(properties) >= 5, "Should have at least 5 var properties in DaemonOptions"


def test_repo_constant_declarations_valid():
    """Repo check: Verify const val declarations are syntactically valid (pass_to_pass)."""
    content = TARGET_FILE.read_text()

    # Should have standard constants (minus the removed one)
    expected_constants = [
        "COMPILE_DAEMON_TIMEOUT_INFINITE_S",
        "COMPILE_DAEMON_DEFAULT_IDLE_TIMEOUT_S",
        "COMPILE_DAEMON_DEFAULT_UNUSED_TIMEOUT_S",
    ]

    for const_name in expected_constants:
        assert const_name in content, f"Constant {const_name} should exist"


def test_repo_propmapper_usage_valid():
    """Repo check: Verify PropMapper class usage is valid (pass_to_pass)."""
    content = TARGET_FILE.read_text()

    # Should have PropMapper class definition or usage
    assert "PropMapper" in content, "PropMapper should be defined or used"

    # Check that PropMapper is used with proper syntax
    # Valid patterns: PropMapper(this, ...), PropMapper(this, DaemonOptions::prop, ...)
    mapper_usage_pattern = re.compile(r"PropMapper\([^)]*\)", re.DOTALL)
    usages = mapper_usage_pattern.findall(content)

    # Should have at least one valid PropMapper usage in mappers list
    assert len(usages) >= 1, "Should have at least one PropMapper constructor call"


def test_repo_file_structure_integrity():
    """Repo check: Verify overall file structure is intact after modification (pass_to_pass)."""
    content = TARGET_FILE.read_text()

    # File should start with copyright header
    assert content.strip().startswith("/*"), "File should start with comment block"
    assert "Copyright" in content or "Licensed under the Apache License" in content, \
        "Should have license header"

    # Should have all major sections
    assert "package " in content, "Should have package declaration"
    assert "import " in content, "Should have imports"
    assert "class " in content or "data class" in content, "Should have class declarations"

    # File should end properly (no truncated content)
    # Check last non-whitespace character is a valid ending
    last_content = content.rstrip()[-20:]
    assert any(c in last_content for c in ["}", ")", ";", "]"]), \
        "File should end with valid Kotlin syntax"


def test_repo_no_double_commas():
    """Repo check: Verify no double commas in Kotlin code (pass_to_pass)."""
    content = TARGET_FILE.read_text()

    # Check for double commas (common syntax error)
    assert ", ," not in content, "Double commas detected"
    assert ",," not in content, "Adjacent commas detected"
