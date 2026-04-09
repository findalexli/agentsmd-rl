"""
Task: bun-simplify-local-jsc-build
Repo: oven-sh/bun @ a14a89ca953910e89697895dfdfb4cdf4c90a151
PR:   26645

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/bun"


def _run_cmake_script(script: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Run a CMake script via cmake -P to verify cmake file contents and logic."""
    script_path = Path(REPO) / "_eval_check.cmake"
    script_path.write_text(script)
    try:
        return subprocess.run(
            ["cmake", "-P", str(script_path)],
            capture_output=True, text=True, timeout=timeout,
        )
    finally:
        script_path.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_setupwebkit_retains_webkit_version():
    """SetupWebKit.cmake must still define WEBKIT_VERSION."""
    result = _run_cmake_script(f"""
file(READ "{REPO}/cmake/tools/SetupWebKit.cmake" content)
string(FIND "${{content}}" "set(WEBKIT_VERSION" pos)
if(pos EQUAL -1)
  message(FATAL_ERROR "SetupWebKit.cmake missing WEBKIT_VERSION definition")
endif()
message(STATUS "OK: WEBKIT_VERSION found")
""")
    assert result.returncode == 0, f"Missing WEBKIT_VERSION: {result.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — cmake code changes
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_setupwebkit_defines_jsc_build_target():
    """SetupWebKit.cmake must define a jsc custom build target for local builds."""
    result = _run_cmake_script(f"""
file(READ "{REPO}/cmake/tools/SetupWebKit.cmake" content)

# Check for add_custom_target(jsc
string(FIND "${{content}}" "add_custom_target(jsc" pos1)
if(pos1 EQUAL -1)
  message(FATAL_ERROR "Missing add_custom_target(jsc")
endif()

# Check for BYPRODUCTS (required for proper dependency tracking)
string(FIND "${{content}}" "BYPRODUCTS" pos2)
if(pos2 EQUAL -1)
  message(FATAL_ERROR "Missing BYPRODUCTS in jsc target")
endif()

# Check that it builds the jsc target
string(FIND "${{content}}" "--target jsc" pos3)
if(pos3 EQUAL -1)
  message(FATAL_ERROR "Missing --target jsc in build command")
endif()

message(STATUS "OK: jsc custom target properly defined")
""")
    assert result.returncode == 0, f"jsc target not properly defined: {result.stderr}"


# [pr_diff] fail_to_pass
def test_setupwebkit_configures_jsc_cmake_args():
    """SetupWebKit.cmake must configure JSC with proper cmake flags."""
    result = _run_cmake_script(f"""
file(READ "{REPO}/cmake/tools/SetupWebKit.cmake" content)

# Check for JSC_CMAKE_ARGS list definition
string(FIND "${{content}}" "set(JSC_CMAKE_ARGS" pos1)
if(pos1 EQUAL -1)
  message(FATAL_ERROR "Missing JSC_CMAKE_ARGS definition")
endif()

# Check for required cmake arguments
string(FIND "${{content}}" "-DPORT=JSCOnly" pos2)
if(pos2 EQUAL -1)
  message(FATAL_ERROR "Missing -DPORT=JSCOnly")
endif()

string(FIND "${{content}}" "-DENABLE_STATIC_JSC=ON" pos3)
if(pos3 EQUAL -1)
  message(FATAL_ERROR "Missing -DENABLE_STATIC_JSC=ON")
endif()

# Check for execute_process that configures JSC
string(FIND "${{content}}" "execute_process(COMMAND ${{CMAKE_COMMAND}} ${{JSC_CMAKE_ARGS}}" pos4)
if(pos4 EQUAL -1)
  message(FATAL_ERROR "Missing execute_process for JSC configuration")
endif()

message(STATUS "OK: JSC cmake args properly configured")
""")
    assert result.returncode == 0, f"JSC cmake args not properly configured: {result.stderr}"


# [pr_diff] fail_to_pass
def test_setupwebkit_webkit_build_type_option():
    """SetupWebKit.cmake must support a WEBKIT_BUILD_TYPE option with proper default."""
    result = _run_cmake_script(f"""
file(READ "{REPO}/cmake/tools/SetupWebKit.cmake" content)

# Check for WEBKIT_BUILD_TYPE option declaration
string(FIND "${{content}}" "option(WEBKIT_BUILD_TYPE" pos1)
if(pos1 EQUAL -1)
  message(FATAL_ERROR "Missing WEBKIT_BUILD_TYPE option declaration")
endif()

# Check for default value assignment from CMAKE_BUILD_TYPE
string(FIND "${{content}}" "set(WEBKIT_BUILD_TYPE ${{CMAKE_BUILD_TYPE}})" pos2)
if(pos2 EQUAL -1)
  # Alternative: check for the if(NOT WEBKIT_BUILD_TYPE) pattern
  string(FIND "${{content}}" "if(NOT WEBKIT_BUILD_TYPE)" pos3)
  if(pos3 EQUAL -1)
    message(FATAL_ERROR "Missing WEBKIT_BUILD_TYPE default logic")
  endif()
endif()

# Check that DEFAULT_WEBKIT_PATH uses WEBKIT_BUILD_TYPE (not CMAKE_BUILD_TYPE directly)
string(FIND "${{content}}" "WebKitBuild/${{WEBKIT_BUILD_TYPE}}" pos4)
if(pos4 EQUAL -1)
  message(FATAL_ERROR "DEFAULT_WEBKIT_PATH should use WEBKIT_BUILD_TYPE variable")
endif()

message(STATUS "OK: WEBKIT_BUILD_TYPE option properly defined")
""")
    assert result.returncode == 0, f"WEBKIT_BUILD_TYPE option not properly defined: {result.stderr}"


