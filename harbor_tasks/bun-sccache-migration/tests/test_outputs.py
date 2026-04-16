#!/usr/bin/env python3
"""
Tests for sccache migration in Bun build system.

This validates:
1. SetupSccache.cmake exists and is properly configured
2. SetupCcache.cmake is removed
3. CMakeLists.txt uses SetupSccache
4. CONTRIBUTING.md documents sccache installation
5. Build scripts reference sccache instead of ccache
"""

import subprocess
import sys
from pathlib import Path

REPO = Path("/workspace/bun")


def test_sccache_cmake_module_exists():
    """[f2p] SetupSccache.cmake must exist with proper S3 configuration."""
    sccache_cmake = REPO / "cmake" / "tools" / "SetupSccache.cmake"
    assert sccache_cmake.exists(), "SetupSccache.cmake should exist"

    content = sccache_cmake.read_text()
    assert "SCCACHE_BUCKET" in content, "Should configure S3 bucket"
    assert "bun-build-sccache-store" in content, "Should use correct bucket name"
    assert "SCCACHE_REGION" in content, "Should configure S3 region"
    assert "us-west-1" in content, "Should use correct region"
    assert "check_aws_credentials" in content, "Should check AWS credentials"
    assert "check_running_in_ci" in content, "Should detect CI environment"


def test_ccache_cmake_module_removed():
    """[f2p] SetupCcache.cmake must be removed."""
    ccache_cmake = REPO / "cmake" / "tools" / "SetupCcache.cmake"
    assert not ccache_cmake.exists(), "SetupCcache.cmake should be removed"


def test_cmake_lists_uses_sccache():
    """[f2p] CMakeLists.txt must include SetupSccache instead of SetupCcache."""
    cmake_lists = REPO / "CMakeLists.txt"
    content = cmake_lists.read_text()

    assert "include(SetupSccache)" in content, "Should include SetupSccache"
    assert "include(SetupCcache)" not in content, "Should not include SetupCcache"


def test_contributing_documents_sccache():
    """[f2p] CONTRIBUTING.md must document sccache installation and configuration."""
    contributing = REPO / "CONTRIBUTING.md"
    content = contributing.read_text()

    # Should mention sccache in the install section
    assert "sccache" in content.lower(), "Should mention sccache"

    # Should have a section about installing sccache
    assert "### Optional: Install `sccache`" in content or "### Install `sccache`" in content, \
        "Should have sccache installation section"

    # Should document S3 support
    assert "S3" in content, "Should mention S3 support"

    # Should have AWS credentials documentation
    assert "AWS" in content, "Should document AWS credentials"

    # Should document sccache --show-stats
    assert "sccache --show-stats" in content, "Should document stats command"


def test_contributing_no_ccache():
    """[f2p] CONTRIBUTING.md should not reference ccache in package lists."""
    contributing = REPO / "CONTRIBUTING.md"
    content = contributing.read_text()

    # Check the package install sections don't have ccache
    lines = content.split('\n')
    in_code_block = False
    for line in lines:
        if '```bash' in line:
            in_code_block = True
        elif '```' in line and in_code_block:
            in_code_block = False
        elif in_code_block and 'ccache' in line and 'sccache' not in line:
            assert False, f"Found ccache (not sccache) in package list: {line}"


def test_contributing_no_ccache_troubleshooting():
    """[f2p] CONTRIBUTING.md should remove ccache troubleshooting section."""
    contributing = REPO / "CONTRIBUTING.md"
    content = contributing.read_text()

    assert "ccache conflicts with building TinyCC" not in content, \
        "Should remove ccache troubleshooting section"


def test_globals_cmake_cache_strategy():
    """[f2p] cmake/Globals.cmake should remove write-only cache strategy option."""
    globals_cmake = REPO / "cmake" / "Globals.cmake"
    content = globals_cmake.read_text()

    # Should not have write-only in the options
    assert 'read-write|read-only|write-only|none' not in content, \
        "Should remove write-only option"
    assert 'read-write|read-only|none' in content, \
        "Should have read-write|read-only|none options"


def test_flake_nix_uses_sccache():
    """[f2p] flake.nix should use sccache instead of ccache."""
    flake_nix = REPO / "flake.nix"
    if flake_nix.exists():
        content = flake_nix.read_text()
        assert "pkgs.sccache" in content, "Should use pkgs.sccache"
        assert "pkgs.ccache" not in content, "Should not use pkgs.ccache"


