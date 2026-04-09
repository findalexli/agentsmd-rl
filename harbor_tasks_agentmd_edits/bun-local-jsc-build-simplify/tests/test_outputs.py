"""
Task: bun-local-jsc-build-simplify
Repo: oven-sh/bun @ a14a89ca953910e89697895dfdfb4cdf4c90a151
PR:   26645

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/bun"


def _cmake_check(script: str, timeout: int = 15) -> subprocess.CompletedProcess:
    """Run a CMake -P script that reads and validates CMake file content."""
    script_path = Path(REPO) / "_eval_cmake_check.cmake"
    script_path.write_text(script)
    try:
        return subprocess.run(
            ["cmake", "-P", str(script_path)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script_path.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_cmake_files_exist():
    """Modified CMake files and doc files must exist."""
    for f in [
        "cmake/tools/SetupWebKit.cmake",
        "cmake/targets/BuildBun.cmake",
        "CONTRIBUTING.md",
        "docs/project/contributing.mdx",
    ]:
        assert (Path(REPO) / f).exists(), f"{f} does not exist"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — CMake code changes
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_setupwebkit_jsc_configure():
    """SetupWebKit.cmake must contain JSC configure integration with -DPORT=JSCOnly."""
    r = _cmake_check("""
file(READ "cmake/tools/SetupWebKit.cmake" content)
string(FIND "${content}" "-DPORT=JSCOnly" pos1)
string(FIND "${content}" "JSC_CMAKE_ARGS" pos2)
string(FIND "${content}" "execute_process" pos3)
if(pos1 EQUAL -1)
    message(FATAL_ERROR "Missing -DPORT=JSCOnly in SetupWebKit.cmake")
endif()
if(pos2 EQUAL -1)
    message(FATAL_ERROR "Missing JSC_CMAKE_ARGS in SetupWebKit.cmake")
endif()
if(pos3 EQUAL -1)
    message(FATAL_ERROR "Missing execute_process for JSC configure in SetupWebKit.cmake")
endif()
message(STATUS "JSC configure integration found")
""")
    assert r.returncode == 0, f"CMake check failed:\n{r.stderr}"


# [pr_diff] fail_to_pass
def test_setupwebkit_webkit_build_type():
    """SetupWebKit.cmake must define WEBKIT_BUILD_TYPE option."""
    r = _cmake_check("""
file(READ "cmake/tools/SetupWebKit.cmake" content)
string(FIND "${content}" "option(WEBKIT_BUILD_TYPE" pos)
if(pos EQUAL -1)
    message(FATAL_ERROR "WEBKIT_BUILD_TYPE option not found in SetupWebKit.cmake")
endif()
message(STATUS "WEBKIT_BUILD_TYPE option found")
""")
    assert r.returncode == 0, f"CMake check failed:\n{r.stderr}"


# [pr_diff] fail_to_pass
def test_setupwebkit_jsc_custom_target():
    """SetupWebKit.cmake must define a 'jsc' custom target for building JSC."""
    r = _cmake_check("""
file(READ "cmake/tools/SetupWebKit.cmake" content)
string(FIND "${content}" "add_custom_target(jsc" pos)
if(pos EQUAL -1)
    message(FATAL_ERROR "add_custom_target(jsc not found in SetupWebKit.cmake")
endif()
message(STATUS "jsc custom target found")
""")
    assert r.returncode == 0, f"CMake check failed:\n{r.stderr}"


# [pr_diff] fail_to_pass
def test_buildbun_jsc_dependency():
    """BuildBun.cmake must add jsc as a build dependency for local WebKit builds."""
    r = _cmake_check("""
file(READ "cmake/targets/BuildBun.cmake" content)
string(FIND "${content}" "add_dependencies" pos1)
string(FIND "${content}" "TARGET jsc" pos2)
if(pos1 EQUAL -1 OR pos2 EQUAL -1)
    message(FATAL_ERROR "add_dependencies with jsc target not found in BuildBun.cmake")
endif()
message(STATUS "jsc dependency found in BuildBun.cmake")
""")
    assert r.returncode == 0, f"CMake check failed:\n{r.stderr}"


# [pr_diff] fail_to_pass
def test_buildbun_system_icu_for_local():
    """BuildBun.cmake must use find_package(ICU) for WEBKIT_LOCAL builds on Linux."""
    r = _cmake_check("""
file(READ "cmake/targets/BuildBun.cmake" content)
string(FIND "${content}" "find_package(ICU" pos)
if(pos EQUAL -1)
    message(FATAL_ERROR "find_package(ICU not found in BuildBun.cmake")
endif()
message(STATUS "find_package(ICU) found in BuildBun.cmake")
""")
    assert r.returncode == 0, f"CMake check failed:\n{r.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — Documentation updates
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_contributing_simplified_build():
    """CONTRIBUTING.md must describe build:local as handling JSC configure + build."""
    content = (Path(REPO) / "CONTRIBUTING.md").read_text()
    lower = content.lower()
    # Must explain that build:local handles JSC configuration and building
    assert "configuring jsc" in lower or "handles everything" in lower, \
        "CONTRIBUTING.md should explain that build:local configures and builds JSC"
    # Must mention incremental JSC rebuilds specifically
    assert "incrementally rebuild" in lower or "incremental rebuild" in lower, \
        "CONTRIBUTING.md should mention incremental JSC rebuilds near build:local"


# [pr_diff] fail_to_pass
def test_contributing_no_manual_jsc_steps():
    """CONTRIBUTING.md must not contain the old manual jsc:build:debug steps."""
    content = (Path(REPO) / "CONTRIBUTING.md").read_text()
    assert "jsc:build:debug" not in content, \
        "CONTRIBUTING.md should not reference manual jsc:build:debug command"
    assert "InspectorProtocolObjects.h" not in content, \
        "CONTRIBUTING.md should not reference manual InspectorProtocolObjects.h deletion"


# [pr_diff] fail_to_pass
def test_contributing_mdx_simplified():
    """docs/project/contributing.mdx must also describe build:local as handling JSC build."""
    content = (Path(REPO) / "docs/project/contributing.mdx").read_text()
    lower = content.lower()
    assert "configuring jsc" in lower or "handles everything" in lower, \
        "contributing.mdx should explain that build:local configures and builds JSC"
    assert "jsc:build:debug" not in content, \
        "contributing.mdx should not reference manual jsc:build:debug command"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — Regression checks
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_setupwebkit_retains_prebuilt_path():
    """SetupWebKit.cmake must still support prebuilt WebKit downloads."""
    r = _cmake_check("""
file(READ "cmake/tools/SetupWebKit.cmake" content)
string(FIND "${content}" "WEBKIT_VERSION" pos1)
string(FIND "${content}" "CACHE_PATH" pos2)
if(pos1 EQUAL -1)
    message(FATAL_ERROR "WEBKIT_VERSION not found - prebuilt support broken")
endif()
if(pos2 EQUAL -1)
    message(FATAL_ERROR "CACHE_PATH not found - prebuilt download path broken")
endif()
message(STATUS "Prebuilt WebKit path retained")
""")
    assert r.returncode == 0, f"CMake check failed:\n{r.stderr}"
