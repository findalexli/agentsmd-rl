"""
Test suite for Kotlin FIR PR #5826: Report warning on `_` variables with implicit Unit type.

This tests that the compiler correctly reports UNNAMED_PROPERTY_WITH_IMPLICIT_UNIT_TYPE
when a `_` variable has its type inferred to Unit implicitly (not via explicit type annotation).

These tests verify file contents (grep-based) for faster validation.
"""

import os
import re

# Note: In the Docker test environment, the repo is at /workspace/kotlin
REPO = "/workspace/kotlin"

# Key files that are modified by this PR
CHECKER_FILE = "compiler/fir/checkers/src/org/jetbrains/kotlin/fir/analysis/checkers/declaration/FirUnnamedPropertyChecker.kt"
DIAGNOSTICS_LIST_FILE = "compiler/fir/checkers/checkers-component-generator/src/org/jetbrains/kotlin/fir/checkers/generator/diagnostics/FirDiagnosticsList.kt"
DIAGNOSTICS_FILE = "compiler/fir/checkers/gen/org/jetbrains/kotlin/fir/analysis/diagnostics/FirErrors.kt"
MESSAGES_FILE = "compiler/fir/checkers/src/org/jetbrains/kotlin/fir/analysis/diagnostics/FirErrorsDefaultMessages.kt"
TESTDATA_FILE = "compiler/testData/diagnostics/tests/unnamedLocalVariables/withUnitType.kt"


# =============================================================================
# FAIL-TO-PASS TESTS (Must fail on base commit, pass after fix)
# These tests verify the fix by checking file contents.
# =============================================================================


def test_new_diagnostic_in_diagnostics_list():
    """
    Fail-to-pass: DIAGNOSTICS_LIST must contain UNNAMED_PROPERTY_WITH_IMPLICIT_UNIT_TYPE.

    Verifies the diagnostic is defined as a warning in the diagnostic list generator.
    This is the source of truth for generated diagnostic files.
    """
    diagnostics_list_path = os.path.join(REPO, DIAGNOSTICS_LIST_FILE)

    with open(diagnostics_list_path, 'r') as f:
        content = f.read()

    # Check for the new diagnostic definition
    assert "UNNAMED_PROPERTY_WITH_IMPLICIT_UNIT_TYPE" in content, (
        "UNNAMED_PROPERTY_WITH_IMPLICIT_UNIT_TYPE not found in DIAGNOSTICS_LIST"
    )

    # Verify it's defined as a warning (not error)
    pattern = r"UNNAMED_PROPERTY_WITH_IMPLICIT_UNIT_TYPE\s+by\s+warning"
    assert re.search(pattern, content), (
        "UNNAMED_PROPERTY_WITH_IMPLICIT_UNIT_TYPE should be defined as a warning"
    )


def test_checker_contains_unit_warning_logic():
    """
    Fail-to-pass: FirUnnamedPropertyChecker must contain the new warning logic.

    Verifies the checker has the logic to detect underscore variables with
    implicit Unit type using isUnitOrFlexibleUnit and ImplicitTypeRef checks.
    """
    checker_path = os.path.join(REPO, CHECKER_FILE)

    with open(checker_path, 'r') as f:
        content = f.read()

    # Check for the key logic components
    assert "UNNAMED_PROPERTY_WITH_IMPLICIT_UNIT_TYPE" in content, (
        "Checker missing UNNAMED_PROPERTY_WITH_IMPLICIT_UNIT_TYPE diagnostic report"
    )

    # Check for type comparison logic
    assert "isUnitOrFlexibleUnit" in content, (
        "Checker missing isUnitOrFlexibleUnit type check"
    )

    # Check for implicit type detection
    assert "ImplicitTypeRef" in content or "KtFakeSourceElementKind.ImplicitTypeRef" in content, (
        "Checker missing implicit type detection"
    )