def test_shell_nix_uses_sccache():
    """[f2p] shell.nix should use sccache instead of ccache."""
    shell_nix = REPO / "shell.nix"
    if shell_nix.exists():
        content = shell_nix.read_text()
        assert "sccache" in content, "Should mention sccache"
        assert "ccache" not in content, "Should not mention ccache"


def test_docs_windows_uses_sccache():
    """[f2p] docs/project/building-windows.mdx should use sccache."""
    docs_windows = REPO / "docs" / "project" / "building-windows.mdx"
    if docs_windows.exists():
        content = docs_windows.read_text()
        assert "sccache" in content.lower(), "Should mention sccache"
        assert "ccache" not in content.lower(), "Should not mention ccache"


def test_bootstrap_sh_uses_sccache():
    """[f2p] scripts/bootstrap.sh should use install_sccache instead of install_ccache."""
    bootstrap_sh = REPO / "scripts" / "bootstrap.sh"
    content = bootstrap_sh.read_text()

    assert "install_sccache" in content, "Should have install_sccache function"
    assert "install_ccache" not in content, "Should not reference install_ccache"


def test_bootstrap_sh_sccache_download():
    """[f2p] scripts/bootstrap.sh should download sccache from GitHub releases."""
    bootstrap_sh = REPO / "scripts" / "bootstrap.sh"
    content = bootstrap_sh.read_text()

    assert "github.com/mozilla/sccache/releases/download" in content, \
        "Should download sccache from GitHub releases"
    assert "v0.12.0" in content, "Should use sccache v0.12.0"


def test_cmake_parses():
    """[p2p] CMakeLists.txt should be valid CMake syntax."""
    result = subprocess.run(
        ["cmake", "-P", "-"],
        input="include(/workspace/bun/cmake/Globals.cmake)\n",
        capture_output=True,
        text=True,
        cwd=REPO
    )
    # Just check that cmake doesn't crash immediately on syntax
    # The full CMake configure requires many dependencies
    assert result.returncode == 0 or "could not find" in result.stderr.lower(), \
        f"CMake syntax error: {result.stderr}"


def test_build_mjs_sccache_stats():
    """[f2p] scripts/build.mjs should show sccache stats after build."""
    build_mjs = REPO / "scripts" / "build.mjs"
    content = build_mjs.read_text()

    assert 'sccache --show-stats' in content, \
        "Should show sccache stats after build"
    assert 'startGroup("sccache stats"' in content, \
        "Should have sccache stats group"


def test_build_mjs_no_ccache_functions():
    """[f2p] scripts/build.mjs should remove ccache-related functions."""
    build_mjs = REPO / "scripts" / "build.mjs"
    content = build_mjs.read_text()

    # Should not have old ccache functions
    assert "isCacheReadEnabled" not in content, "Should remove isCacheReadEnabled"
    assert "isCacheWriteEnabled" not in content, "Should remove isCacheWriteEnabled"
    assert "getCachePath" not in content, "Should remove getCachePath"
    assert "getDefaultBranch" not in content, "Should remove getDefaultBranch"


def test_build_mjs_imports():
    """[p2p] scripts/build.mjs should have correct fs imports."""
    build_mjs = REPO / "scripts" / "build.mjs"
    content = build_mjs.read_text()

    # Should not import removed functions
    assert "chmodSync" not in content, "Should not import chmodSync"
    assert "cpSync" not in content, "Should not import cpSync"
    assert "mkdirSync" not in content, "Should not import mkdirSync"


def test_machine_mjs_iam_profile():
    """[f2p] scripts/machine.mjs should attach IAM instance profile for CI."""
    machine_mjs = REPO / "scripts" / "machine.mjs"
    content = machine_mjs.read_text()

    assert "iam-instance-profile" in content, "Should set IAM instance profile"
    assert "buildkite-build-agent" in content, "Should use buildkite-build-agent IAM role"
    assert 'args["ci"]' in content, "Should check CI flag"


def test_machine_mjs_service_tag():
    """[f2p] scripts/machine.mjs should set Service tag for S3 cache access."""
    machine_mjs = REPO / "scripts" / "machine.mjs"
    content = machine_mjs.read_text()

    assert '"Service":' in content, "Should set Service tag"
    assert 'buildkite-agent' in content, "Should set buildkite-agent as Service"


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
