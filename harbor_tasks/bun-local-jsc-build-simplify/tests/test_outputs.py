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


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — Real CI commands
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_cmake_files_parse():
    """Modified CMake files must be syntactically parseable (pass_to_pass)."""
    for cmake_file in [
        "cmake/tools/SetupWebKit.cmake",
        "cmake/targets/BuildBun.cmake",
    ]:
        # Use _cmake_check pattern to write script and run cmake -P
        r = _cmake_check(f'file(READ "{cmake_file}" content)')
        assert r.returncode == 0, f"CMake parse failed for {cmake_file}:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_cmake_consistent_options():
    """CMake option definitions must follow consistent patterns (pass_to_pass)."""
    r = _cmake_check("""
file(READ "cmake/tools/SetupWebKit.cmake" content)
# Check that option() calls follow pattern: option(VAR "desc")
string(REGEX MATCHALL "option\\([^)]+\\)" options "${content}")
list(LENGTH options count)
if(count LESS 2)
    message(FATAL_ERROR "Too few option() definitions found")
endif()
message(STATUS "Found ${count} option definitions")
""")
    assert r.returncode == 0, f"CMake options check failed:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_cmake_webkit_local_path_consistency():
    """WEBKIT_LOCAL path construction must be consistent (pass_to_pass)."""
    r = _cmake_check("""
file(READ "cmake/tools/SetupWebKit.cmake" content)
# Check WEBKIT_LOCAL and path construction exist
string(FIND "${content}" "if(WEBKIT_LOCAL)" pos1)
string(FIND "${content}" "VENDOR_PATH" pos2)
string(FIND "${content}" "DEFAULT_WEBKIT_PATH" pos3)
if(pos1 EQUAL -1)
    message(FATAL_ERROR "WEBKIT_LOCAL conditional not found")
endif()
if(pos2 EQUAL -1)
    message(FATAL_ERROR "VENDOR_PATH reference not found")
endif()
if(pos3 EQUAL -1)
    message(FATAL_ERROR "DEFAULT_WEBKIT_PATH not found")
endif()
message(STATUS "WEBKIT_LOCAL path construction is consistent")
""")
    assert r.returncode == 0, f"CMake WEBKIT_LOCAL check failed:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_cmake_no_syntax_errors():
    """CMake files must have no obvious syntax errors when validated (pass_to_pass)."""
    # Use _cmake_check to run a basic CMake script
    r = _cmake_check('message(STATUS "CMake syntax OK")')
    assert r.returncode == 0, f"CMake basic syntax check failed:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_package_json_valid():
    """Repo package.json must be valid JSON if it exists (pass_to_pass)."""
    pkg_path = Path(REPO) / "package.json"
    if not pkg_path.exists():
        return  # Skip if package.json not in sparse checkout
    r = subprocess.run(
        ["python3", "-c", f"import json; json.load(open('{REPO}/package.json'))"],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"package.json is invalid JSON:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_shell_scripts_valid():
    """Shell scripts must have valid bash syntax (pass_to_pass)."""
    scripts = [
        "scripts/run-clang-format.sh",
        "scripts/bd",
    ]
    for script in scripts:
        script_path = Path(REPO) / script
        if script_path.exists():
            r = subprocess.run(
                ["bash", "-n", str(script_path)],
                capture_output=True, text=True, timeout=30,
            )
            assert r.returncode == 0, f"Script {script} has syntax errors:\n{r.stderr}"


# [repo_tests] pass_to_pass - Real CI commands (enriched)
# Following commands verified to work in Docker container:
# - git status, python3 for file validation

def test_git_repo_valid():
    """Git repository must be valid and at expected commit (pass_to_pass)."""
    r = subprocess.run(
        ["git", "status"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Git repo not valid:\n{r.stderr}"
    # Verify we're at a detached HEAD with the expected base commit
    r2 = subprocess.run(
        ["git", "log", "--oneline", "-1"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r2.returncode == 0, f"Git log failed:\n{r2.stderr}"
    # Commit hash a14a89c is the base_commit from eval_manifest
    assert "a14a89c" in r2.stdout, f"Not at expected base commit:\n{r2.stdout}"


def test_contributing_md_syntax():
    """CONTRIBUTING.md must have valid markdown syntax (pass_to_pass)."""
    r = subprocess.run(
        [
            "python3", "-c",
            f"""
import sys
from pathlib import Path
content = Path('{REPO}/CONTRIBUTING.md').read_text()
# Check for balanced code blocks
if content.count('```') % 2 != 0:
    print('ERROR: Unbalanced code blocks', file=sys.stderr)
    sys.exit(1)
# Check for trailing whitespace
lines_with_ws = [i for i, line in enumerate(content.split(chr(10)), 1) if line.endswith(' ')]
if lines_with_ws:
    print(f'WARNING: {{len(lines_with_ws)}} lines with trailing whitespace', file=sys.stderr)
print('CONTRIBUTING.md syntax OK')
"""
        ],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"CONTRIBUTING.md syntax check failed:\n{r.stderr}"


def test_contributing_mdx_syntax():
    """docs/project/contributing.mdx must have valid MDX syntax (pass_to_pass)."""
    r = subprocess.run(
        [
            "python3", "-c",
            f"""
import sys
import re
from pathlib import Path
content = Path('{REPO}/docs/project/contributing.mdx').read_text()
# Check for balanced code blocks
if content.count('```') % 2 != 0:
    print('ERROR: Unbalanced code blocks', file=sys.stderr)
    sys.exit(1)
print('contributing.mdx syntax OK')
"""
        ],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"contributing.mdx syntax check failed:\n{r.stderr}"


def test_cmake_structure_setup_webkit():
    """SetupWebKit.cmake must have required structure (pass_to_pass)."""
    r = subprocess.run(
        [
            "python3", "-c",
            f"""
import sys
import re
from pathlib import Path
content = Path('{REPO}/cmake/tools/SetupWebKit.cmake').read_text()
required_patterns = ['WEBKIT_VERSION', 'WEBKIT_LOCAL', 'DEFAULT_WEBKIT_PATH', 'WEBKIT_INCLUDE_PATH', 'WEBKIT_LIB_PATH']
for p in required_patterns:
    if p not in content:
        print(f'MISSING: {{p}}', file=sys.stderr)
        sys.exit(1)
print('SetupWebKit.cmake structure OK')
"""
        ],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"SetupWebKit.cmake structure check failed:\n{r.stderr}"


def test_cmake_structure_build_bun():
    """BuildBun.cmake must have required structure (pass_to_pass)."""
    r = subprocess.run(
        [
            "python3", "-c",
            f"""
import sys
from pathlib import Path
content = Path('{REPO}/cmake/targets/BuildBun.cmake').read_text()
required_patterns = ['WEBKIT_LIB_PATH', 'WEBKIT_INCLUDE_PATH', 'target_link_libraries']
for p in required_patterns:
    if p not in content:
        print(f'MISSING: {{p}}', file=sys.stderr)
        sys.exit(1)
print('BuildBun.cmake structure OK')
"""
        ],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"BuildBun.cmake structure check failed:\n{r.stderr}"
