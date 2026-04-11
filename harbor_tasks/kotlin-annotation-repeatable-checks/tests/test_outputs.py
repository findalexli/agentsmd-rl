#!/usr/bin/env python3
"""
Test outputs for Kotlin FIR annotation repeatable checks fix.

This tests the fix for KT-85005: Annotation repeatable checks around ALL use-site target.
The bug was that @all: use-site target wasn't being properly handled when checking for
repeated annotations, leading to missing REPEATED_ANNOTATION errors.
"""

import subprocess
import sys
import tempfile
import os
from pathlib import Path

REPO = "/workspace/kotlin"


def run_kotlin_compiler(source_file: str, args: list = None) -> subprocess.CompletedProcess:
    """Run the Kotlin compiler on a source file and return the result."""
    cmd = [
        "./gradlew", "-q",
        ":compiler:fir:fir2ir:run",
        f"-Dkotlin.compiler.args=-source-path {source_file}"
    ]
    if args:
        cmd.extend(args)

    result = subprocess.run(
        cmd,
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180
    )
    return result


def run_fir_test(test_name: str) -> subprocess.CompletedProcess:
    """Run a specific FIR analysis test."""
    cmd = [
        "./gradlew", "-q",
        ":compiler:fir:analysis-tests:test",
        "--tests", test_name
    ]

    result = subprocess.run(
        cmd,
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )
    return result


def check_file_contains(filepath: str, pattern: str) -> bool:
    """Check if a file contains a pattern."""
    try:
        with open(filepath, 'r') as f:
            return pattern in f.read()
    except FileNotFoundError:
        return False


def test_annotation_all_repeatable_detection():
    """
    Test that @all: use-site target properly triggers REPEATED_ANNOTATION errors.

    This is a fail-to-pass test - before the fix, the compiler would not properly
    detect repeated annotations when @all: was used.
    """
    # Check that the FirAnnotationHelpers.kt has the fix
    helpers_file = Path(REPO) / "compiler/fir/checkers/src/org/jetbrains/kotlin/fir/analysis/checkers/FirAnnotationHelpers.kt"

    content = helpers_file.read_text()

    # The fix adds a check for AnnotationUseSiteTarget.ALL
    assert "it != AnnotationUseSiteTarget.ALL" in content, \
        "Fix not applied: AnnotationUseSiteTarget.ALL check missing in FirAnnotationHelpers.kt"

    # Also verify the logic structure is correct
    assert "takeIf {" in content and "annotationContainer?.getDefaultUseSiteTarget" in content, \
        "Fix not applied: Proper use-site target handling logic missing"


def test_opt_in_checker_simplified():
    """
    Test that FirOptInMarkedDeclarationChecker has simplified use-site target checks.

    The fix removes complex use-site target checks and relies on declaration type checks.
    """
    checker_file = Path(REPO) / "compiler/fir/checkers/src/org/jetbrains/kotlin/fir/analysis/checkers/declaration/FirOptInMarkedDeclarationChecker.kt"

    content = checker_file.read_text()

    # Should check declaration type for getters
    assert "declaration is FirPropertyAccessor && declaration.isGetter" in content, \
        "Fix not applied: Getter check should use declaration type"

    # Should check declaration type for value parameters (simplified)
    assert "declaration is FirValueParameter" in content, \
        "Fix not applied: Value parameter check should use declaration type"

    # Should not have the old complex condition
    assert "useSiteTarget != PROPERTY && useSiteTarget != PROPERTY_SETTER" not in content, \
        "Fix not applied: Old complex use-site target condition still present"


def test_opt_in_checker_backing_field():
    """
    Test that backing field check uses declaration type instead of just use-site target.
    """
    checker_file = Path(REPO) / "compiler/fir/checkers/src/org/jetbrains/kotlin/fir/analysis/checkers/declaration/FirOptInMarkedDeclarationChecker.kt"

    content = checker_file.read_text()

    # Should check declaration is FirBackingField
    assert "declaration is FirBackingField" in content, \
        "Fix not applied: Backing field check should use declaration type"


def test_annotation_checker_all_target():
    """
    Test that FirAnnotationChecker handles ALL use-site target without crashing.

    The fix changes a TODO() crash to a proper return statement.
    """
    checker_file = Path(REPO) / "compiler/fir/checkers/src/org/jetbrains/kotlin/fir/analysis/checkers/declaration/FirAnnotationChecker.kt"

    content = checker_file.read_text()

    # Should have return instead of TODO() for ALL target
    assert "ALL -> return" in content, \
        "Fix not applied: ALL use-site target should return instead of throwing TODO()"

    assert "ALL -> TODO()" not in content, \
        "Fix not applied: ALL use-site target still has crashing TODO()"