def test_error_message_defined():
    """
    Fail-to-pass: FirErrorsDefaultMessages must define the error message text.

    Verifies the human-readable error message is defined for the new diagnostic.
    """
    messages_path = os.path.join(REPO, MESSAGES_FILE)

    with open(messages_path, 'r') as f:
        content = f.read()

    assert "UNNAMED_PROPERTY_WITH_IMPLICIT_UNIT_TYPE" in content, (
        "Error message for UNNAMED_PROPERTY_WITH_IMPLICIT_UNIT_TYPE not defined"
    )

    # Check for expected message text
    expected_patterns = [
        "underscore property is inferred to",
        "Unit",
    ]
    for pattern in expected_patterns:
        assert pattern in content, (
            f"Error message missing expected text: {pattern}"
        )


def test_analysis_api_converter_exists():
    """
    Fail-to-pass: Analysis API must have converter for the new diagnostic.

    Verifies the IDE Analysis API can convert this FIR diagnostic to its own model.
    """
    converter_path = os.path.join(
        REPO,
        "analysis/analysis-api-fir/gen/org/jetbrains/kotlin/analysis/api/fir/diagnostics/KaFirDataClassConverters.kt"
    )

    with open(converter_path, 'r') as f:
        content = f.read()

    assert "UNNAMED_PROPERTY_WITH_IMPLICIT_UNIT_TYPE" in content, (
        "Analysis API converter missing UNNAMED_PROPERTY_WITH_IMPLICIT_UNIT_TYPE"
    )
    assert "UnnamedPropertyWithImplicitUnitTypeImpl" in content, (
        "Analysis API converter missing UnnamedPropertyWithImplicitUnitTypeImpl"
    )


def test_analysis_api_diagnostic_interface():
    """
    Fail-to-pass: Analysis API must define diagnostic interface.

    Verifies KaFirDiagnostic interface is defined for UnnamedPropertyWithImplicitUnitType.
    """
    diagnostics_path = os.path.join(
        REPO,
        "analysis/analysis-api-fir/gen/org/jetbrains/kotlin/analysis/api/fir/diagnostics/KaFirDiagnostics.kt"
    )

    with open(diagnostics_path, 'r') as f:
        content = f.read()

    assert "UnnamedPropertyWithImplicitUnitType" in content, (
        "Analysis API KaFirDiagnostic.UnnamedPropertyWithImplicitUnitType interface missing"
    )


def test_analysis_api_implementation():
    """
    Fail-to-pass: Analysis API must have implementation class.

    Verifies the implementation class exists for the IDE Analysis API.
    """
    impl_path = os.path.join(
        REPO,
        "analysis/analysis-api-fir/gen/org/jetbrains/kotlin/analysis/api/fir/diagnostics/KaFirDiagnosticsImpl.kt"
    )

    with open(impl_path, 'r') as f:
        content = f.read()

    assert "UnnamedPropertyWithImplicitUnitTypeImpl" in content, (
        "Analysis API UnnamedPropertyWithImplicitUnitTypeImpl class missing"
    )


def test_testdata_file_exists():
    """
    Fail-to-pass: Test data file withUnitType.kt must exist with proper test cases.

    This is the primary test file that exercises the diagnostic.
    """
    testdata_path = os.path.join(REPO, TESTDATA_FILE)
    assert os.path.exists(testdata_path), (
        f"Test data file {TESTDATA_FILE} does not exist"
    )

    with open(testdata_path, 'r') as f:
        content = f.read()

    # Check for expected test markers
    assert "UNNAMED_PROPERTY_WITH_IMPLICIT_UNIT_TYPE" in content, (
        "Test data missing UNNAMED_PROPERTY_WITH_IMPLICIT_UNIT_TYPE markers"
    )

    # Check for issue reference
    assert "KT-84618" in content, (
        "Test data missing issue reference KT-84618"
    )

    # Check for required directives
    assert "RUN_PIPELINE_TILL: BACKEND" in content, (
        "Test data missing RUN_PIPELINE_TILL: BACKEND directive"
    )

    # Check for language feature flags
    assert "UnnamedLocalVariables" in content, (
        "Test data missing UnnamedLocalVariables feature flag"
    )


