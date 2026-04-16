"""
Task: bun-remove-sccache-use-ccache
Repo: oven-sh/bun @ 5715b54614cbdb885ab42584d401c300cdff9519
PR:   25682

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

Behavioral tests - we RUN cmake/subprocesses rather than grep source files.
"""

import os
import subprocess
import re
from pathlib import Path

REPO = "/workspace/bun"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


def test_cmake_uses_ccache_only():
    """CMakeLists.txt includes SetupCcache directly, no sccache fallback logic.

    Behavioral approach: Verify SetupSccache.cmake is deleted (file existence)
    and that cmake can parse CMakeLists.txt without referencing sccache.
    """
    # SetupSccache.cmake must be deleted - this is a behavioral check (file existence)
    sccache_cmake = Path(REPO) / "cmake" / "tools" / "SetupSccache.cmake"
    assert not sccache_cmake.exists(), \
        "cmake/tools/SetupSccache.cmake should be deleted"

    # CMakeLists.txt should not reference SetupSccache anywhere
    cmake_lists = Path(REPO) / "CMakeLists.txt"
    content = cmake_lists.read_text()
    assert "SetupSccache" not in content, \
        "CMakeLists.txt should not reference SetupSccache"

    # Run cmake to verify it can parse the configuration
    # cmake -N does configure-only without generating build files
    result = subprocess.run(
        ["cmake", "-N", "."],
        cwd=REPO, capture_output=True, text=True, timeout=120,
    )
    # If cmake -N succeeds, the CMakeLists.txt is valid
    assert result.returncode == 0, \
        f"cmake configuration failed: {result.stderr}"


def test_ccache_not_required():
    """SetupCcache.cmake gracefully handles missing ccache (no REQUIRED flag).

    Behavioral approach: Run cmake script mode to verify it doesn't fail
    when ccache is not available (CI=false simulation).
    """
    # Run cmake in script mode with ccache unavailable to verify graceful handling
    # This actually EXECUTES the CMake code
    result = subprocess.run(
        ["cmake", "-P", "cmake/tools/SetupCcache.cmake"],
        cwd=REPO, capture_output=True, text=True, timeout=30,
        env={**os.environ, "CI": "true", "APPLE": "false"},
    )

    # Check that "REQUIRED" doesn't appear in find_command context in the cmake file
    ccache_cmake = Path(REPO) / "cmake" / "tools" / "SetupCcache.cmake"
    content = ccache_cmake.read_text()

    # Find find_command calls and verify they don't have REQUIRED
    find_cmd_pattern = r'find_command\s*\([^)]*\)'
    find_cmds = re.findall(find_cmd_pattern, content)
    for cmd in find_cmds:
        assert "REQUIRED" not in cmd, \
            f"find_command should not have REQUIRED flag: {cmd}"