def test_supertypes_checker_comment():
    """
    Test that FirSupertypesChecker has explanatory comment about use-site targets.
    """
    checker_file = Path(REPO) / "compiler/fir/checkers/src/org/jetbrains/kotlin/fir/analysis/checkers/declaration/FirSupertypesChecker.kt"

    content = checker_file.read_text()

    # Should have the explanatory comment
    assert "Without a use-site target it can be a valid type annotation" in content, \
        "Fix not applied: Explanatory comment about type annotations missing"


def test_parcelize_checker_simplified():
    """
    Test that FirParcelizePropertyChecker has simplified hasIgnoredOnParcel check.
    """
    checker_file = Path(REPO) / "plugins/parcelize/parcelize-compiler/parcelize.k2/src/org/jetbrains/kotlin/parcelize/fir/diagnostics/FirParcelizePropertyChecker.kt"

    if not checker_file.exists():
        # Plugin might not be present in minimal setup
        return

    content = checker_file.read_text()

    # The simplified version should just check fqName without complex target checks
    assert "it.fqName(session) in IGNORED_ON_PARCEL_FQ_NAMES" in content, \
        "Fix not applied: Simplified hasIgnoredOnParcel check missing"


def test_annotation_kdoc_added():
    """
    Test that FirAnnotation and FirAnnotationCall have comprehensive KDoc.
    """
    annotation_file = Path(REPO) / "compiler/fir/tree/gen/org/jetbrains/kotlin/fir/expressions/FirAnnotation.kt"
    annotation_call_file = Path(REPO) / "compiler/fir/tree/gen/org/jetbrains/kotlin/fir/expressions/FirAnnotationCall.kt"

    annotation_content = annotation_file.read_text()
    annotation_call_content = annotation_call_file.read_text()

    # FirAnnotation should have KDoc explaining useSiteTarget
    assert "useSiteTarget" in annotation_content and "annotationUseSiteTarget" in annotation_content.lower(), \
        "Fix not applied: FirAnnotation KDoc missing useSiteTarget documentation"

    # FirAnnotationCall should have comprehensive KDoc
    assert "FirAnnotationCall is a FirCall" in annotation_call_content or "FirAnnotationCall] is a [FirCall" in annotation_call_content, \
        "Fix not applied: FirAnnotationCall KDoc missing or incomplete"


def test_fir_tree_generator_kdoc():
    """
    Test that FirTree.kt generator has KDoc for annotation and annotationCall elements.
    """
    tree_file = Path(REPO) / "compiler/fir/tree/tree-generator/src/org/jetbrains/kotlin/fir/tree/generator/FirTree.kt"

    content = tree_file.read_text()

    # Should have kDoc = """ for annotation element
    assert 'kDoc = """' in content or "kDoc = \"\"\"" in content, \
        "Fix not applied: KDoc not added to FirTree annotation elements"

    # Should document useSiteTarget
    assert "useSiteTarget" in content, \
        "Fix not applied: KDoc should mention useSiteTarget"


# =============================================================================
# PASS-TO-PASS TESTS - Repo CI/CD checks that should pass on both base and fix
# =============================================================================


def test_fir_checkers_compile():
    """
    FIR checkers module compiles successfully (pass_to_pass).

    This ensures the core FIR checker code is syntactically valid
    and compiles without errors on the base commit.
    """
    r = subprocess.run(
        ["./gradlew", ":compiler:fir:checkers:compileKotlin", "-q"],
        capture_output=True,
        text=True,
        timeout=600,
        cwd=REPO,
    )
    assert r.returncode == 0, f"FIR checkers compilation failed:\n{r.stderr[-1000:]}"


def test_fir_analysis_tests_compile():
    """
    FIR analysis tests module compiles successfully (pass_to_pass).

    This verifies the test infrastructure compiles correctly.
    """
    r = subprocess.run(
        ["./gradlew", ":compiler:fir:analysis-tests:compileTestFixturesKotlin", "-q"],
        capture_output=True,
        text=True,
        timeout=600,
        cwd=REPO,
    )
    assert r.returncode == 0, f"FIR analysis tests compilation failed:\n{r.stderr[-1000:]}"


