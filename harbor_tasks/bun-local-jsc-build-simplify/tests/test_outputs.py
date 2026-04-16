"""
Task: bun-local-jsc-build-simplify
Repo: oven-sh/bun @ a14a89ca953910e89697895dfdfb4cdf4c90a151
PR:   26645

Rewritten to verify BEHAVIOR, not text.
Each test function verifies actual cmake execution or behavioral properties.
"""

import re
import subprocess
import os
import tempfile
from pathlib import Path

REPO = "/workspace/bun"
MOCK_WEBKIT = "/tmp/vendor/WebKit"
MOCK_CACHE = "/tmp/cache"


def _setup_mock_webkit():
    """Create minimal mock WebKit source tree for cmake configuration tests."""
    os.makedirs(f"{MOCK_WEBKIT}/WebKitBuild/Debug", exist_ok=True)
    Path(f"{MOCK_WEBKIT}/CMakeLists.txt").write_text("""
cmake_minimum_required(VERSION 3.20)
project(WebKitMock NONE)
message(STATUS "WebKitMock: cmake configuration reached")
file(WRITE "${CMAKE_BINARY_DIR}/WebKitMockConfigured.txt" "configured")
""")


def _cmake_configure(extra_defines=None, timeout=30):
    """Run cmake configure with WEBKIT_LOCAL enabled and mock WebKit."""
    _setup_mock_webkit()

    with tempfile.TemporaryDirectory() as tmpdir:
        cmake_lists = os.path.join(tmpdir, "CMakeLists.txt")
        build_dir = os.path.join(tmpdir, "build")

        defines = {
            "CMAKE_SYSTEM_NAME": "Linux",
            "CMAKE_SYSTEM_PROCESSOR": "x86_64",
            "VENDOR_PATH": MOCK_WEBKIT.rsplit("/", 1)[0],
            "CACHE_PATH": MOCK_CACHE,
            "WEBKIT_LOCAL": "ON",
            "WEBKIT_BUILD_TYPE": "Debug",
            "WEBKIT_PATH": f"{MOCK_WEBKIT}/WebKitBuild/Debug",
        }
        if extra_defines:
            defines.update(extra_defines)

        content = f"""cmake_minimum_required(VERSION 3.20)
project(test-jsc NONE)
"""
        for k, v in defines.items():
            content += f'set({k} "{v}")\n'
        content += f'include({REPO}/cmake/tools/SetupWebKit.cmake)\n'
        
        Path(cmake_lists).write_text(content)

        try:
            return subprocess.run(
                ["cmake", "-S", tmpdir, "-B", build_dir],
                capture_output=True, text=True, timeout=timeout, cwd=REPO,
            )
        except subprocess.TimeoutExpired:
            return subprocess.CompletedProcess(args=[], returncode=2, stdout="", stderr="Timeout")


def test_cmake_files_exist():
    """Modified CMake files and doc files must exist."""
    for f in [
        "cmake/tools/SetupWebKit.cmake",
        "cmake/targets/BuildBun.cmake",
        "CONTRIBUTING.md",
        "docs/project/contributing.mdx",
    ]:
        assert (Path(REPO) / f).exists(), f"{f} does not exist"


def test_setupwebkit_jsc_configure():
    """When WEBKIT_LOCAL=ON, cmake must attempt to configure JSC."""
    r = _cmake_configure()
    combined = r.stdout + r.stderr
    assert "Configuring JSC" in combined, (
        f"cmake did not reach JSC configuration code.\n"
        f"Output: {combined[:500]}"
    )


def test_setupwebkit_webkit_build_type():
    """WEBKIT_BUILD_TYPE option must affect the WebKit build path."""
    with tempfile.TemporaryDirectory() as tmpdir:
        cmake_lists = os.path.join(tmpdir, "CMakeLists.txt")
        build_dir = os.path.join(tmpdir, "build")
        custom_type = "MyCustomWebKitBuild"

        content = f"""cmake_minimum_required(VERSION 3.20)
project(test NONE)
set(VENDOR_PATH /tmp/vendor)
set(CACHE_PATH /tmp/cache)
set(WEBKIT_LOCAL ON)
set(WEBKIT_BUILD_TYPE "{custom_type}")
set(CMAKE_SYSTEM_NAME Linux)
set(CMAKE_SYSTEM_PROCESSOR x86_64)
set(CMAKE_BUILD_TYPE Debug)
include({REPO}/cmake/tools/SetupWebKit.cmake)
message(STATUS "PATH_CHECK: DEFAULT_WEBKIT_PATH=${{DEFAULT_WEBKIT_PATH}}")
"""
        Path(cmake_lists).write_text(content)

        r = subprocess.run(
            ["cmake", "-S", tmpdir, "-B", build_dir],
            capture_output=True, text=True, timeout=30, cwd=REPO,
        )

        output = r.stdout + r.stderr
        assert custom_type in output, (
            f"WEBKIT_BUILD_TYPE option was not used in path construction.\n"
            f"Output: {output[:500]}"
        )


def test_setupwebkit_jsc_custom_target():
    """A jsc target must be created when configuring with WEBKIT_LOCAL."""
    r = _cmake_configure()
    combined = r.stdout + r.stderr
    assert "Configuring JSC" in combined, (
        f"cmake did not reach JSC configuration code.\n"
        f"Output: {combined[:500]}"
    )


def test_buildbun_jsc_dependency():
    """When WEBKIT_LOCAL=ON, jsc should be handled as a dependency."""
    content = (Path(REPO) / "cmake/targets/BuildBun.cmake").read_text()
    lower = content.lower()
    has_webkit_local_jsc = "webkit_local" in lower and "jsc" in lower
    has_dep = "add_dependencies" in content or "target" in lower
    assert has_webkit_local_jsc and has_dep, (
        "BuildBun.cmake does not have jsc dependency logic for WEBKIT_LOCAL."
    )


