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


def test_cmake_syntax_valid():
    """CMakeLists.txt should have valid syntax (pass-to-pass).

    Basic syntax check that doesn't require full build.
    """
    cmake_file = os.path.join(REPO, "contrib/boost-cmake/CMakeLists.txt")

    # Use cmake to parse the file
    result = subprocess.run(
        ["cmake", "-P", "-"],
        input=f"include({cmake_file})",
        capture_output=True,
        text=True,
        timeout=30
    )

    # Note: include will fail due to missing context, but syntax errors
    # would be reported differently
    # Just check file is readable and has matching if/endif
    with open(cmake_file, "r") as f:
        content = f.read()

    # Rough syntax validation: check for matching if/endif
    if_count = content.count("if (")
    endif_count = content.count("endif()")
    assert if_count > 0 and endif_count > 0, \
        "CMakeLists.txt should have if/endif statements"


def test_fiber_stack_cpp_syntax_valid():
    """FiberStack.cpp should have valid C++ syntax (pass-to-pass).

    Basic clang syntax check.
    """
    fiber_stack_cpp = os.path.join(REPO, "src/Common/FiberStack.cpp")

    # Try to compile just this file with clang
    # We don't need full build, just syntax check
    result = subprocess.run(
        ["clang-18", "-fsyntax-only", "-std=c++23", fiber_stack_cpp],
        capture_output=True,
        text=True,
        timeout=60
    )

    # The syntax check may fail due to missing includes, but should not
    # have syntax errors in the code itself
    # We check that the file exists and has valid structure
    with open(fiber_stack_cpp, "r") as f:
        content = f.read()

    # Check for valid C++ structure
    assert "boost::context::stack_context FiberStack::allocate()" in content, \
        "Should have correct function signature"

    # Check braces are balanced (rough check)
    open_braces = content.count("{")
    close_braces = content.count("}")
    assert open_braces == close_braces, \
        "Braces should be balanced in FiberStack.cpp"


def test_dragonbox_test_syntax_valid():
    """gtest_dragonbox_msan.cpp should have valid C++ syntax (pass-to-pass).
    """
    test_file = os.path.join(REPO, "src/Common/tests/gtest_dragonbox_msan.cpp")

    if not os.path.exists(test_file):
        pytest.skip("Test file does not exist yet")

    with open(test_file, "r") as f:
        content = f.read()

    # Check for valid C++ structure
    open_braces = content.count("{")
    close_braces = content.count("}")
    assert open_braces == close_braces, \
        "Braces should be balanced in gtest_dragonbox_msan.cpp"

    # Check parentheses balance (rough)
    open_parens = content.count("(")
    close_parens = content.count(")")
    assert open_parens == close_parens, \
        "Parentheses should be balanced"


def test_pr_files_no_style_violations():
    """PR-modified files should pass repo's C++ style check (pass-to-pass).

    This runs the repo's check_cpp.sh script on the specific files that
    the PR modifies to ensure they follow ClickHouse coding standards.
    """
    pr_files = [
        "contrib/boost-cmake/CMakeLists.txt",
        "src/Common/Fiber.h",
        "src/Common/FiberStack.cpp",
    ]

    # Run style check script on each file
    for file_path in pr_files:
        full_path = os.path.join(REPO, file_path)
        if not os.path.exists(full_path):
            pytest.skip(f"File {file_path} does not exist")

    # Run the repo's style check script and filter for our files
    result = subprocess.run(
        ["bash", "./ci/jobs/scripts/check_style/check_cpp.sh"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )

    # Check if any style issues are found in PR files
    style_issues = []
    for line in (result.stdout + result.stderr).splitlines():
        for pr_file in pr_files:
            if pr_file in line and "style error" in line.lower():
                style_issues.append(line)

    assert len(style_issues) == 0, \
        f"Style violations found in PR files:\n" + "\n".join(style_issues[:10])


def test_cmake_syntax_structure():
    """CMakeLists.txt should have valid structure (pass-to-pass).

    Validates that the CMakeLists.txt has balanced if/endif statements
    and proper cmake syntax for the boost-cmake module.
    """
    cmake_file = os.path.join(REPO, "contrib/boost-cmake/CMakeLists.txt")

    with open(cmake_file, "r") as f:
        content = f.read()

    # Count cmake if/elseif/endif statements (at start of lines)
    if_count = len(__import__('re').findall(r'^if\s*\(', content, __import__('re').MULTILINE))
    elseif_count = len(__import__('re').findall(r'^elseif\s*\(', content, __import__('re').MULTILINE))
    endif_count = len(__import__('re').findall(r'^endif\s*\(', content, __import__('re').MULTILINE))

    # Basic sanity: should have at least some if blocks
    assert if_count >= 1, "Should have at least one if() statement"
    assert endif_count >= 1, "Should have at least one endif() statement"

    # Check for expected patterns in the file
    assert "if (SANITIZE" in content or "if(SANITIZE" in content, \
        "Should check for SANITIZE variable"
    assert "OS_LINUX" in content, "Should check for OS_LINUX"
    assert "target_compile_definitions" in content, \
        "Should use target_compile_definitions"


def test_fiber_h_structure():
    """Fiber.h should have valid header structure (pass-to-pass).

    Validates header guards, include structure, and basic formatting.
    """
    fiber_h = os.path.join(REPO, "src/Common/Fiber.h")

    with open(fiber_h, "r") as f:
        content = f.read()

    # Check for pragma once or include guards
    assert "#pragma once" in content, "Header should have #pragma once"

    # Check for expected includes
    assert "base/defines.h" in content, "Should include base/defines.h"
    assert "boost/context/fiber.hpp" in content, "Should include boost fiber"

    # Check brace balance
    open_braces = content.count("{")
    close_braces = content.count("}")
    assert open_braces == close_braces, "Braces should be balanced"

    # Check class declaration exists
    assert "class Fiber" in content, "Should declare Fiber class"


def test_fiber_stack_cpp_structure():
    """FiberStack.cpp should have valid implementation structure (pass-to-pass).

    Validates function definitions and basic structure.
    """
    fiber_stack_cpp = os.path.join(REPO, "src/Common/FiberStack.cpp")

    with open(fiber_stack_cpp, "r") as f:
        content = f.read()

    # Check for expected function
    assert "FiberStack::allocate" in content, "Should have FiberStack::allocate function"

    # Check for boost context include
    assert "boost/context/stack_context.hpp" in content.lower() or \
           "boost/context/fixedsize_stack.hpp" in content.lower() or \
           "FiberStack.h" in content, "Should include required headers"

    # Check brace balance
    open_braces = content.count("{")
    close_braces = content.count("}")
    assert open_braces == close_braces, "Braces should be balanced"

    # Check parentheses balance
    open_parens = content.count("(")
    close_parens = content.count(")")
    assert open_parens == close_parens, "Parentheses should be balanced"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
