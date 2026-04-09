"""Test outputs for the billing toast dependency fix task.

This module tests that the fix for duplicate payment successful toast messages
is correctly implemented in the billing.tsx component.
"""

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path("/workspace/openhands")
FRONTEND_DIR = REPO_ROOT / "frontend"
BILLING_FILE = FRONTEND_DIR / "src" / "routes" / "billing.tsx"
TEST_FILE = FRONTEND_DIR / "__tests__" / "routes" / "billing.test.tsx"


def test_billing_file_exists():
    """Verify the billing.tsx file exists."""
    assert BILLING_FILE.exists(), f"Billing file not found at {BILLING_FILE}"


def test_search_params_extracted_outside_effect():
    """Test that amount and sessionId are extracted as primitives outside useEffect.

    This is the core fix - extracting primitive values (strings) outside the effect
    so they don't cause unnecessary re-renders when the searchParams object changes.
    """
    content = BILLING_FILE.read_text()

    # Check that amount and sessionId are extracted at component level
    assert "const amount = searchParams.get(\"amount\");" in content, \
        "amount should be extracted as primitive outside useEffect"
    assert "const sessionId = searchParams.get(\"session_id\");" in content, \
        "sessionId should be extracted as primitive outside useEffect"

    # Verify the extraction happens before the useEffect
    amount_idx = content.find("const amount = searchParams.get")
    session_id_idx = content.find("const sessionId = searchParams.get")
    effect_idx = content.find("React.useEffect")

    assert amount_idx > 0 and amount_idx < effect_idx, \
        "amount extraction should be outside and before useEffect"
    assert session_id_idx > 0 and session_id_idx < effect_idx, \
        "sessionId extraction should be outside and before useEffect"


def test_useeffect_dependencies_use_primitives():
    """Test that useEffect dependency array uses primitives, not the searchParams object.

    The bug was caused by using the entire searchParams object in the dependency array,
    which has unstable identity and triggers the effect on every render.
    """
    content = BILLING_FILE.read_text()

    # Find the useEffect dependency array
    effect_start = content.find("React.useEffect(() => {")
    effect_end = content.find("}", effect_start)
    effect_section = content[effect_start:effect_end]

    # Get the dependency array (the part after the effect body)
    deps_start = content.find("}, [", effect_start)
    deps_end = content.find("]);", deps_start)
    deps_section = content[deps_start:deps_end]

    # Should use 'amount' and 'sessionId' (primitives) not 'searchParams' (object)
    assert "amount," in deps_section, \
        "useEffect dependencies should include 'amount' (primitive)"
    assert "sessionId," in deps_section, \
        "useEffect dependencies should include 'sessionId' (primitive)"

    # Should NOT include the full searchParams object
    assert "searchParams," not in deps_section, \
        "useEffect dependencies should NOT include the searchParams object (causes duplicate toasts)"


def test_no_searchparams_get_inside_effect():
    """Test that searchParams.get() is NOT called inside the useEffect body.

    The original bug had these calls inside the effect, which required searchParams
    to be in the dependency array. After the fix, they should be outside.
    """
    content = BILLING_FILE.read_text()

    # Find the useEffect body
    effect_start = content.find("React.useEffect(() => {")
    effect_end = content.find("}", effect_start)
    effect_body = content[effect_start:effect_end]

    # The effect body should NOT call searchParams.get()
    assert "searchParams.get(\"amount\")" not in effect_body, \
        "searchParams.get('amount') should not be called inside useEffect"
    assert "searchParams.get(\"session_id\")" not in effect_body, \
        "searchParams.get('session_id') should not be called inside useEffect"


def test_unit_tests_pass():
    """Test that the billing unit tests pass (fail-to-pass).

    The PR includes new tests that verify the toast is shown exactly once.
    These tests should fail on the base commit and pass after the fix.
    """
    result = subprocess.run(
        ["npm", "test", "--", "--run", "billing.test.tsx"],
        cwd=FRONTEND_DIR,
        capture_output=True,
        text=True,
        timeout=120,
    )

    assert result.returncode == 0, \
        f"Billing tests failed:\n{result.stdout}\n{result.stderr}"


def test_checkout_success_flow_test_exists():
    """Test that the new checkout success flow tests exist.

    The PR adds tests to verify the fix works correctly.
    """
    content = TEST_FILE.read_text()

    # Check for the new test cases
    assert "should display success toast exactly once" in content, \
        "Test for success toast exactly once should exist"
    assert "should display error toast exactly once on checkout cancel" in content, \
        "Test for error toast exactly once on cancel should exist"
    assert "mockDisplaySuccessToast" in content, \
        "Mock for displaySuccessToast should exist"
    assert "mockDisplayErrorToast" in content, \
        "Mock for displayErrorToast should exist"


def test_lint_passes():
    """Test that the code passes linting.

    Per AGENTS.md, frontend changes must pass lint:fix.
    """
    result = subprocess.run(
        ["npm", "run", "lint"],
        cwd=FRONTEND_DIR,
        capture_output=True,
        text=True,
        timeout=120,
    )

    assert result.returncode == 0, \
        f"Linting failed:\n{result.stdout}\n{result.stderr}"


def test_build_passes():
    """Test that the code builds successfully.

    Per AGENTS.md, frontend changes must build successfully.
    """
    result = subprocess.run(
        ["npm", "run", "build"],
        cwd=FRONTEND_DIR,
        capture_output=True,
        text=True,
        timeout=180,
    )

    assert result.returncode == 0, \
        f"Build failed:\n{result.stdout}\n{result.stderr}"