def test_testdata_implicit_cases_have_warnings():
    """
    Fail-to-pass: Test data must have warning markers on implicit Unit cases.

    Verifies the test data marks expected warnings for cases like:
    - val _ = Unit
    - val _ = returnUnit()
    - for (_ in arrayOf(Unit, Unit)) { }
    """
    testdata_path = os.path.join(REPO, TESTDATA_FILE)

    with open(testdata_path, 'r') as f:
        content = f.read()

    # Find testWithImplicit function section
    implicit_match = re.search(
        r'fun testWithImplicit\(\).*?(?=fun testWithExplicit|\Z)',
        content,
        re.DOTALL
    )
    assert implicit_match, "Could not find testWithImplicit() function in test data"

    implicit_section = implicit_match.group(0)

    # Should have warning markers in implicit section
    warning_count = implicit_section.count("<!UNNAMED_PROPERTY_WITH_IMPLICIT_UNIT_TYPE!>")
    assert warning_count >= 3, (
        f"Expected at least 3 implicit Unit warnings in testWithImplicit, found {warning_count}"
    )


def test_testdata_explicit_no_warning():
    """
    Fail-to-pass: Explicit Unit type annotations should NOT trigger warning.

    Verifies that the test data correctly has no warning markers for explicit
    type annotations like `val _: Unit = Unit`.
    """
    testdata_path = os.path.join(REPO, TESTDATA_FILE)

    with open(testdata_path, 'r') as f:
        content = f.read()

    # Find testWithExplicit function section
    explicit_match = re.search(
        r'fun testWithExplicit\(\).*?(?=\/\* GENERATED|\Z)',
        content,
        re.DOTALL
    )
    assert explicit_match, "Could not find testWithExplicit() function in test data"

    explicit_section = explicit_match.group(0)

    # Should NOT have warning markers in explicit section
    assert "<!UNNAMED_PROPERTY_WITH_IMPLICIT_UNIT_TYPE!>" not in explicit_section, (
        "Explicit Unit type annotations should not trigger the warning - "
        "testWithExplicit section has unexpected warning markers"
    )


def test_scripting_testdata_updated():
    """
    Fail-to-pass: Scripting test data must be updated to avoid false positives.

    The scripting test file had a function returning Unit implicitly which would
    trigger the new warning. It should be updated to return Int instead.
    """
    # Check both possible locations
    script_paths = [
        "plugins/scripting/scripting-tests/testData/testScripts/unnamedLocalVariables.test.kts",
        "plugins/scripting/scripting-tests/testData/codegen/testScripts/unnamedLocalVariables.test.kts",
    ]

    found_file = False
    for script_path in script_paths:
        full_path = os.path.join(REPO, script_path)
        if os.path.exists(full_path):
            found_file = True
            with open(full_path, 'r') as f:
                content = f.read()

            # The function should return Int (not Unit) to avoid triggering the warning
            assert "fun call(): Int" in content, (
                f"Script test {script_path} should have call() returning Int to avoid Unit warning"
            )
            break

    if not found_file:
        # If file doesn't exist, that's okay - the location may have changed
        pass


# =============================================================================
# PASS-TO-PASS TESTS (Must pass on both base and after fix)
# These verify the compiler infrastructure is intact.
# =============================================================================


def test_compiler_module_structure():
    """
    Pass-to-pass: Verify the compiler module structure is intact.

    This validates that the FIR checkers module has proper source directories
    and key files exist.
    """
    # Key directories that should exist
    dirs_to_check = [
        "compiler/fir/checkers/src/org/jetbrains/kotlin/fir/analysis/checkers/declaration",
        "compiler/fir/checkers/src/org/jetbrains/kotlin/fir/analysis/diagnostics",
        "compiler/testData/diagnostics/tests",
        "analysis/analysis-api-fir/gen/org/jetbrains/kotlin/analysis/api/fir/diagnostics",
    ]

    for dir_path in dirs_to_check:
        full_path = os.path.join(REPO, dir_path)
        assert os.path.isdir(full_path), f"Required directory missing: {dir_path}"


