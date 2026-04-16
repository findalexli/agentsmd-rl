#!/usr/bin/env python3
"""
Test outputs for Kotlin SearchPathType fix.
Tests that SearchPathType arguments (classpath, klibLibraries, javaModulePath)
are resolved to absolute paths before being joined with path separator.
"""

import subprocess
import os
import re

REPO = "/workspace/kotlin"

def test_generator_has_absolute_path_fix():
    """
    Fail-to-pass: Generator code must map paths through absolutePathStringOrThrow.

    The fix adds .map { it.absolutePathStringOrThrow() } before .joinToString()
    for SearchPathType arguments in BtaImplGenerator.kt.
    """
    file_path = os.path.join(REPO, "compiler/build-tools/kotlin-build-tools-options-generator/src/org/jetbrains/kotlin/buildtools/options/generator/BtaImplGenerator.kt")

    with open(file_path, 'r') as f:
        lines = f.readlines()

    # Find the first SearchPathType section (around line 404 in the base commit)
    # and check that it contains the fix for converting TO SearchPathType
    found_first_searchpath = False
    in_searchpath_block = False
    searchpath_block_content = []

    for i, line in enumerate(lines):
        if "argument.valueType.origin is SearchPathType ->" in line:
            if not found_first_searchpath:
                found_first_searchpath = True
                in_searchpath_block = True
                searchpath_block_content.append(line)
            else:
                # Second SearchPathType - stop here
                break
        elif in_searchpath_block:
            searchpath_block_content.append(line)
            # Check if we've reached the end of the block (next case or closing brace)
            if "argument.valueType.origin is PathListType ->" in line:
                break

    # Check first SearchPathType block (the one that converts TO SearchPathType)
    block_content = ''.join(searchpath_block_content)
    assert "joinToString" in block_content, "Should have joinToString in first SearchPathType block"
    assert "absolutePathStringOrThrow" in block_content, \
        "First SearchPathType block should use absolutePathStringOrThrow"
    assert "map" in block_content, \
        "First SearchPathType block should use map before joinToString"


def test_compat_generated_has_absolute_path_fix():
    """
    Fail-to-pass: Compat generated code must resolve paths to absolute.

    JvmCompilerArgumentsImpl.kt in kotlin-build-tools-compat must map
    classpath, klibLibraries, and javaModulePath through absolutePathStringOrThrow.
    """
    file_path = os.path.join(REPO, "compiler/build-tools/kotlin-build-tools-compat/gen/org/jetbrains/kotlin/buildtools/internal/compat/arguments/JvmCompilerArgumentsImpl.kt")

    with open(file_path, 'r') as f:
        content = f.read()

    # Check for the fix pattern: .map { it.absolutePathStringOrThrow() } before .joinToString
    assert "absolutePathStringOrThrow" in content, \
        "Compat generated code should use absolutePathStringOrThrow"

    # Check specific arguments
    for arg_name in ["X_KLIB", "X_MODULE_PATH", "CLASSPATH"]:
        pattern = rf"get\({arg_name}\)\?\.map.*?absolutePathStringOrThrow.*?joinToString"
        assert re.search(pattern, content, re.DOTALL), \
            f"Compat code should resolve {arg_name} paths to absolute before joinToString"


def test_impl_generated_has_absolute_path_fix():
    """
    Fail-to-pass: Impl generated code must resolve paths to absolute.

    JvmCompilerArgumentsImpl.kt in kotlin-build-tools-impl must map
    classpath, klibLibraries, and javaModulePath through absolutePathStringOrThrow.
    """
    file_path = os.path.join(REPO, "compiler/build-tools/kotlin-build-tools-impl/gen/org/jetbrains/kotlin/buildtools/internal/arguments/JvmCompilerArgumentsImpl.kt")

    with open(file_path, 'r') as f:
        content = f.read()

    # Check for the fix pattern: .map { it.absolutePathStringOrThrow() } before .joinToString
    assert "absolutePathStringOrThrow" in content, \
        "Impl generated code should use absolutePathStringOrThrow"

    # Check specific arguments - there are two occurrences of each (for different compiler versions)
    for arg_name in ["X_KLIB", "X_MODULE_PATH", "CLASSPATH"]:
        pattern = rf"get\({arg_name}\)\?\.map.*?absolutePathStringOrThrow.*?joinToString"
        matches = re.findall(pattern, content, re.DOTALL)
        assert len(matches) >= 2, \
            f"Impl code should resolve {arg_name} paths to absolute in both compiler version sections"


