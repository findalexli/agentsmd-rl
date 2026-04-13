"""
Task: bun-remove-sccache-use-ccache
Repo: oven-sh/bun @ 5715b54614cbdb885ab42584d401c300cdff9519
PR:   25682

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/bun"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


def test_cmake_uses_ccache_only():
    """CMakeLists.txt includes SetupCcache directly, no sccache fallback logic."""
    cmake_lists = Path(REPO) / "CMakeLists.txt"
    content = cmake_lists.read_text()

    assert "include(SetupCcache)" in content, \
        "CMakeLists.txt should directly include SetupCcache"
    assert "find_program(SCCACHE_PROGRAM" not in content, \
        "CMakeLists.txt should not have sccache detection"
    assert "SetupSccache" not in content, \
        "CMakeLists.txt should not reference SetupSccache"

    # SetupSccache.cmake must be deleted
    sccache_cmake = Path(REPO) / "cmake" / "tools" / "SetupSccache.cmake"
    assert not sccache_cmake.exists(), \
        "cmake/tools/SetupSccache.cmake should be deleted"


def test_ccache_not_required():
    """SetupCcache.cmake gracefully handles missing ccache (no REQUIRED flag, no CI guard)."""
    ccache_cmake = Path(REPO) / "cmake" / "tools" / "SetupCcache.cmake"
    content = ccache_cmake.read_text()

    # Must not have REQUIRED flag on find_command
    assert "REQUIRED" not in content or "find_command" not in content, \
        "SetupCcache.cmake should not require ccache to be present"

    # Must not have CI-specific guard that disables ccache in non-macOS CI
    assert "if (CI AND NOT APPLE)" not in content, \
        "SetupCcache.cmake should not have CI-specific ccache disable guard"


def test_bootstrap_uses_ccache():
    """bootstrap.sh uses install_ccache not install_sccache, no mozilla/sccache download."""
    bootstrap = Path(REPO) / "scripts" / "bootstrap.sh"
    content = bootstrap.read_text()

    # Must call install_ccache, not install_sccache
    assert "install_ccache" in content, \
        "bootstrap.sh should reference install_ccache"

    # Must not call install_sccache
    assert "install_sccache" not in content, \
        "bootstrap.sh should not reference install_sccache"

    # Must not download sccache binary from GitHub releases
    assert "mozilla/sccache" not in content, \
        "bootstrap.sh should not download sccache binary from GitHub"


def test_build_cache_removed():
    """scripts/build-cache/ directory removed; build.mjs uses ccache, not sccache."""
    build_cache = Path(REPO) / "scripts" / "build-cache"
    assert not build_cache.exists(), \
        "scripts/build-cache/ directory should be removed (was only for sccache S3)"

    # build.mjs should reference ccache, not sccache
    build_mjs = Path(REPO) / "scripts" / "build.mjs"
    content = build_mjs.read_text()
    assert "ccache" in content, \
        "build.mjs should reference ccache"
    assert "sccache" not in content, \
        "build.mjs should not reference sccache"


def test_docs_use_ccache():
    """CONTRIBUTING.md documents ccache (not sccache) for build caching."""
    contributing = Path(REPO) / "CONTRIBUTING.md"
    content = contributing.read_text()

    assert "ccache" in content.lower(), \
        "CONTRIBUTING.md should mention ccache"
    assert "Optional: Install `ccache`" in content, \
        "CONTRIBUTING.md should have ccache install section heading"

    # Should not mention sccache anywhere
    assert "sccache" not in content.lower(), \
        "CONTRIBUTING.md should not mention sccache"


def test_docs_contributing_mdx_ccache():
    """docs/project/contributing.mdx documents ccache (not sccache)."""
    contributing_mdx = Path(REPO) / "docs" / "project" / "contributing.mdx"
    content = contributing_mdx.read_text()

    assert "ccache" in content.lower(), \
        "contributing.mdx should mention ccache"
    assert "sccache" not in content.lower(), \
        "contributing.mdx should not mention sccache"


def test_building_windows_docs_ccache():
    """docs/project/building-windows.mdx references ccache (not sccache) for Windows."""
    windows_mdx = Path(REPO) / "docs" / "project" / "building-windows.mdx"
    content = windows_mdx.read_text()

    assert "ccache" in content, \
        "building-windows.mdx should reference ccache in scoop install command"
    assert "sccache" not in content.lower(), \
        "building-windows.mdx should not reference sccache"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — syntax validation
# ---------------------------------------------------------------------------


def test_cmake_syntax_valid():
    """CMakeLists.txt is non-empty and contains valid cmake directives."""
    cmake_lists = Path(REPO) / "CMakeLists.txt"
    content = cmake_lists.read_text()

    # Basic structural checks that would catch malformed CMakeLists.txt
    assert "cmake_minimum_required" in content, "CMakeLists.txt should have cmake_minimum_required"
    assert "include(" in content, "CMakeLists.txt should have include() directives"
    # Check that SetupCcache is included (the main change from the PR)
    assert "include(SetupCcache)" in content, "CMakeLists.txt should include SetupCcache"


def test_bootstrap_syntax_valid():
    """scripts/bootstrap.sh is syntactically valid bash."""
    result = subprocess.run(
        ["bash", "-n", "scripts/bootstrap.sh"],
        cwd=REPO, capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, f"bootstrap.sh has bash syntax errors: {result.stderr}"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI command validation
# ---------------------------------------------------------------------------


def test_bootstrap_sh_posix_syntax():
    """Repo's bootstrap.sh passes POSIX shell syntax check (pass_to_pass)."""
    result = subprocess.run(
        ["sh", "-n", "scripts/bootstrap.sh"],
        cwd=REPO, capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, f"bootstrap.sh has shell syntax errors: {result.stderr}"


def test_run_clang_format_sh_syntax():
    """Repo's run-clang-format.sh passes bash syntax check (pass_to_pass)."""
    result = subprocess.run(
        ["bash", "-n", "scripts/run-clang-format.sh"],
        cwd=REPO, capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, f"run-clang-format.sh has bash syntax errors: {result.stderr}"


def test_check_node_sh_syntax():
    """Repo's check-node.sh passes POSIX shell syntax check (pass_to_pass)."""
    result = subprocess.run(
        ["sh", "-n", "scripts/check-node.sh"],
        cwd=REPO, capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, f"check-node.sh has shell syntax errors: {result.stderr}"


def test_check_node_all_sh_syntax():
    """Repo's check-node-all.sh passes POSIX shell syntax check (pass_to_pass)."""
    result = subprocess.run(
        ["sh", "-n", "scripts/check-node-all.sh"],
        cwd=REPO, capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, f"check-node-all.sh has shell syntax errors: {result.stderr}"


def test_trace_sh_syntax():
    """Repo's trace.sh passes POSIX shell syntax check (pass_to_pass)."""
    result = subprocess.run(
        ["sh", "-n", "scripts/trace.sh"],
        cwd=REPO, capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, f"trace.sh has shell syntax errors: {result.stderr}"


def test_cmake_modules_syntax():
    """Repo's CMake modules can be parsed by cmake without syntax errors (pass_to_pass)."""
    # Test SetupCcache.cmake can be loaded in script mode
    # cmake -P will fail if there are syntax errors, even with undefined commands
    result = subprocess.run(
        ["cmake", "-P", "cmake/tools/SetupCcache.cmake"],
        cwd=REPO, capture_output=True, text=True, timeout=30,
    )
    # The script may fail due to undefined functions, but syntax errors are what we care about
    # A syntax error will contain "Parse error" in output
    assert "Parse error" not in result.stderr, f"SetupCcache.cmake has parse errors: {result.stderr}"
    assert "syntax error" not in result.stderr.lower(), f"SetupCcache.cmake has syntax errors: {result.stderr}"


def test_generate_perf_trace_events_sh_syntax():
    """Repo's generate-perf-trace-events.sh passes bash syntax check (pass_to_pass)."""
    result = subprocess.run(
        ["bash", "-n", "scripts/generate-perf-trace-events.sh"],
        cwd=REPO, capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, f"generate-perf-trace-events.sh has bash syntax errors: {result.stderr}"


def test_lldb_inline_sh_syntax():
    """Repo's lldb-inline.sh passes bash syntax check (pass_to_pass)."""
    result = subprocess.run(
        ["bash", "-n", "scripts/lldb-inline.sh"],
        cwd=REPO, capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, f"lldb-inline.sh has bash syntax errors: {result.stderr}"


def test_update_sqlite_amalgamation_sh_syntax():
    """Repo's update-sqlite-amalgamation.sh passes bash syntax check (pass_to_pass)."""
    result = subprocess.run(
        ["bash", "-n", "scripts/update-sqlite-amalgamation.sh"],
        cwd=REPO, capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, f"update-sqlite-amalgamation.sh has bash syntax errors: {result.stderr}"
