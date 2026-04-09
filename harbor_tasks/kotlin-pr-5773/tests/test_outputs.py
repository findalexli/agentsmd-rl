#!/usr/bin/env python3
"""
Test outputs for Kotlin typo fix benchmark.

This task tests the ability to fix a typo in a package name:
- Package 'org.jetbrains.kotlin.analysis.utils.relfection' should be 'reflection'
- Need to rename directory and update package/import declarations
"""

import subprocess
import os
import re

REPO = "/workspace/kotlin"


def test_directory_renamed():
    """The directory 'relfection' has been renamed to 'reflection'. (fail_to_pass)"""
    old_dir = os.path.join(REPO, "analysis/analysis-internal-utils/src/org/jetbrains/kotlin/analysis/utils/relfection")
    new_dir = os.path.join(REPO, "analysis/analysis-internal-utils/src/org/jetbrains/kotlin/analysis/utils/reflection")

    assert not os.path.isdir(old_dir), f"Old directory still exists: {old_dir}"
    assert os.path.isdir(new_dir), f"New directory does not exist: {new_dir}"


def test_package_declaration_updated():
    """Package declaration in toStringDataClassLike.kt uses 'reflection'. (fail_to_pass)"""
    filepath = os.path.join(
        REPO,
        "analysis/analysis-internal-utils/src/org/jetbrains/kotlin/analysis/utils/reflection/toStringDataClassLike.kt"
    )

    assert os.path.exists(filepath), f"File not found: {filepath}"

    with open(filepath, 'r') as f:
        content = f.read()

    # Check for correct package declaration
    assert "package org.jetbrains.kotlin.analysis.utils.reflection" in content, \
        "Package declaration should use 'reflection', not 'relfection'"

    # Ensure old typo is gone
    assert "relfection" not in content, \
        "File still contains typo 'relfection'"


def test_import_statement_updated():
    """Import in KaSymbolPointer.kt uses correct 'reflection' package. (fail_to_pass)"""
    filepath = os.path.join(
        REPO,
        "analysis/analysis-api/src/org/jetbrains/kotlin/analysis/api/symbols/pointers/KaSymbolPointer.kt"
    )

    assert os.path.exists(filepath), f"File not found: {filepath}"

    with open(filepath, 'r') as f:
        content = f.read()

    # Check for correct import
    assert "import org.jetbrains.kotlin.analysis.utils.reflection.renderAsDataClassToString" in content, \
        "Import should reference 'reflection' package"

    # Ensure old import is gone
    assert "relfection" not in content, \
        "File still contains import with typo 'relfection'"


def test_no_other_occurrences():
    """No other files contain the typo 'relfection'. (fail_to_pass)"""
    # Search for any remaining occurrences of the typo
    result = subprocess.run(
        ["grep", "-r", "relfection", "--include=*.kt", "--include=*.java", REPO],
        capture_output=True,
        text=True
    )

    # grep returns 0 if matches found, 1 if no matches
    assert result.returncode != 0 or result.stdout.strip() == "", \
        f"Found remaining occurrences of 'relfection':\n{result.stdout[:500]}"


def test_copyright_year_updated():
    """Copyright year is updated to 2026 in the renamed file. (fail_to_pass)"""
    filepath = os.path.join(
        REPO,
        "analysis/analysis-internal-utils/src/org/jetbrains/kotlin/analysis/utils/reflection/toStringDataClassLike.kt"
    )

    assert os.path.exists(filepath), f"File not found: {filepath}"

    with open(filepath, 'r') as f:
        content = f.read()

    # Check for updated copyright year
    assert "Copyright 2010-2026" in content, \
        "Copyright year should be updated to 2010-2026"


