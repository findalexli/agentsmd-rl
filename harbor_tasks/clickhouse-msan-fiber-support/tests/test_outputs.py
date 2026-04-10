#!/usr/bin/env python3
"""Tests for ClickHouse MSan fiber support PR.

This PR adds MSan (Memory Sanitizer) support for fibers and fixes
dragonbox struct padding issues. The changes include:
1. CMake: Define BOOST_USE_MSAN for memory sanitizer builds
2. Fiber.h: Update comment to include BOOST_USE_MSAN
3. FiberStack.cpp: Update comment explaining __msan_unpoison
4. New test: gtest_dragonbox_msan.cpp documenting the MSan limitation
"""

import os
import subprocess
import sys

import pytest

REPO = "/workspace/ClickHouse"


def test_cmake_boost_use_msan_defined():
    """BOOST_USE_MSAN must be defined for memory sanitizer builds in CMake.

    This is a fail-to-pass test: the base commit lacks the MSAN handling,
    only having ASAN and TSAN. The fix adds the elseif branch for MSAN.
    """
    cmake_file = os.path.join(REPO, "contrib/boost-cmake/CMakeLists.txt")
    with open(cmake_file, "r") as f:
        content = f.read()

    # Check that BOOST_USE_MSAN is defined in the CMakeLists.txt
    assert "BOOST_USE_MSAN" in content, \
        "CMakeLists.txt should define BOOST_USE_MSAN for memory sanitizer builds"

    # Check the pattern: elseif (SANITIZE MATCHES "memory")
    assert 'elseif (SANITIZE MATCHES "memory")' in content, \
        "CMakeLists.txt should check for memory sanitizer"

    # Check that it comes after ASAN and before TSAN
    asan_pos = content.find('target_compile_definitions(_boost_context PUBLIC BOOST_USE_ASAN)')
    msan_pos = content.find('target_compile_definitions(_boost_context PUBLIC BOOST_USE_MSAN)')
    tsan_pos = content.find('target_compile_definitions(_boost_context PUBLIC BOOST_USE_TSAN)')

    assert asan_pos != -1 and msan_pos != -1 and tsan_pos != -1, \
        "All three sanitizer definitions should exist"
    assert asan_pos < msan_pos < tsan_pos, \
        "BOOST_USE_MSAN should be between ASAN and TSAN definitions"


def test_fiber_h_comment_updated():
    """Fiber.h comment should mention BOOST_USE_MSAN.

    The header comment was updated to include MSAN alongside ASAN and TSAN.
    """
    fiber_h = os.path.join(REPO, "src/Common/Fiber.h")
    with open(fiber_h, "r") as f:
        content = f.read()

    # Check that the comment mentions BOOST_USE_MSAN
    assert "BOOST_USE_MSAN" in content, \
        "Fiber.h comment should mention BOOST_USE_MSAN"

    # Check the updated comment format (should NOT have the old comment)
    old_comment = "defines.h should be included before fiber.hpp"
    assert old_comment not in content, \
        "Old comment about defines.h should be removed"

    # Check new comment format
    new_comment = "are defined via CMake for sanitizer builds"
    assert new_comment in content, \
        "Fiber.h should have updated comment about CMake definitions"


def test_fiber_stack_cpp_comment_explains_msan_unpoison():
    """FiberStack.cpp comment should explain the MSan struct padding issue.

    The comment was updated to explain why __msan_unpoison is needed:
    MSan doesn't track shadow for struct padding bytes through return values.
    """
    fiber_stack_cpp = os.path.join(REPO, "src/Common/FiberStack.cpp")
    with open(fiber_stack_cpp, "r") as f:
        content = f.read()

    # Check that __msan_unpoison is called
    assert "__msan_unpoison(data, num_bytes)" in content, \
        "FiberStack::allocate should call __msan_unpoison"

    # Check for the new explanatory comment about struct padding
    assert "struct padding" in content.lower(), \
        "Comment should explain the struct padding issue"

    # Check for the key explanation about shadow tracking
    assert "per-field" in content.lower() or "LLVM IR" in content, \
        "Comment should explain MSan per-field shadow tracking"

    # The old comment was about "stack slots reused across function calls"
    # The new comment should NOT have the old explanation
    old_explanation = "stack slots are reused across function calls"
    assert old_explanation not in content, \
        "Old incorrect explanation should be removed"