def test_kotlin_syntax_valid_generator():
    """
    Pass-to-pass: Generator Kotlin file must have valid syntax.

    The BtaImplGenerator.kt file should compile without syntax errors.
    """
    file_path = os.path.join(REPO, "compiler/build-tools/kotlin-build-tools-options-generator/src/org/jetbrains/kotlin/buildtools/options/generator/BtaImplGenerator.kt")

    # Use kotlinc to check syntax only (no output, just parsing)
    result = subprocess.run(
        ["kotlinc", "-d", "/dev/null", "-no-stdlib", "-no-reflect", file_path],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO
    )

    # Syntax check should pass (may fail on resolution, but not syntax)
    # Allow for resolution errors, but not syntax errors
    if result.returncode != 0:
        # Filter out resolution errors, only fail on syntax errors
        stderr = result.stderr
        syntax_errors = [line for line in stderr.split('\n') if 'error:' in line.lower() and 'syntax' in line.lower()]
        assert len(syntax_errors) == 0, f"Syntax errors found: {syntax_errors}"


def test_kotlin_syntax_valid_compat():
    """
    Pass-to-pass: Compat generated Kotlin file must have valid syntax.

    JvmCompilerArgumentsImpl.kt in kotlin-build-tools-compat should compile.
    """
    file_path = os.path.join(REPO, "compiler/build-tools/kotlin-build-tools-compat/gen/org/jetbrains/kotlin/buildtools/internal/compat/arguments/JvmCompilerArgumentsImpl.kt")

    result = subprocess.run(
        ["kotlinc", "-d", "/dev/null", "-no-stdlib", "-no-reflect", file_path],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO
    )

    # Allow resolution errors but not syntax errors
    if result.returncode != 0:
        stderr = result.stderr
        syntax_errors = [line for line in stderr.split('\n') if 'error:' in line.lower() and 'syntax' in line.lower()]
        assert len(syntax_errors) == 0, f"Syntax errors found: {syntax_errors}"


def test_kotlin_syntax_valid_impl():
    """
    Pass-to-pass: Impl generated Kotlin file must have valid syntax.

    JvmCompilerArgumentsImpl.kt in kotlin-build-tools-impl should compile.
    """
    file_path = os.path.join(REPO, "compiler/build-tools/kotlin-build-tools-impl/gen/org/jetbrains/kotlin/buildtools/internal/arguments/JvmCompilerArgumentsImpl.kt")

    result = subprocess.run(
        ["kotlinc", "-d", "/dev/null", "-no-stdlib", "-no-reflect", file_path],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO
    )

    # Allow resolution errors but not syntax errors
    if result.returncode != 0:
        stderr = result.stderr
        syntax_errors = [line for line in stderr.split('\n') if 'error:' in line.lower() and 'syntax' in line.lower()]
        assert len(syntax_errors) == 0, f"Syntax errors found: {syntax_errors}"


