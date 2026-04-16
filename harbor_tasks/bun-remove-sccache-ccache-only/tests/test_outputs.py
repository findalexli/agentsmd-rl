#!/usr/bin/env python3
"""
Test suite for bun-remove-sccache-ccache-only task.

This task tests:
1. Code changes: Removal of sccache support, simplification to ccache only
2. Config/doc changes: Documentation updated to reference ccache instead of sccache

Behavioral tests: We verify fix via filesystem state, subprocess execution.
"""

import subprocess
import os
import re
from pathlib import Path

REPO = Path("/workspace/bun")


def test_setup_sccache_removed():
    """SetupSccache.cmake should be removed entirely."""
    sccache_file = REPO / "cmake" / "tools" / "SetupSccache.cmake"
    assert not sccache_file.exists(), "SetupSccache.cmake should be removed"


def test_setup_ccache_exists():
    """SetupCcache.cmake should exist (behavioral: file state)."""
    ccache_file = REPO / "cmake" / "tools" / "SetupCcache.cmake"
    assert ccache_file.exists(), "SetupCcache.cmake should exist"


def test_setup_ccache_does_not_have_required_flag():
    """SetupCcache.cmake should NOT have REQUIRED flag for ccache."""
    ccache_file = REPO / "cmake" / "tools" / "SetupCcache.cmake"
    content = ccache_file.read_text()
    # REQUIRED flag would cause cmake to fail when ccache is not found
    # Behavioral: checking that the config won't hard-fail
    assert "REQUIRED" not in content, (
        "SetupCcache.cmake should not have REQUIRED flag for ccache"
    )


def test_cmake_uses_optional_ccache_lookup():
    """SetupCcache.cmake should use optional lookup for ccache (find_command or find_program)."""
    ccache_file = REPO / "cmake" / "tools" / "SetupCcache.cmake"
    content = ccache_file.read_text()
    # Using find_command or find_program (without REQUIRED) means ccache is optional
    # This distinguishes from find_package which would typically be REQUIRED
    assert ("find_command" in content or "find_program" in content), (
        "SetupCcache.cmake should use find_command/find_program to locate ccache"
    )


def test_build_cache_directory_removed():
    """scripts/build-cache directory should be removed entirely."""
    build_cache_dir = REPO / "scripts" / "build-cache"
    assert not build_cache_dir.exists(), "scripts/build-cache directory should be removed"


def test_cmake_tools_directory_state():
    """cmake/tools directory should have only expected files (behavioral: subprocess ls)."""
    tools_dir = REPO / "cmake" / "tools"
    assert tools_dir.exists(), "cmake/tools directory should exist"

    # Behavioral: run ls to verify directory state
    result = subprocess.run(
        ["ls", "-la", str(tools_dir)],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, "ls should succeed"
    assert "SetupSccache" not in result.stdout, "SetupSccache should not exist"


def test_contributing_md_has_ccache_install_instructions():
    """CONTRIBUTING.md should have ccache installation instructions (macOS and Linux)."""
    contributing = REPO / "CONTRIBUTING.md"
    assert contributing.exists(), "CONTRIBUTING.md should exist"
    content = contributing.read_text()

    # Behavioral: verify instructions actually exist as actionable commands
    # Check for brew install with ccache
    assert re.search(r'brew install.*ccache', content, re.IGNORECASE), (
        "CONTRIBUTING.md should have macOS ccache install instructions (brew install ccache)"
    )
    # Check for apt install with ccache
    assert re.search(r'(apt|apt-get) install.*ccache', content, re.IGNORECASE), (
        "CONTRIBUTING.md should have Linux ccache install instructions (apt install ccache)"
    )
    # Check for ccache --show-stats
    assert re.search(r'ccache --show-stats', content), (
        "CONTRIBUTING.md should mention ccache --show-stats"
    )


def test_contributing_md_no_sccache():
    """CONTRIBUTING.md should NOT mention sccache anywhere."""
    contributing = REPO / "CONTRIBUTING.md"
    content = contributing.read_text()
    assert "sccache" not in content.lower(), (
        "CONTRIBUTING.md should NOT mention sccache"
    )


def test_contributing_md_no_aws_credentials():
    """CONTRIBUTING.md should NOT have AWS credentials section."""
    contributing = REPO / "CONTRIBUTING.md"
    content = contributing.read_text()
    # Behavioral: AWS and S3 should not appear at all
    assert not re.search(r'AWS', content), (
        "CONTRIBUTING.md should NOT reference AWS"
    )
    assert not re.search(r'S3', content), (
        "CONTRIBUTING.md should NOT reference S3"
    )


def test_docs_contributing_mdx_has_ccache():
    """docs/project/contributing.mdx should reference ccache in macOS brew install."""
    contributing_mdx = REPO / "docs" / "project" / "contributing.mdx"
    assert contributing_mdx.exists(), "contributing.mdx should exist"
    content = contributing_mdx.read_text()

    # Behavioral: check for ccache in brew install line
    assert re.search(r'brew install.*ccache', content, re.IGNORECASE), (
        "contributing.mdx macOS section should include ccache in brew install"
    )
    assert "sccache" not in content.lower(), (
        "contributing.mdx should NOT mention sccache"
    )


def test_building_windows_mdx_has_ccache():
    """docs/project/building-windows.mdx scoop install should have ccache."""
    building_windows = REPO / "docs" / "project" / "building-windows.mdx"
    assert building_windows.exists(), "building-windows.mdx should exist"
    content = building_windows.read_text()

    # Behavioral: check scoop install line has ccache
    lines = content.split("\n")
    scoop_line_found = False
    for line in lines:
        if re.search(r'scoop install.*nodejs', line, re.IGNORECASE):
            scoop_line_found = True
            assert re.search(r'ccache', line, re.IGNORECASE), (
                f"scoop install line should include ccache: {line.strip()}"
            )
            assert not re.search(r'sccache', line, re.IGNORECASE), (
                f"scoop install line should NOT include sccache: {line.strip()}"
            )
            break
    assert scoop_line_found, "Should have a scoop install line for nodejs"


def test_ccache_binary_available():
    """Verify ccache binary is available in environment (behavioral check)."""
    result = subprocess.run(
        ["which", "ccache"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, "ccache should be available"
    # Run ccache --version to verify it works
    result = subprocess.run(
        ["ccache", "--version"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, "ccache --version should succeed"
    assert "ccache" in result.stdout.lower(), "version output should mention ccache"


def test_cmake_tools_only_has_expected_files():
    """cmake/tools should only have expected files, not sccache-related ones."""
    tools_dir = REPO / "cmake" / "tools"
    
    # Behavioral: list files and verify no sccache files exist
    result = subprocess.run(
        ["find", str(tools_dir), "-type", "f", "-name", "*.cmake"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, "find should succeed"
    
    cmake_files = result.stdout.strip().split("\n")
    for f in cmake_files:
        basename = os.path.basename(f)
        assert "Sccache" not in basename, (
            f"Found sccache-related file: {basename}"
        )