# [pr_diff] fail_to_pass
def test_buildbun_jsc_dependency():
    """BuildBun.cmake must add jsc as a build dependency for local WebKit."""
    result = _run_cmake_script(f"""
file(READ "{REPO}/cmake/targets/BuildBun.cmake" content)

# Check for WEBKIT_LOCAL guard around add_dependencies
string(FIND "${{content}}" "if(WEBKIT_LOCAL AND TARGET jsc)" pos1)
if(pos1 EQUAL -1)
  string(FIND "${{content}}" "WEBKIT_LOCAL" pos_alt)
  if(pos_alt EQUAL -1)
    message(FATAL_ERROR "Missing WEBKIT_LOCAL check for jsc dependency")
  endif()
endif()

# Check for add_dependencies call with jsc
string(FIND "${{content}}" "add_dependencies(${{bun}} jsc)" pos2)
if(pos2 EQUAL -1)
  # Try alternative patterns
  string(FIND "${{content}}" "add_dependencies" pos3)
  string(FIND "${{content}}" " jsc)" pos4)
  if(pos3 EQUAL -1 OR pos4 EQUAL -1)
    message(FATAL_ERROR "Missing add_dependencies with jsc target")
  endif()
endif()

message(STATUS "OK: jsc dependency properly added")
""")
    assert result.returncode == 0, f"jsc dependency not properly added: {result.stderr}"


# [pr_diff] fail_to_pass
def test_buildbun_system_icu_local():
    """BuildBun.cmake must use system ICU via find_package for local builds on Linux."""
    result = _run_cmake_script(f"""
file(READ "{REPO}/cmake/targets/BuildBun.cmake" content)

# Check for WEBKIT_LOCAL conditional around ICU linking
string(FIND "${{content}}" "if(WEBKIT_LOCAL)" pos1)
if(pos1 EQUAL -1)
  message(FATAL_ERROR "Missing if(WEBKIT_LOCAL) for ICU handling")
endif()

# Check for find_package(ICU
string(FIND "${{content}}" "find_package(ICU" pos2)
if(pos2 EQUAL -1)
  message(FATAL_ERROR "Missing find_package(ICU)")
endif()

# Check for ICU::data ICU::i18n ICU::uc targets
string(FIND "${{content}}" "ICU::data" pos3)
string(FIND "${{content}}" "ICU::i18n" pos4)
string(FIND "${{content}}" "ICU::uc" pos5)
if(pos3 EQUAL -1 OR pos4 EQUAL -1 OR pos5 EQUAL -1)
  message(FATAL_ERROR "Missing ICU::data/ICU::i18n/ICU::uc target_link_libraries")
endif()

# Check for else() branch that uses static .a files (for non-local builds)
string(FIND "${{content}}" "libicudata.a" pos6)
if(pos6 EQUAL -1)
  message(FATAL_ERROR "Missing libicudata.a fallback (should be in else branch)")
endif()

message(STATUS "OK: System ICU properly configured for local builds")
""")
    assert result.returncode == 0, f"System ICU not properly configured: {result.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — config/documentation updates
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_contributing_simplified_local_build():
    """CONTRIBUTING.md must simplify the local JSC build to a single command."""
    content = Path(f"{REPO}/CONTRIBUTING.md").read_text()

    # Old manual multi-step process should be removed
    assert "jsc:build:debug" not in content, \
        "CONTRIBUTING.md still has manual jsc:build:debug step"
    assert "InspectorProtocolObjects" not in content, \
        "CONTRIBUTING.md still references manual InspectorProtocolObjects.h deletion"
    assert "cmake --build vendor/WebKit" not in content, \
        "CONTRIBUTING.md still has manual cmake --build command"

    # New simplified instructions should explain build:local handles everything
    lower = content.lower()
    assert "handles everything" in lower or "automatically" in lower, \
        "CONTRIBUTING.md should explain that build:local handles JSC automatically"

    # Should reference the simplified single command
    assert "bun run build:local" in content, \
        "CONTRIBUTING.md should reference bun run build:local command"


# [pr_diff] fail_to_pass
def test_contributing_mdx_simplified():
    """docs/project/contributing.mdx must match the simplified build instructions."""
    content = Path(f"{REPO}/docs/project/contributing.mdx").read_text()

    # Old manual multi-step process should be removed
    assert "jsc:build:debug" not in content, \
        "contributing.mdx still has manual jsc:build:debug step"
    assert "InspectorProtocolObjects" not in content, \
        "contributing.mdx still references manual InspectorProtocolObjects.h deletion"
    assert "cmake --build vendor/WebKit" not in content, \
        "contributing.mdx still has manual cmake --build command"

    # New simplified instructions should explain build:local handles everything
    lower = content.lower()
    assert "handles everything" in lower or "automatically" in lower, \
        "contributing.mdx should explain that build:local handles JSC automatically"

    # Should reference the simplified single command
    assert "bun run build:local" in content, \
        "contributing.mdx should reference bun run build:local command"
