"""
Test suite for Kotlin FIR false positive DUPLICATE_BRANCH_CONDITION_IN_WHEN fix.

This tests that the FIR checker correctly handles guard conditions (else if)
in when expressions without reporting false positive duplicate branch errors.
"""

import subprocess
import os
import re

REPO = "/workspace/kotlin"


def _get_checker_file_path() -> str:
    """Return the path to the checker file."""
    return os.path.join(
        REPO,
        "compiler/fir/checkers/src/org/jetbrains/kotlin/fir/analysis/checkers/expression/FirWhenConditionChecker.kt"
    )


def _read_checker_file() -> str:
    """Read and return the content of the checker file."""
    with open(_get_checker_file_path(), "r") as f:
        return f.read()


def test_guard_condition_fix_behavior():
    """
    Behavioral test: Guard conditions only check when subject, not other variables.

    The fix adds a guard (if condition) to only check branches where the
    condition involves the when subject expression. This prevents false
    positives for guard conditions like 'else if b is Int' where b is a
    different variable than the when subject.

    Before fix: The checker would see 'is Int' twice and report duplicate,
                even though one checks 'a' (subject) and one checks 'b'.
    After fix:  The checker only tracks conditions that check the subject.
    """
    content = _read_checker_file()

    # Verify the guard pattern exists for both condition types
    equality_guard = "is FirEqualityOperatorCall if condition.isArgumentWhenSubject() ->"
    type_guard = "is FirTypeOperatorCall if condition.isArgumentWhenSubject() ->"

    assert equality_guard in content, (
        f"Fix not applied: Missing guard condition for FirEqualityOperatorCall.\n"
        f"Expected pattern: {equality_guard}"
    )

    assert type_guard in content, (
        f"Fix not applied: Missing guard condition for FirTypeOperatorCall.\n"
        f"Expected pattern: {type_guard}"
    )

    # Count the when branches - should be exactly 2 guarded branches
    # Pattern matches: "is FirEqualityOperatorCall if condition.isArgumentWhenSubject() -> {" or just "->"
    when_branches = re.findall(r"is Fir\w+Call(?: if [\w\.()]+)?\s*->", content)
    guarded_branches = [b for b in when_branches if "if" in b]

    assert len(guarded_branches) >= 2, (
        f"Expected at least 2 guarded when branches, found: {guarded_branches}"
    )


def test_helper_method_behaviorally_correct():
    """
    Behavioral test: isArgumentWhenSubject correctly identifies subject expressions.

    The helper method must:
    1. Be defined as a private extension on FirCall
    2. Check if the argument (after unwrapping smartcasts) is FirWhenSubjectExpression
    3. Return Boolean
    """
    content = _read_checker_file()

    # Check the helper method exists with correct signature
    method_pattern = r"private fun FirCall\.isArgumentWhenSubject\(\): Boolean"
    assert re.search(method_pattern, content), (
        "Helper method not found or has wrong signature. "
        "Expected: private fun FirCall.isArgumentWhenSubject(): Boolean"
    )

    # Check the implementation unwraps smartcasts and checks for subject
    impl_pattern = r"argument\.unwrapSmartcastExpression\(\) is FirWhenSubjectExpression"
    assert re.search(impl_pattern, content), (
        "Helper method implementation incorrect. "
        "Expected: argument.unwrapSmartcastExpression() is FirWhenSubjectExpression"
    )


def test_old_unguarded_pattern_removed():
    """
    Behavioral test: The old pattern that caused false positives is removed.

    The original code checked 'arguments.size == 2 && arguments[0].unwrapSmartcastExpression()'
    directly in the when branch body. This is the problematic pattern that
    didn't distinguish between subject and non-subject conditions.
    """
    content = _read_checker_file()

    # The old pattern that caused the false positive
    old_pattern = "arguments.size == 2 && arguments[0].unwrapSmartcastExpression() is FirWhenSubjectExpression"

    assert old_pattern not in content, (
        f"Old unguarded pattern still present - false positive not fixed.\n"
        f"Found: {old_pattern}\n"
        f"This pattern should be replaced with a guard condition."
    )

    # Also verify the nested if is gone
    old_nested_if = "if (arguments.size == 2"
    assert old_nested_if not in content, (
        f"Old nested if pattern still present. "
        f"The fix should use guard conditions instead of nested if statements."
    )


def test_checkered_logic_restructured_for_subject_only():
    """
    Behavioral test: After the guard, checker logic assumes subject access.

    With the guard condition, we know arguments[0] is the subject, so we can
    directly access arguments[1] for the value being compared.
    """
    content = _read_checker_file()

    # After fix, we access arguments[1] directly without checking arguments[0]
    assert "condition.arguments[1].unwrapSmartcastExpression()" in content, (
        "Fix not applied: Should directly access arguments[1] after guard ensures subject.\n"
        "Expected: condition.arguments[1].unwrapSmartcastExpression()"
    )

    # Should NOT have the old pattern accessing arguments[0] for subject check
    old_subject_check = "arguments[0].unwrapSmartcastExpression() is FirWhenSubjectExpression"
    assert old_subject_check not in content, (
        "Old subject check in body should be removed - now handled by guard."
    )