def test_no_raw_joinToString_for_searchpaths():
    """
    Fail-to-pass: SearchPathType arguments must not use raw joinToString.

    After the fix, X_KLIB, X_MODULE_PATH, and CLASSPATH should not directly
    call joinToString without first mapping through absolutePathStringOrThrow.
    """
    files_to_check = [
        "compiler/build-tools/kotlin-build-tools-compat/gen/org/jetbrains/kotlin/buildtools/internal/compat/arguments/JvmCompilerArgumentsImpl.kt",
        "compiler/build-tools/kotlin-build-tools-impl/gen/org/jetbrains/kotlin/buildtools/internal/arguments/JvmCompilerArgumentsImpl.kt"
    ]

    for rel_path in files_to_check:
        file_path = os.path.join(REPO, rel_path)
        with open(file_path, 'r') as f:
            content = f.read()

        # Look for the pattern: get(X_KLIB)?.joinToString (without map)
        # This should NOT exist after the fix
        for arg in ["X_KLIB", "X_MODULE_PATH", "CLASSPATH"]:
            # Match get(ARG)?.joinToString without .map in between
            pattern = rf"get\({arg}\)\?\.joinToString"
            bad_matches = re.findall(pattern, content)

            # If we found raw joinToString, that's an error
            assert len(bad_matches) == 0, \
                f"{rel_path}: {arg} should not use raw joinToString without mapping to absolute paths first"


# =============================================================================
# Additional Pass-to-Pass Tests (using repo CI commands)
# =============================================================================