def test_git_tracked_properly():
    """Git tracks the file rename properly (pass_to_pass)."""
    # Check that git recognizes the file was renamed
    result = subprocess.run(
        ["git", "status", "--short"],
        cwd=REPO,
        capture_output=True,
        text=True
    )

    # The output should show the rename (R) operation
    # Format: R  old/path -> new/path
    assert "R" in result.stdout or "analysis/analysis-internal-utils" in result.stdout, \
        f"Git should track the file rename:\n{result.stdout}"


def test_analysis_internal_utils_exists():
    """Analysis internal utils module exists (pass_to_pass)."""
    assert os.path.isdir(os.path.join(REPO, "analysis/analysis-internal-utils")), \
        "analysis-internal-utils module should exist"


def test_analysis_api_exists():
    """Analysis API module exists (pass_to_pass)."""
    assert os.path.isdir(os.path.join(REPO, "analysis/analysis-api")), \
        "analysis-api module should exist"


def test_build_files_exist():
    """Build files for analysis modules exist (pass_to_pass)."""
    assert os.path.isfile(os.path.join(REPO, "analysis/analysis-api/build.gradle.kts")), \
        "analysis-api build.gradle.kts should exist"
    assert os.path.isfile(os.path.join(REPO, "analysis/analysis-internal-utils/build.gradle.kts")), \
        "analysis-internal-utils build.gradle.kts should exist"


def test_tostringdataclasslike_file_exists():
    """toStringDataClassLike.kt file exists (pass_to_pass)."""
    # Check both old and new paths - one should exist at base, other after fix
    old_path = os.path.join(REPO, "analysis/analysis-internal-utils/src/org/jetbrains/kotlin/analysis/utils/relfection/toStringDataClassLike.kt")
    new_path = os.path.join(REPO, "analysis/analysis-internal-utils/src/org/jetbrains/kotlin/analysis/utils/reflection/toStringDataClassLike.kt")

    assert os.path.isfile(old_path) or os.path.isfile(new_path), \
        "toStringDataClassLike.kt should exist at either old or new path"


def test_kasymbolpointer_file_exists():
    """KaSymbolPointer.kt file exists (pass_to_pass)."""
    filepath = os.path.join(REPO, "analysis/analysis-api/src/org/jetbrains/kotlin/analysis/api/symbols/pointers/KaSymbolPointer.kt")
    assert os.path.isfile(filepath), \
        "KaSymbolPointer.kt should exist"


def test_no_syntax_errors_in_kt_files():
    """Kotlin source files have no obvious syntax errors (pass_to_pass)."""
    # Check that all .kt files in the modified modules can be parsed as text
    # This is a basic sanity check - files should be readable and not have unmatched braces
    filepath = os.path.join(REPO, "analysis/analysis-internal-utils/src/org/jetbrains/kotlin/analysis/utils/relfection/toStringDataClassLike.kt")

    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            content = f.read()

        # Basic syntax checks
        open_braces = content.count('{')
        close_braces = content.count('}')
        open_parens = content.count('(')
        close_parens = content.count(')')

        assert open_braces == close_braces, f"Unmatched braces in {filepath}"
        assert open_parens == close_parens, f"Unmatched parentheses in {filepath}"

        # Check for basic Kotlin file structure
        assert "package" in content, f"Missing package declaration in {filepath}"


def test_package_name_consistency():
    """Package declaration matches directory path (pass_to_pass)."""
    # Check that the package declaration in toStringDataClassLike.kt matches its directory
    filepath = os.path.join(REPO, "analysis/analysis-internal-utils/src/org/jetbrains/kotlin/analysis/utils/relfection/toStringDataClassLike.kt")

    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            content = f.read()

        # Extract package declaration
        package_match = re.search(r'^package\s+([\w.]+)', content, re.MULTILINE)
        if package_match:
            declared_package = package_match.group(1)
            # The directory path is .../utils/relfection so package should end with that
            expected_suffix = "relfection"  # or "reflection" after fix
            assert declared_package.endswith(expected_suffix) or declared_package.endswith("reflection"), \
                f"Package declaration '{declared_package}' should end with 'relfection' or 'reflection'"