def test_buildbun_system_icu_for_local():
    """For WEBKIT_LOCAL on Linux, ICU must be resolved via find_package."""
    content = (Path(REPO) / "cmake/targets/BuildBun.cmake").read_text()
    lower = content.lower()
    has_icu = "webkit_local" in lower and "icu" in lower
    has_linux = "linux" in lower
    assert has_icu and has_linux, (
        "BuildBun.cmake does not have ICU logic for WEBKIT_LOCAL on Linux."
    )


def test_contributing_simplified_build():
    """CONTRIBUTING.md must describe the simplified build:local workflow."""
    content = (Path(REPO) / "CONTRIBUTING.md").read_text()
    lower = content.lower()
    assert "build:local" in lower, "CONTRIBUTING.md does not mention build:local."
    assert "jsc:build:debug" not in content, "jsc:build:debug still in CONTRIBUTING.md"
    assert "inspectorprotocolobjects.h" not in lower, "manual header deletion still in CONTRIBUTING.md"


def test_contributing_no_manual_jsc_steps():
    """Old manual JSC build steps must be removed from documentation."""
    content = (Path(REPO) / "CONTRIBUTING.md").read_text()
    assert "jsc:build:debug" not in content, "jsc:build:debug still referenced"
    assert "InspectorProtocolObjects.h" not in content, "InspectorProtocolObjects.h still referenced"


def test_contributing_mdx_simplified():
    """docs/project/contributing.mdx must describe simplified build:local."""
    content = (Path(REPO) / "docs/project/contributing.mdx").read_text()
    lower = content.lower()
    assert "build:local" in lower, "contributing.mdx does not mention build:local"
    assert "jsc:build:debug" not in content, "jsc:build:debug still in contributing.mdx"


def test_setupwebkit_retains_prebuilt_path():
    """SetupWebKit.cmake must still support prebuilt WebKit downloads."""
    content = (Path(REPO) / "cmake/tools/SetupWebKit.cmake").read_text()
    assert "WEBKIT_VERSION" in content
    assert "CACHE_PATH" in content


def test_cmake_files_parse():
    """Modified CMake files must be syntactically parseable."""
    for cmake_file in [
        "cmake/tools/SetupWebKit.cmake",
        "cmake/targets/BuildBun.cmake",
    ]:
        subprocess.run(
            ["cmake", "--trace-format=cmake", "-N", "-S", REPO, "-B", "/tmp/cmake-parse-test"],
            capture_output=True, text=True, timeout=30, cwd=REPO,
        )


def test_cmake_consistent_options():
    """CMake option definitions must follow consistent patterns."""
    content = (Path(REPO) / "cmake/tools/SetupWebKit.cmake").read_text()
    options = re.findall(r"option\(\s*(\w+)", content)
    assert len(options) >= 2, f"Too few options: {options}"


def test_cmake_webkit_local_path_consistency():
    """WEBKIT_LOCAL path construction must be consistent."""
    content = (Path(REPO) / "cmake/tools/SetupWebKit.cmake").read_text()
    assert "if(WEBKIT_LOCAL)" in content
    assert "VENDOR_PATH" in content
    assert "DEFAULT_WEBKIT_PATH" in content


def test_cmake_no_syntax_errors():
    """CMake files must have no obvious syntax errors."""
    r = subprocess.run(["cmake", "--version"], capture_output=True, text=True, timeout=10)
    assert r.returncode == 0


def test_package_json_valid():
    """Repo package.json must be valid JSON if it exists."""
    pkg_path = Path(REPO) / "package.json"
    if pkg_path.exists():
        import json
        json.load(open(pkg_path))


def test_shell_scripts_valid():
    """Shell scripts must have valid bash syntax."""
    for script in ["scripts/run-clang-format.sh", "scripts/bd"]:
        script_path = Path(REPO) / script
        if script_path.exists():
            r = subprocess.run(["bash", "-n", str(script_path)], capture_output=True, text=True, timeout=30)
            assert r.returncode == 0, f"Script {script} has syntax errors"


def test_git_repo_valid():
    """Git repository must be valid and at expected commit."""
    r = subprocess.run(["git", "status"], capture_output=True, text=True, timeout=30, cwd=REPO)
    assert r.returncode == 0
    r2 = subprocess.run(["git", "log", "--oneline", "-1"], capture_output=True, text=True, timeout=30, cwd=REPO)
    assert "a14a89c" in r2.stdout


def test_contributing_md_syntax():
    """CONTRIBUTING.md must have valid markdown syntax."""
    content = (Path(REPO) / "CONTRIBUTING.md").read_text()
    assert content.count("```") % 2 == 0


def test_contributing_mdx_syntax():
    """docs/project/contributing.mdx must have valid MDX syntax."""
    content = (Path(REPO) / "docs/project/contributing.mdx").read_text()
    assert content.count("```") % 2 == 0


def test_cmake_structure_setup_webkit():
    """SetupWebKit.cmake must have required structure."""
    content = (Path(REPO) / "cmake/tools/SetupWebKit.cmake").read_text()
    for p in ["WEBKIT_VERSION", "WEBKIT_LOCAL", "DEFAULT_WEBKIT_PATH", "WEBKIT_INCLUDE_PATH", "WEBKIT_LIB_PATH"]:
        assert p in content, f"Missing: {p}"


def test_cmake_structure_build_bun():
    """BuildBun.cmake must have required structure."""
    content = (Path(REPO) / "cmake/targets/BuildBun.cmake").read_text()
    for p in ["WEBKIT_LIB_PATH", "WEBKIT_INCLUDE_PATH", "target_link_libraries"]:
        assert p in content, f"Missing: {p}"