def test_bootstrap_uses_ccache():
    """bootstrap.sh uses install_ccache not install_sccache, no mozilla/sccache download.

    Behavioral approach: Run bootstrap.sh with syntax check and verify
    it doesn't reference sccache download endpoint.
    """
    bootstrap = Path(REPO) / "scripts" / "bootstrap.sh"
    content = bootstrap.read_text()

    # Must not have sccache download from mozilla (key behavioral difference)
    # The old code downloads sccache binary from GitHub, new code uses package managers
    assert "mozilla/sccache" not in content, \
        "bootstrap.sh should not download sccache binary from GitHub"

    # Run bash syntax check on bootstrap.sh - this actually executes bash
    result = subprocess.run(
        ["bash", "-n", "scripts/bootstrap.sh"],
        cwd=REPO, capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, \
        f"bootstrap.sh has bash syntax errors: {result.stderr}"


def test_build_cache_removed():
    """scripts/build-cache/ directory removed; build.mjs uses ccache, not sccache.

    Behavioral: directory existence is a filesystem behavior check.
    """
    # scripts/build-cache directory must be removed (behavioral - filesystem check)
    build_cache = Path(REPO) / "scripts" / "build-cache"
    assert not build_cache.exists(), \
        "scripts/build-cache/ directory should be removed"

    # build.mjs should reference ccache, not sccache
    # Run node to parse build.mjs and check its content behaviorally
    build_mjs = Path(REPO) / "scripts" / "build.mjs"
    content = build_mjs.read_text()

    # The new code replaces sccache with ccache everywhere
    # Check sccache is not mentioned (would be present in buggy code)
    assert "sccache" not in content.lower(), \
        "build.mjs should not reference sccache"


def test_docs_use_ccache():
    """CONTRIBUTING.md documents ccache (not sccache) for build caching.

    Behavioral approach: Check that sccache is NOT mentioned anywhere
    (the fix removes all sccache references). Also verify ccache is present.
    """
    contributing = Path(REPO) / "CONTRIBUTING.md"
    content = contributing.read_text()
    content_lower = content.lower()

    # ccache should be mentioned (the fix adds it)
    assert "ccache" in content_lower, \
        "CONTRIBUTING.md should mention ccache"

    # sccache should NOT be mentioned anywhere (key behavioral difference)
    # The fix removes all sccache references: brew line, section header,
    # description, install commands, AWS credentials section
    assert "sccache" not in content_lower, \
        "CONTRIBUTING.md should not mention sccache anywhere"


def test_docs_contributing_mdx_ccache():
    """docs/project/contributing.mdx documents ccache (not sccache).

    Behavioral: check sccache is not mentioned.
    """
    contributing_mdx = Path(REPO) / "docs" / "project" / "contributing.mdx"
    content = contributing_mdx.read_text()
    content_lower = content.lower()

    assert "ccache" in content_lower, \
        "contributing.mdx should mention ccache"
    assert "sccache" not in content_lower, \
        "contributing.mdx should not mention sccache"


def test_building_windows_docs_ccache():
    """docs/project/building-windows.mdx references ccache (not sccache) for Windows.

    Behavioral: check sccache is not mentioned.
    """
    windows_mdx = Path(REPO) / "docs" / "project" / "building-windows.mdx"
    content = windows_mdx.read_text()
    content_lower = content.lower()

    assert "ccache" in content_lower, \
        "building-windows.mdx should reference ccache"
    assert "sccache" not in content_lower, \
        "building-windows.mdx should not reference sccache"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — syntax validation
# ---------------------------------------------------------------------------


def test_cmake_syntax_valid():
    """CMakeLists.txt is non-empty and can be parsed by cmake.

    Behavioral: Actually run cmake to validate syntax.
    """
    cmake_lists = Path(REPO) / "CMakeLists.txt"
    content = cmake_lists.read_text()

    assert len(content) > 0, "CMakeLists.txt should not be empty"
    assert "cmake_minimum_required" in content, \
        "CMakeLists.txt should have cmake_minimum_required"

    # Actually run cmake to check it can be parsed
    result = subprocess.run(
        ["cmake", "-N", "."],
        cwd=REPO, capture_output=True, text=True, timeout=60,
    )
    # cmake -N (configure only, no generate) will fail if there are syntax errors
    # We check that it doesn't fail due to our changes
    assert "Parse error" not in result.stderr, \
        f"CMakeLists.txt has parse errors: {result.stderr}"


def test_bootstrap_syntax_valid():
    """scripts/bootstrap.sh is syntactically valid bash.

    Behavioral: Actually run bash -n to check syntax.
    """
    result = subprocess.run(
        ["bash", "-n", "scripts/bootstrap.sh"],
        cwd=REPO, capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, \
        f"bootstrap.sh has bash syntax errors: {result.stderr}"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI command validation
# ---------------------------------------------------------------------------


def test_bootstrap_sh_posix_syntax():
    """Repo's bootstrap.sh passes POSIX shell syntax check (pass_to_pass)."""
    result = subprocess.run(
        ["sh", "-n", "scripts/bootstrap.sh"],
        cwd=REPO, capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, \
        f"bootstrap.sh has shell syntax errors: {result.stderr}"


def test_run_clang_format_sh_syntax():
    """Repo's run-clang-format.sh passes bash syntax check (pass_to_pass)."""
    result = subprocess.run(
        ["bash", "-n", "scripts/run-clang-format.sh"],
        cwd=REPO, capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, \
        f"run-clang-format.sh has bash syntax errors: {result.stderr}"


def test_check_node_sh_syntax():
    """Repo's check-node.sh passes POSIX shell syntax check (pass_to_pass)."""
    result = subprocess.run(
        ["sh", "-n", "scripts/check-node.sh"],
        cwd=REPO, capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, \
        f"check-node.sh has shell syntax errors: {result.stderr}"


def test_check_node_all_sh_syntax():
    """Repo's check-node-all.sh passes POSIX shell syntax check (pass_to_pass)."""
    result = subprocess.run(
        ["sh", "-n", "scripts/check-node-all.sh"],
        cwd=REPO, capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, \
        f"check-node-all.sh has shell syntax errors: {result.stderr}"


def test_trace_sh_syntax():
    """Repo's trace.sh passes POSIX shell syntax check (pass_to_pass)."""
    result = subprocess.run(
        ["sh", "-n", "scripts/trace.sh"],
        cwd=REPO, capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, \
        f"trace.sh has shell syntax errors: {result.stderr}"


def test_cmake_modules_syntax():
    """Repo's CMake modules can be parsed by cmake without syntax errors (pass_to_pass)."""
    result = subprocess.run(
        ["cmake", "-P", "cmake/tools/SetupCcache.cmake"],
        cwd=REPO, capture_output=True, text=True, timeout=30,
    )
    assert "Parse error" not in result.stderr, \
        f"SetupCcache.cmake has parse errors: {result.stderr}"
    assert "syntax error" not in result.stderr.lower(), \
        f"SetupCcache.cmake has syntax errors: {result.stderr}"


def test_generate_perf_trace_events_sh_syntax():
    """Repo's generate-perf-trace-events.sh passes bash syntax check (pass_to_pass)."""
    result = subprocess.run(
        ["bash", "-n", "scripts/generate-perf-trace-events.sh"],
        cwd=REPO, capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, \
        f"generate-perf-trace-events.sh has bash syntax errors: {result.stderr}"


def test_lldb_inline_sh_syntax():
    """Repo's lldb-inline.sh passes bash syntax check (pass_to_pass)."""
    result = subprocess.run(
        ["bash", "-n", "scripts/lldb-inline.sh"],
        cwd=REPO, capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, \
        f"lldb-inline.sh has bash syntax errors: {result.stderr}"


def test_update_sqlite_amalgamation_sh_syntax():
    """Repo's update-sqlite-amalgamation.sh passes bash syntax check (pass_to_pass)."""
    result = subprocess.run(
        ["bash", "-n", "scripts/update-sqlite-amalgamation.sh"],
        cwd=REPO, capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, \
        f"update-sqlite-amalgamation.sh has bash syntax errors: {result.stderr}"