def test_repo_generator_has_searchpath_type():
    """
    Pass-to-pass: Generator source must contain SearchPathType handling.

    The BtaImplGenerator.kt file must contain SearchPathType pattern for
    handling classpath, klibLibraries, and javaModulePath arguments.
    """
    result = subprocess.run(
        ["grep", "-q", "SearchPathType",
         f"{REPO}/compiler/build-tools/kotlin-build-tools-options-generator/src/org/jetbrains/kotlin/buildtools/options/generator/BtaImplGenerator.kt"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO
    )
    assert result.returncode == 0, "Generator source must contain SearchPathType handling"


def test_repo_generator_has_pathlist_type():
    """
    Pass-to-pass: Generator source must contain PathListType handling.

    The BtaImplGenerator.kt file must contain PathListType pattern which
    already correctly uses absolutePathStringOrThrow.
    """
    result = subprocess.run(
        ["grep", "-q", "PathListType",
         f"{REPO}/compiler/build-tools/kotlin-build-tools-options-generator/src/org/jetbrains/kotlin/buildtools/options/generator/BtaImplGenerator.kt"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO
    )
    assert result.returncode == 0, "Generator source must contain PathListType handling"


def test_repo_compat_generated_exists():
    """
    Pass-to-pass: Compat generated JvmCompilerArgumentsImpl.kt must exist.

    The generated file for the compat module must exist.
    """
    result = subprocess.run(
        ["test", "-f",
         f"{REPO}/compiler/build-tools/kotlin-build-tools-compat/gen/org/jetbrains/kotlin/buildtools/internal/compat/arguments/JvmCompilerArgumentsImpl.kt"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO
    )
    assert result.returncode == 0, "Compat generated file must exist"


def test_repo_impl_generated_exists():
    """
    Pass-to-pass: Impl generated JvmCompilerArgumentsImpl.kt must exist.

    The generated file for the impl module must exist.
    """
    result = subprocess.run(
        ["test", "-f",
         f"{REPO}/compiler/build-tools/kotlin-build-tools-impl/gen/org/jetbrains/kotlin/buildtools/internal/arguments/JvmCompilerArgumentsImpl.kt"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO
    )
    assert result.returncode == 0, "Impl generated file must exist"


def test_repo_compat_has_x_klib():
    """
    Pass-to-pass: Compat generated code must contain X_KLIB handling.

    The compat JvmCompilerArgumentsImpl.kt must reference X_KLIB constant.
    """
    result = subprocess.run(
        ["grep", "-q", "X_KLIB",
         f"{REPO}/compiler/build-tools/kotlin-build-tools-compat/gen/org/jetbrains/kotlin/buildtools/internal/compat/arguments/JvmCompilerArgumentsImpl.kt"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO
    )
    assert result.returncode == 0, "Compat generated code must contain X_KLIB handling"


def test_repo_compat_has_classpath():
    """
    Pass-to-pass: Compat generated code must contain CLASSPATH handling.

    The compat JvmCompilerArgumentsImpl.kt must reference CLASSPATH constant.
    """
    result = subprocess.run(
        ["grep", "-q", "CLASSPATH",
         f"{REPO}/compiler/build-tools/kotlin-build-tools-compat/gen/org/jetbrains/kotlin/buildtools/internal/compat/arguments/JvmCompilerArgumentsImpl.kt"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO
    )
    assert result.returncode == 0, "Compat generated code must contain CLASSPATH handling"


def test_repo_compat_has_module_path():
    """
    Pass-to-pass: Compat generated code must contain X_MODULE_PATH handling.

    The compat JvmCompilerArgumentsImpl.kt must reference X_MODULE_PATH constant.
    """
    result = subprocess.run(
        ["grep", "-q", "X_MODULE_PATH",
         f"{REPO}/compiler/build-tools/kotlin-build-tools-compat/gen/org/jetbrains/kotlin/buildtools/internal/compat/arguments/JvmCompilerArgumentsImpl.kt"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO
    )
    assert result.returncode == 0, "Compat generated code must contain X_MODULE_PATH handling"


def test_repo_impl_has_x_klib():
    """
    Pass-to-pass: Impl generated code must contain X_KLIB handling.

    The impl JvmCompilerArgumentsImpl.kt must reference X_KLIB constant.
    """
    result = subprocess.run(
        ["grep", "-q", "X_KLIB",
         f"{REPO}/compiler/build-tools/kotlin-build-tools-impl/gen/org/jetbrains/kotlin/buildtools/internal/arguments/JvmCompilerArgumentsImpl.kt"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO
    )
    assert result.returncode == 0, "Impl generated code must contain X_KLIB handling"


def test_repo_impl_has_classpath():
    """
    Pass-to-pass: Impl generated code must contain CLASSPATH handling.

    The impl JvmCompilerArgumentsImpl.kt must reference CLASSPATH constant.
    """
    result = subprocess.run(
        ["grep", "-q", "CLASSPATH",
         f"{REPO}/compiler/build-tools/kotlin-build-tools-impl/gen/org/jetbrains/kotlin/buildtools/internal/arguments/JvmCompilerArgumentsImpl.kt"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO
    )
    assert result.returncode == 0, "Impl generated code must contain CLASSPATH handling"


def test_repo_impl_has_module_path():
    """
    Pass-to-pass: Impl generated code must contain X_MODULE_PATH handling.

    The impl JvmCompilerArgumentsImpl.kt must reference X_MODULE_PATH constant.
    """
    result = subprocess.run(
        ["grep", "-q", "X_MODULE_PATH",
         f"{REPO}/compiler/build-tools/kotlin-build-tools-impl/gen/org/jetbrains/kotlin/buildtools/internal/arguments/JvmCompilerArgumentsImpl.kt"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO
    )
    assert result.returncode == 0, "Impl generated code must contain X_MODULE_PATH handling"


def test_repo_generator_has_jointostring():
    """
    Pass-to-pass: Generator uses joinToString for SearchPathType.

    The BtaImplGenerator.kt uses joinToString for SearchPathType arguments.
    """
    result = subprocess.run(
        ["grep", "-q", "joinToString",
         f"{REPO}/compiler/build-tools/kotlin-build-tools-options-generator/src/org/jetbrains/kotlin/buildtools/options/generator/BtaImplGenerator.kt"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO
    )
    assert result.returncode == 0, "Generator must use joinToString for SearchPathType"


def test_repo_generator_has_kotlinpoet_imports():
    """
    Pass-to-pass: Generator imports KotlinPoet for code generation.

    The BtaImplGenerator.kt uses KotlinPoet library for code generation.
    """
    result = subprocess.run(
        ["grep", "-q", "com.squareup.kotlinpoet",
         f"{REPO}/compiler/build-tools/kotlin-build-tools-options-generator/src/org/jetbrains/kotlin/buildtools/options/generator/BtaImplGenerator.kt"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO
    )
    assert result.returncode == 0, "Generator must import KotlinPoet library"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