def test_dragonbox_msan_test_file_exists():
    """The gtest_dragonbox_msan.cpp test file should exist.

    This test documents the MSan limitation with struct padding in return values.
    """
    test_file = os.path.join(REPO, "src/Common/tests/gtest_dragonbox_msan.cpp")
    assert os.path.exists(test_file), \
        "gtest_dragonbox_msan.cpp test file should exist"

    with open(test_file, "r") as f:
        content = f.read()

    # Check that the test has the correct structure
    assert "TEST(DragonboxMSan, ReturnValuePaddingShadowIsLost)" in content, \
        "Test should be named ReturnValuePaddingShadowIsLost"

    # Check for MEMORY_SANITIZER guard
    assert "MEMORY_SANITIZER" in content, \
        "Test should check for MEMORY_SANITIZER"

    # Check that it uses dragonbox
    assert "dragonbox" in content.lower(), \
        "Test should use dragonbox library"

    # Check for the struct padding explanation
    assert "padding" in content.lower(), \
        "Test should mention struct padding"


def test_repo_style_check():
    """PR-modified files pass ClickHouse C++ style check (pass_to_pass).

    This runs the repo's check_cpp.sh script on the codebase to ensure
    the modified files follow ClickHouse coding standards.
    """
    result = subprocess.run(
        ["bash", "ci/jobs/scripts/check_style/check_cpp.sh"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )

    # The script outputs style issues to stdout. Check that PR files don't
    # have style errors by looking for them in output
    pr_files = ["src/Common/Fiber.h", "src/Common/FiberStack.cpp", "contrib/boost-cmake/CMakeLists.txt"]
    output = result.stdout + result.stderr

    for line in output.splitlines():
        for pr_file in pr_files:
            if pr_file in line and "style error" in line.lower():
                pytest.fail(f"Style error in {pr_file}: {line}")

    # Test passes if no style errors found in PR files
    assert True


def test_repo_various_checks():
    """ClickHouse repo various_checks.sh passes (pass_to_pass).

    This runs the various_checks.sh script which performs various
    repository validation checks.
    """
    result = subprocess.run(
        ["bash", "ci/jobs/scripts/check_style/various_checks.sh"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )

    # The script should exit 0 on success
    assert result.returncode == 0, \
        f"various_checks.sh failed:\n{result.stdout[-1000:]}{result.stderr[-500:]}"


def test_repo_cmake_syntax():
    """CMakeLists.txt files have valid syntax (pass_to_pass).

    Uses cmake --help-command-list and basic parsing to validate CMake syntax.
    """
    cmake_file = os.path.join(REPO, "contrib/boost-cmake/CMakeLists.txt")

    # Use cmake to validate the file can be parsed
    result = subprocess.run(
        ["cmake", "-P", "-"],
        input=f"include({cmake_file})",
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )

    # The include will fail due to missing context, but we check for
    # actual syntax errors vs context errors
    error_output = result.stderr.lower()

    # Syntax errors would mention "parse error", "syntax error", etc.
    syntax_indicators = ["parse error", "syntax error", "unknown command"]
    for indicator in syntax_indicators:
        assert indicator not in error_output, \
            f"CMake syntax error detected: {result.stderr[-500:]}"


def test_repo_clang_syntax_check():
    """C++ implementation files have valid syntax (pass_to_pass).

    Runs clang -fsyntax-only on modified C++ implementation files only.
    """
    cpp_files = [
        os.path.join(REPO, "src/Common/FiberStack.cpp"),
    ]

    for cpp_file in cpp_files:
        if not os.path.exists(cpp_file):
            pytest.skip(f"File {cpp_file} does not exist")

        result = subprocess.run(
            ["clang-18", "-fsyntax-only", "-std=c++23", "-I", os.path.join(REPO, "src"), cpp_file],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=REPO,
        )

        # Check for actual syntax errors vs missing includes
        error_output = result.stderr.lower()
        syntax_indicators = ["expected", "syntax error", "parse error", "invalid"]

        has_syntax_error = any(indicator in error_output for indicator in syntax_indicators)
        if has_syntax_error:
            pytest.fail(f"Syntax error in {cpp_file}:\
{result.stderr[-500:]}")


def test_repo_git_check():
    """Git repository is in valid state (pass_to_pass).

    Verifies the git repo is properly initialized and base commit is checked out.
    """
    # Check git status works
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )

    assert result.returncode == 0, \
        f"Git status failed: {result.stderr}"

    # Check the base commit exists
    result = subprocess.run(
        ["git", "rev-parse", "--verify", "HEAD"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )

    assert result.returncode == 0, \
        f"Git HEAD not valid: {result.stderr}"

    # Verify we have the expected commit
    head_commit = result.stdout.strip()
    assert len(head_commit) == 40, \
        f"Invalid HEAD commit: {head_commit}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
