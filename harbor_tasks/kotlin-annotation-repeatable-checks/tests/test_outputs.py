#!/usr/bin/env python3
"""
Test outputs for Kotlin FIR annotation repeatable checks fix.

This tests the fix for KT-85005: Annotation repeatable checks around ALL use-site target.
The bug was that @all: use-site target wasn't being properly handled when checking for
repeated annotations, leading to missing REPEATED_ANNOTATION errors.
"""

import subprocess
import sys
from pathlib import Path

REPO = "/workspace/kotlin"


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
# LIGHTWEIGHT PASS-TO-PASS TESTS - Repo sanity checks
# =============================================================================


def test_repo_cloned():
    """
    Verify the Kotlin repository was cloned and is at the expected commit.
    """
    # Check the repo exists
    assert Path(REPO).exists(), f"Kotlin repository not found at {REPO}"
    assert (Path(REPO) / ".git").exists(), f"Not a git repository: {REPO}"

    # Check we can read the git log
    result = subprocess.run(
        ["git", "log", "-1", "--oneline"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30
    )
    assert result.returncode == 0, f"Git log failed: {result.stderr}"
    # Check we're at a valid commit (either base 4cf5ab5ee40 or the fixed 3325ebdb5ef)
    valid_commits = ["4cf5ab5ee40", "3325ebdb5ef"]
    assert any(c in result.stdout for c in valid_commits), f"Not at expected commit: {result.stdout}"


def test_gradle_wrapper_present():
    """
    Verify the Gradle wrapper is present and executable.
    """
    gradlew = Path(REPO) / "gradlew"
    assert gradlew.exists(), "Gradle wrapper not found"
    assert gradlew.stat().st_mode & 0o111, "Gradle wrapper not executable"


def test_key_source_files_present():
    """
    Verify key source files are present in the repository.
    """
    key_files = [
        "compiler/fir/checkers/src/org/jetbrains/kotlin/fir/analysis/checkers/FirAnnotationHelpers.kt",
        "compiler/fir/checkers/src/org/jetbrains/kotlin/fir/analysis/checkers/declaration/FirAnnotationChecker.kt",
        "compiler/fir/checkers/src/org/jetbrains/kotlin/fir/analysis/checkers/declaration/FirOptInMarkedDeclarationChecker.kt",
        "compiler/fir/checkers/src/org/jetbrains/kotlin/fir/analysis/checkers/declaration/FirSupertypesChecker.kt",
        "compiler/fir/tree/tree-generator/src/org/jetbrains/kotlin/fir/tree/generator/FirTree.kt",
    ]

    for file_path in key_files:
        full_path = Path(REPO) / file_path
        assert full_path.exists(), f"Key source file not found: {file_path}"


def test_gradle_basic_command():
    """
    Basic Gradle sanity check - verify the wrapper works.
    """
    result = subprocess.run(
        ["./gradlew", "--version"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"Gradle version check failed: {result.stderr[:500]}"
    assert "Gradle" in result.stdout, "Gradle version output unexpected"


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v", "--tb=short"]))
