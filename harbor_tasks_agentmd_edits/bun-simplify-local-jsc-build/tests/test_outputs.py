"""Test outputs for bun PR #26645 - Simplify local JSC build.

This module contains pass_to_pass and fail_to_pass tests for validating
changes to the local WebKit/JSC build process in the Bun repository.
"""

import subprocess

REPO = "/workspace/bun"


def test_setupwebkit_retains_webkit_version():
    """SetupWebKit.cmake still defines WEBKIT_VERSION (pass_to_pass)."""
    r = subprocess.run(
        ["grep", "option(WEBKIT_VERSION", f"{REPO}/cmake/tools/SetupWebKit.cmake"],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert r.returncode == 0, "WEBKIT_VERSION option not found in SetupWebKit.cmake"


def test_setupwebkit_defines_jsc_build_target():
    """SetupWebKit.cmake defines a jsc custom build target for local builds (fail_to_pass)."""
    r = subprocess.run(
        ["grep", "add_custom_target(jsc", f"{REPO}/cmake/tools/SetupWebKit.cmake"],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert r.returncode == 0, "add_custom_target(jsc) not found in SetupWebKit.cmake"


def test_setupwebkit_configures_jsc_cmake_args():
    """SetupWebKit.cmake configures JSC with PORT=JSCOnly and ENABLE_STATIC_JSC (fail_to_pass)."""
    content = subprocess.run(
        ["cat", f"{REPO}/cmake/tools/SetupWebKit.cmake"],
        capture_output=True,
        text=True,
        timeout=10,
    ).stdout

    assert "-DPORT=JSCOnly" in content, "PORT=JSCOnly not found in JSC_CMAKE_ARGS"
    assert "-DENABLE_STATIC_JSC=ON" in content, "ENABLE_STATIC_JSC not found in JSC_CMAKE_ARGS"


def test_setupwebkit_webkit_build_type_option():
    """SetupWebKit.cmake supports WEBKIT_BUILD_TYPE option (fail_to_pass)."""
    r = subprocess.run(
        ["grep", "option(WEBKIT_BUILD_TYPE", f"{REPO}/cmake/tools/SetupWebKit.cmake"],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert r.returncode == 0, "WEBKIT_BUILD_TYPE option not found in SetupWebKit.cmake"


def test_buildbun_jsc_dependency():
    """BuildBun.cmake adds jsc as a build dependency for local WebKit (fail_to_pass)."""
    r = subprocess.run(
        ["grep", "add_dependencies.*jsc", f"{REPO}/cmake/targets/BuildBun.cmake"],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert r.returncode == 0, "add_dependencies with jsc not found in BuildBun.cmake"


def test_buildbun_system_icu_local():
    """BuildBun.cmake uses system ICU via find_package for local builds on Linux (fail_to_pass)."""
    content = subprocess.run(
        ["cat", f"{REPO}/cmake/targets/BuildBun.cmake"],
        capture_output=True,
        text=True,
        timeout=10,
    ).stdout

    # Check for find_package(ICU and ICU::data linking
    assert "find_package(ICU" in content, "find_package(ICU) not found in BuildBun.cmake"
    assert "ICU::data" in content, "ICU::data linking not found in BuildBun.cmake"


def test_contributing_simplified_local_build():
    """CONTRIBUTING.md simplifies local JSC build instructions to single command (fail_to_pass)."""
    content = subprocess.run(
        ["cat", f"{REPO}/CONTRIBUTING.md"],
        capture_output=True,
        text=True,
        timeout=10,
    ).stdout

    # Check for the simplified single-command build instruction
    assert "bun run build:local" in content, "Simplified 'bun run build:local' instruction not found"
    # Make sure old complex instructions are removed
    assert "bun run jsc:build:debug" not in content, "Old jsc:build:debug instruction should be removed"


def test_contributing_mdx_simplified():
    """docs/project/contributing.mdx matches simplified build instructions (fail_to_pass)."""
    content = subprocess.run(
        ["cat", f"{REPO}/docs/project/contributing.mdx"],
        capture_output=True,
        text=True,
        timeout=10,
    ).stdout

    # Check for the simplified single-command build instruction
    assert "bun run build:local" in content, "Simplified 'bun run build:local' instruction not found"
    # Make sure old complex instructions are removed
    assert "bun run jsc:build:debug" not in content, "Old jsc:build:debug instruction should be removed"
