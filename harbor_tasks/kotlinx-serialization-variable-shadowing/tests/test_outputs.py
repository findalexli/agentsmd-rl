"""Tests for Kotlin repository task.

This task adds missing FIR documentation to compiler/AGENTS.md.
"""

import subprocess
import sys

# REPO path inside the Docker container
REPO = "/workspace/kotlin"


def test_agents_md_has_fir_docs():
    """AGENTS.md contains FIR documentation (fail_to_pass).

    The patch adds documentation about FIR (K2 Frontend) to compiler/AGENTS.md.
    This test verifies the documentation exists after the fix.
    """
    result = subprocess.run(
        ["grep", "-q", "## FIR (K2 Frontend)", f"{REPO}/compiler/AGENTS.md"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, "AGENTS.md missing FIR documentation"


def test_agents_md_has_fir_element():
    """AGENTS.md documents FirElement usage (fail_to_pass).

    The patch should mention FirElement types for representing Kotlin code.
    """
    result = subprocess.run(
        ["grep", "-q", "FirElement", f"{REPO}/compiler/AGENTS.md"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, "AGENTS.md missing FirElement documentation"


def test_repo_java_version():
    """Java version check passes (pass_to_pass).

    Verify Java 17+ is available for building the Kotlin compiler.
    """
    result = subprocess.run(
        ["java", "-version"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, f"Java check failed: {result.stderr}"
    # Check for Java 17
    assert "17" in result.stderr or "17" in result.stdout, "Java 17 required"


def test_repo_file_structure():
    """Repository file structure is valid (pass_to_pass).

    Verify key directories exist in the Kotlin repository.
    """
    result = subprocess.run(
        ["ls", "-d", f"{REPO}/compiler", f"{REPO}/analysis"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, f"Directory check failed: {result.stderr}"


def test_repo_agents_md_exists():
    """AGENTS.md file exists (pass_to_pass).

    Verify the main AGENTS.md files exist in the repository.
    """
    result = subprocess.run(
        ["test", "-f", f"{REPO}/compiler/AGENTS.md"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, "compiler/AGENTS.md does not exist"


def test_repo_analysis_tests_list():
    """Analysis tests can be listed (pass_to_pass).

    Verify analysis test directory structure is accessible.
    """
    result = subprocess.run(
        ["find", f"{REPO}/analysis", "-name", "*Test*", "-type", "f"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, f"Analysis tests listing failed: {result.stderr}"
    # Should have some test files
    assert len(result.stdout.strip()) > 0, "No analysis test files found"


def test_repo_compiler_structure():
    """Compiler directory structure is valid (pass_to_pass).

    Verify key compiler subdirectories exist.
    """
    dirs = ["fir", "ir", "backend", "psi"]
    for d in dirs:
        result = subprocess.run(
            ["test", "-d", f"{REPO}/compiler/{d}"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, f"compiler/{d} directory missing"


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
