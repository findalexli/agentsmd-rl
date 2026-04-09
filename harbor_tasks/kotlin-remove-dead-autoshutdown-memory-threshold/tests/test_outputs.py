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