def test_checker_base_structure():
    """
    Pass-to-pass: FirUnnamedPropertyChecker has valid base structure.

    Verifies the checker extends the right class and has the check method.
    """
    checker_path = os.path.join(REPO, CHECKER_FILE)

    with open(checker_path, 'r') as f:
        content = f.read()

    # Check for valid checker structure
    assert "object FirUnnamedPropertyChecker" in content, (
        "Checker should be a singleton object"
    )
    assert "FirPropertyChecker(MppCheckerKind.Common)" in content, (
        "Should extend FirPropertyChecker"
    )
    assert "override fun check(declaration: FirProperty)" in content, (
        "Should have check method for FirProperty"
    )


def test_existing_checkers_still_work():
    """
    Pass-to-pass: Existing unnamed property checkers still work.

    Verifies that UNNAMED_VAR_PROPERTY and UNNAMED_DELEGATED_PROPERTY
    diagnostics are still being reported correctly.
    """
    checker_path = os.path.join(REPO, CHECKER_FILE)

    with open(checker_path, 'r') as f:
        content = f.read()

    # Check that existing diagnostics are still present
    assert "UNNAMED_VAR_PROPERTY" in content, (
        "Checker missing UNNAMED_VAR_PROPERTY (existing diagnostic)"
    )
    assert "UNNAMED_DELEGATED_PROPERTY" in content, (
        "Checker missing UNNAMED_DELEGATED_PROPERTY (existing diagnostic)"
    )


def test_testdata_directory_structure():
    """
    Pass-to-pass: Test data directories have expected structure.

    Verifies that the unnamedLocalVariables test directory exists and
    has the expected format.
    """
    testdata_dir = os.path.join(REPO, "compiler/testData/diagnostics/tests/unnamedLocalVariables")

    assert os.path.exists(testdata_dir), (
        "unnamedLocalVariables testdata directory should exist"
    )

    # Check for existing test files
    kt_files = [f for f in os.listdir(testdata_dir) if f.endswith('.kt')]
    assert len(kt_files) > 0, "No .kt test data files found in unnamedLocalVariables"


def test_diagnostics_list_has_base_entries():
    """
    Pass-to-pass: DIAGNOSTICS_LIST has existing unnamed property diagnostics.

    Verifies the diagnostic list contains the base UNNAMED_VAR_PROPERTY
    and UNNAMED_DELEGATED_PROPERTY entries.
    """
    diagnostics_list_path = os.path.join(REPO, DIAGNOSTICS_LIST_FILE)

    with open(diagnostics_list_path, 'r') as f:
        content = f.read()

    # Check for existing diagnostics
    assert "UNNAMED_VAR_PROPERTY" in content, (
        "DIAGNOSTICS_LIST missing UNNAMED_VAR_PROPERTY"
    )
    assert "UNNAMED_DELEGATED_PROPERTY" in content, (
        "DIAGNOSTICS_LIST missing UNNAMED_DELEGATED_PROPERTY"
    )


def test_analysis_api_base_structure():
    """
    Pass-to-pass: Analysis API has expected base structure.

    Verifies the Analysis API files for unnamed property diagnostics exist
    and have the expected base interfaces.
    """
    # Check KaFirDiagnostics.kt
    diagnostics_path = os.path.join(
        REPO,
        "analysis/analysis-api-fir/gen/org/jetbrains/kotlin/analysis/api/fir/diagnostics/KaFirDiagnostics.kt"
    )

    with open(diagnostics_path, 'r') as f:
        content = f.read()

    # Check for existing unnamed property interfaces
    assert "UnnamedDelegatedProperty" in content, (
        "Analysis API missing UnnamedDelegatedProperty interface"
    )
