#!/usr/bin/env python3
"""
Test suite for bun PR: Simplify local WebKit builds and auto-configure JSC

Validates that:
1. cmake/tools/SetupWebKit.cmake adds WEBKIT_BUILD_TYPE and auto-configures/builds JSC
2. cmake/targets/BuildBun.cmake adds JSC build dependency and uses system ICU for local builds
3. CONTRIBUTING.md and docs/project/contributing.mdx simplify local build instructions
"""

import subprocess
import sys
from pathlib import Path

REPO = Path("/workspace/bun")


def _run_cmake_check(cmake_script: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Run a cmake -P script to validate cmake file contents."""
    script_path = REPO / "_eval_cmake_check.cmake"
    script_path.write_text(cmake_script)
    try:
        return subprocess.run(
            ["cmake", "-P", str(script_path)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script_path.unlink(missing_ok=True)


# =============================================================================
# Pass-to-Pass Tests
# =============================================================================


def test_setup_webkit_cmake_exists():
    """cmake/tools/SetupWebKit.cmake must exist and reference WEBKIT_LOCAL."""
    fp = REPO / "cmake" / "tools" / "SetupWebKit.cmake"
    assert fp.exists(), f"File not found: {fp}"
    content = fp.read_text()
    assert "WEBKIT_LOCAL" in content, "SetupWebKit.cmake should reference WEBKIT_LOCAL"


def test_build_bun_cmake_exists():
    """cmake/targets/BuildBun.cmake must exist and reference WEBKIT_LIB_PATH."""
    fp = REPO / "cmake" / "targets" / "BuildBun.cmake"
    assert fp.exists(), f"File not found: {fp}"
    content = fp.read_text()
    assert "WEBKIT_LIB_PATH" in content, "BuildBun.cmake should reference WEBKIT_LIB_PATH"


def test_contributing_docs_exist():
    """CONTRIBUTING.md and docs/project/contributing.mdx must exist."""
    assert (REPO / "CONTRIBUTING.md").exists(), "CONTRIBUTING.md not found"
    assert (REPO / "docs" / "project" / "contributing.mdx").exists(), "contributing.mdx not found"


# =============================================================================
# Fail-to-Pass Tests
# =============================================================================


def test_setup_webkit_build_type_option():
    """SetupWebKit.cmake must define WEBKIT_BUILD_TYPE so the local JSC build
    type can be set independently of CMAKE_BUILD_TYPE."""
    r = _run_cmake_check(f"""
file(READ "{REPO}/cmake/tools/SetupWebKit.cmake" content)
string(FIND "${{content}}" "WEBKIT_BUILD_TYPE" idx)
if(idx EQUAL -1)
  message(FATAL_ERROR "WEBKIT_BUILD_TYPE not found in SetupWebKit.cmake")
endif()
message(STATUS "PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in (r.stdout + r.stderr)


def test_setup_webkit_auto_configures_jsc():
    """SetupWebKit.cmake must auto-configure JSC by invoking cmake via
    execute_process when WEBKIT_LOCAL is set, removing the need for manual
    pre-build steps."""
    r = _run_cmake_check(f"""
file(READ "{REPO}/cmake/tools/SetupWebKit.cmake" content)
string(FIND "${{content}}" "execute_process" idx)
if(idx EQUAL -1)
  message(FATAL_ERROR "No execute_process found — JSC must be auto-configured")
endif()
message(STATUS "PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in (r.stdout + r.stderr)


def test_setup_webkit_jsc_build_target():
    """SetupWebKit.cmake must create a jsc build target via add_custom_target
    so that JSC is built as part of the normal build process."""
    r = _run_cmake_check(f"""
file(READ "{REPO}/cmake/tools/SetupWebKit.cmake" content)
string(FIND "${{content}}" "add_custom_target" idx)
if(idx EQUAL -1)
  message(FATAL_ERROR "No add_custom_target found — must create a jsc build target")
endif()
message(STATUS "PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in (r.stdout + r.stderr)


def test_setup_webkit_no_vcpkg():
    """SetupWebKit.cmake must not use vcpkg for ICU. Windows ICU should be
    built from source instead."""
    r = _run_cmake_check(f"""
file(READ "{REPO}/cmake/tools/SetupWebKit.cmake" content)
string(FIND "${{content}}" "vcpkg" idx)
if(NOT idx EQUAL -1)
  message(FATAL_ERROR "SetupWebKit.cmake still references vcpkg")
endif()
message(STATUS "PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in (r.stdout + r.stderr)


def test_buildbun_jsc_build_dependency():
    """BuildBun.cmake must add a build dependency (add_dependencies) to ensure
    JSC is compiled before Bun's C++ sources when using a local WebKit."""
    r = _run_cmake_check(f"""
file(READ "{REPO}/cmake/targets/BuildBun.cmake" content)
string(FIND "${{content}}" "add_dependencies" idx)
if(idx EQUAL -1)
  message(FATAL_ERROR "No add_dependencies found — must enforce JSC build order")
endif()
message(STATUS "PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in (r.stdout + r.stderr)


def test_buildbun_system_icu_for_local():
    """BuildBun.cmake must use find_package(ICU) for local WebKit builds on
    Linux instead of hardcoded paths to prebuilt ICU static libraries."""
    r = _run_cmake_check(f"""
file(READ "{REPO}/cmake/targets/BuildBun.cmake" content)
string(FIND "${{content}}" "find_package(ICU" idx)
if(idx EQUAL -1)
  message(FATAL_ERROR "No find_package(ICU) found — local builds must use system ICU")
endif()
message(STATUS "PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in (r.stdout + r.stderr)


def test_contributing_no_manual_jsc_build():
    """CONTRIBUTING.md must not contain the old multi-step manual JSC build
    commands (jsc:build:debug && rm, cmake --build vendor/WebKit/WebKitBuild).
    The typo 'change make changes' must also be fixed."""
    r = subprocess.run(
        ["python3", "-c", """
from pathlib import Path
content = Path("/workspace/bun/CONTRIBUTING.md").read_text()

# Old multi-step manual commands must be removed
assert "jsc:build:debug && rm" not in content, \
    "Old manual jsc:build:debug command still present"
assert "cmake --build vendor/WebKit/WebKitBuild" not in content, \
    "Old manual cmake --build command still present"

# Typo must be fixed
assert "change make changes" not in content, \
    "Typo 'change make changes' not fixed"

print("PASS")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_contributing_mdx_no_manual_jsc_build():
    """docs/project/contributing.mdx must also remove the old multi-step
    manual JSC build commands, matching the CONTRIBUTING.md changes."""
    r = subprocess.run(
        ["python3", "-c", """
from pathlib import Path
content = Path("/workspace/bun/docs/project/contributing.mdx").read_text()

# Old multi-step manual commands must be removed
assert "jsc:build:debug && rm" not in content, \
    "Old manual jsc:build:debug command still present in contributing.mdx"
assert "cmake --build vendor/WebKit/WebKitBuild" not in content, \
    "Old manual cmake --build command still present in contributing.mdx"

# Typo must be fixed
assert "change make changes" not in content, \
    "Typo 'change make changes' not fixed in contributing.mdx"

print("PASS")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