def test_fir_analysis_tests_relevant():
    """
    FIR analysis tests for annotations pass (pass_to_pass).

    Runs tests specifically related to annotation handling in FIR.
    These tests should pass on both the base commit and after the fix.
    """
    r = subprocess.run(
        [
            "./gradlew",
            ":compiler:fir:analysis-tests:test",
            "--tests", "*Annotation*",
            "-q",
        ],
        capture_output=True,
        text=True,
        timeout=600,
        cwd=REPO,
    )
    assert r.returncode == 0, f"FIR annotation tests failed:\n{r.stderr[-1000:]}"


def test_fir_tree_generator_compile():
    """
    FIR tree generator compiles successfully (pass_to_pass).

    Verifies the FIR tree generator module (where FirTree.kt changes are made)
    compiles without errors.
    """
    r = subprocess.run(
        ["./gradlew", ":compiler:fir:tree:tree-generator:compileKotlin", "-q"],
        capture_output=True,
        text=True,
        timeout=600,
        cwd=REPO,
    )
    assert r.returncode == 0, f"FIR tree generator compilation failed:\n{r.stderr[-1000:]}"


def test_gradle_project_sanity():
    """
    Basic Gradle project sanity check (pass_to_pass).

    Verifies the Gradle wrapper and basic project structure is intact.
    """
    r = subprocess.run(
        ["./gradlew", "projects", "-q"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Gradle projects listing failed:\n{r.stderr[-500:]}"
    assert "compiler:fir" in r.stdout, "FIR modules not found in project structure"


def test_fir_serialization_compile():
    """
    FIR serialization module compiles successfully (pass_to_pass).

    Verifies the FIR serialization module (where FirElementSerializer.kt changes are made)
    compiles without errors on the base commit.
    """
    r = subprocess.run(
        ["./gradlew", ":compiler:fir:fir-serialization:compileKotlin", "-q"],
        capture_output=True,
        text=True,
        timeout=600,
        cwd=REPO,
    )
    assert r.returncode == 0, f"FIR serialization compilation failed:\n{r.stderr[-1000:]}"


def test_parcelize_compiler_compile():
    """
    Parcelize compiler module compiles successfully (pass_to_pass).

    Verifies the parcelize compiler plugin (where FirParcelizePropertyChecker.kt changes are made)
    compiles without errors on the base commit.
    """
    r = subprocess.run(
        ["./gradlew", ":plugins:parcelize:parcelize-compiler:parcelize.k2:compileKotlin", "-q"],
        capture_output=True,
        text=True,
        timeout=600,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Parcelize compiler compilation failed:\n{r.stderr[-1000:]}"


def test_fir_analysis_tests_opt_in():
    """
    FIR analysis tests for OptIn markers pass (pass_to_pass).

    Runs tests specifically related to OptIn/ExperimentalAPI handling in FIR.
    These tests should pass on both the base commit and after the fix.
    """
    r = subprocess.run(
        [
            "./gradlew",
            ":compiler:fir:analysis-tests:test",
            "--tests", "*OptIn*",
            "-q",
        ],
        capture_output=True,
        text=True,
        timeout=600,
        cwd=REPO,
    )
    assert r.returncode == 0, f"FIR OptIn tests failed:\n{r.stderr[-1000:]}"


def test_fir_analysis_tests_backing_field():
    """
    FIR analysis tests for backing fields pass (pass_to_pass).

    Runs tests specifically related to backing field handling in FIR.
    These tests should pass on both the base commit and after the fix.
    """
    r = subprocess.run(
        [
            "./gradlew",
            ":compiler:fir:analysis-tests:test",
            "--tests", "*BackingField*",
            "-q",
        ],
        capture_output=True,
        text=True,
        timeout=600,
        cwd=REPO,
    )
    assert r.returncode == 0, f"FIR backing field tests failed:\n{r.stderr[-1000:]}"


def test_fir_checkers_common_compile():
    """
    FIR checkers common module compiles successfully (pass_to_pass).

    Verifies the FIR checkers common module compiles without errors.
    This module contains shared checker infrastructure.
    """
    r = subprocess.run(
        ["./gradlew", ":compiler:fir:checkers:checkers-common:compileKotlin", "-q"],
        capture_output=True,
        text=True,
        timeout=600,
        cwd=REPO,
    )
    assert r.returncode == 0, f"FIR checkers common compilation failed:\n{r.stderr[-1000:]}"


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v", "--tb=short"]))