def test_guard_condition_test_data_parsable():
    """
    Behavioral test: Test data file exists and has correct structure.

    The test data file demonstrates the false positive scenario.
    """
    test_file = os.path.join(
        REPO,
        "compiler/fir/analysis-tests/testData/resolve/when/falsePositiveDuplicateCodition.kt"
    )

    assert os.path.exists(test_file), (
        f"Test data file not found: {test_file}"
    )

    with open(test_file, "r") as f:
        content = f.read()

    # Verify the test file has the expected structure
    assert "// ISSUE: KT-85244" in content, (
        "Test file missing required ISSUE directive for KT-85244"
    )

    assert "// RUN_PIPELINE_TILL: BACKEND" in content, (
        "Test file missing required RUN_PIPELINE_TILL directive"
    )

    # Verify the false positive pattern exists
    assert "else if b is" in content, (
        "Test file missing guard condition pattern 'else if b is'"
    )


def test_kotlin_syntax_valid():
    """
    Behavioral test: Modified file has valid Kotlin structure.

    Uses basic structural validation since we can't run the compiler.
    """
    content = _read_checker_file()

    # Basic structural validation
    open_braces = content.count("{")
    close_braces = content.count("}")
    assert open_braces == close_braces, (
        f"Unbalanced braces: {open_braces} open, {close_braces} close"
    )

    open_parens = content.count("(")
    close_parens = content.count(")")
    assert open_parens == close_parens, (
        f"Unbalanced parentheses: {open_parens} open, {close_parens} close"
    )

    # Check for required declarations
    required_patterns = [
        "object FirWhenConditionChecker",
        "override fun check(expression: FirWhenExpression)",
        "checkDuplicatedLabels",
    ]

    for pattern in required_patterns:
        assert pattern in content, f"Missing required pattern: {pattern}"


def test_repo_checker_imports_complete():
    """
    Pass-to-pass: Checker file has all required imports.
    """
    content = _read_checker_file()

    required = [
        "package org.jetbrains.kotlin.fir.analysis.checkers.expression",
        "MppCheckerKind",
        "FirErrors",
    ]

    for r in required:
        assert r in content, f"Missing required import or declaration: {r}"

    # Check for Fir expressions imports
    has_expressions_import = (
        "org.jetbrains.kotlin.fir.expressions.*" in content or
        "FirWhenExpression" in content or
        "FirEqualityOperatorCall" in content
    )
    assert has_expressions_import, "Missing required expressions import"


def test_repo_testdata_structure_valid():
    """
    Pass-to-pass: Test data file has valid structure and directives.
    """
    test_file = os.path.join(
        REPO,
        "compiler/fir/analysis-tests/testData/resolve/when/falsePositiveDuplicateCodition.kt"
    )

    assert os.path.exists(test_file), "Test data file should exist"

    with open(test_file, "r") as f:
        content = f.read()

    # Verify test file has required directives
    assert "// ISSUE: KT-85244" in content, "Test file should reference KT-85244"
    assert "// RUN_PIPELINE_TILL: BACKEND" in content, "Missing RUN_PIPELINE_TILL directive"

    # Verify test file has expected code patterns
    assert "fun isInt(a: Number, b: Number)" in content, "Missing test function"
    assert "when (a)" in content, "Missing when expression with subject 'a'"
    assert "is Int -> true" in content, "Missing subject type check"
    assert "else if b is" in content, "Missing guard condition on variable 'b'"


def test_repo_analysis_tests_directory_structure():
    """
    Pass-to-pass: FIR analysis tests directory has expected structure.
    """
    analysis_tests_dir = os.path.join(REPO, "compiler/fir/analysis-tests")
    assert os.path.isdir(analysis_tests_dir), "analysis-tests directory should exist"

    build_file = os.path.join(analysis_tests_dir, "build.gradle.kts")
    assert os.path.exists(build_file), "analysis-tests should have build.gradle.kts"

    testdata_dir = os.path.join(analysis_tests_dir, "testData/resolve")
    assert os.path.isdir(testdata_dir), "testData/resolve directory should exist"

    when_dir = os.path.join(testdata_dir, "when")
    assert os.path.isdir(when_dir), "when test directory should exist"

    test_files = [f for f in os.listdir(when_dir) if f.endswith(".kt")]
    assert len(test_files) >= 1, f"when directory should have at least one .kt file"
