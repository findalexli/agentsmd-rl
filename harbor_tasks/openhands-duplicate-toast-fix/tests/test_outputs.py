"""
Tests for OpenHands PR #13649: Fix duplicate toast messages in billing route.

This task tests the fix for a React useEffect dependency issue where unstable
object references (searchParams) caused the effect to re-fire on every render,
resulting in duplicate "Payment successful" toast messages.
"""

import subprocess
import re

REPO = "/workspace/OpenHands"
FRONTEND = f"{REPO}/frontend"
BILLING_FILE = f"{FRONTEND}/src/routes/billing.tsx"


def test_vitest_billing_tests():
    """Repo's billing tests pass (pass_to_pass)."""
    result = subprocess.run(
        ["npm", "run", "test", "--", "billing.test.tsx", "--run"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"Billing tests failed:\n{result.stderr[-1000:]}\n{result.stdout[-1000:]}"


def test_useeffect_has_primitive_dependencies():
    """useEffect dependency array uses primitive string values, not searchParams object (fail_to_pass).

    The bug: searchParams object has unstable reference, causing effect to re-fire.
    The fix: extract amount and sessionId as primitive strings outside the effect.
    """
    with open(BILLING_FILE, 'r') as f:
        content = f.read()

    # Find the useEffect hook
    useeffect_match = re.search(
        r'React\.useEffect\s*\(\s*\(\)\s*=>\s*\{[^}]+\}\s*,\s*\[([^\]]+)\]',
        content,
        re.DOTALL
    )

    if not useeffect_match:
        # Try alternative pattern with React.useEffect(() => {...}, [deps])
        useeffect_match = re.search(
            r'React\.useEffect\s*\(\s*\(\)\s*=>\s*\{.*?\}\s*,\s*\[([^\]]+)\]',
            content,
            re.DOTALL
        )

    assert useeffect_match, "Could not find useEffect hook with dependency array in billing.tsx"

    deps_str = useeffect_match.group(1)

    # Check that searchParams is NOT in the dependency array (the bug)
    assert "searchParams" not in deps_str, (
        f"BUG: searchParams object found in useEffect dependencies: [{deps_str}]. "
        "This causes unstable references and duplicate toasts. "
        "Extract 'amount' and 'sessionId' as primitive strings outside the effect instead."
    )

    # Check that primitive 'amount' and 'sessionId' ARE in the dependency array (the fix)
    assert "amount" in deps_str, (
        f"Expected 'amount' in useEffect dependencies, but got: [{deps_str}]. "
        "Extract searchParams.get('amount') as a primitive string outside the effect."
    )

    assert "sessionId" in deps_str, (
        f"Expected 'sessionId' in useEffect dependencies, but got: [{deps_str}]. "
        "Extract searchParams.get('session_id') as a primitive string outside the effect."
    )


def test_searchparams_extracted_outside_effect():
    """amount and sessionId extracted outside useEffect as primitive values (fail_to_pass).

    The fix requires extracting these values before the effect so they have stable references.
    """
    with open(BILLING_FILE, 'r') as f:
        content = f.read()

    # Find the component function
    # Check for primitive extraction before useEffect
    # Pattern: const amount = searchParams.get("amount"); (outside useEffect)

    # Look for extraction of amount and sessionId at component level
    amount_pattern = r'const\s+amount\s*=\s*searchParams\.get\s*\(\s*["\']amount["\']\s*\)'
    sessionid_pattern = r'const\s+sessionId\s*=\s*searchParams\.get\s*\(\s*["\']session_id["\']\s*\)'

    amount_match = re.search(amount_pattern, content)
    sessionid_match = re.search(sessionid_pattern, content)

    assert amount_match, (
        "Expected 'const amount = searchParams.get(\"amount\")' to be extracted "
        "outside the useEffect at component level. This ensures stable primitive reference."
    )

    assert sessionid_match, (
        "Expected 'const sessionId = searchParams.get(\"session_id\")' to be extracted "
        "outside the useEffect at component level. This ensures stable primitive reference."
    )

    # Verify these are NOT inside the useEffect callback (i.e., at component level)
    # Find the useEffect callback
    useeffect_start = content.find('React.useEffect')

    if useeffect_start > 0:
        # Check that the extractions happen BEFORE the useEffect
        amount_pos = amount_match.start()
        sessionid_pos = sessionid_match.start()

        assert amount_pos < useeffect_start, (
            "The 'amount' extraction should be outside useEffect, at component level"
        )
        assert sessionid_pos < useeffect_start, (
            "The 'sessionId' extraction should be outside useEffect, at component level"
        )


def test_no_searchparams_get_inside_effect():
    """searchParams.get() calls should not be inside the useEffect callback (fail_to_pass).

    The bug was having searchParams.get() calls inside the effect. After the fix,
    these should be at component level with the values passed as dependencies.
    """
    with open(BILLING_FILE, 'r') as f:
        content = f.read()

    # Find the useEffect callback body
    useeffect_match = re.search(
        r'React\.useEffect\s*\(\s*\(\)\s*=>\s*\{([^}]+(?:\{[^}]*\}[^}]*)*)\}\s*,\s*\[',
        content,
        re.DOTALL
    )

    if not useeffect_match:
        # Try simpler pattern
        useeffect_match = re.search(
            r'React\.useEffect\s*\(\s*\(\)\s*=>\s*\{(.*?)\}\s*,\s*\[',
            content,
            re.DOTALL
        )

    if useeffect_match:
        effect_body = useeffect_match.group(1)

        # The effect body should NOT contain searchParams.get calls (these cause the bug)
        # Allow for commented-out code or the fixed version where we just use the primitives
        searchparams_get_in_effect = re.search(
            r'searchParams\.get\s*\(',
            effect_body
        )

        # This is a soft check - if they exist, they should be the problem
        if searchparams_get_in_effect:
            # Count how many - should be 0 in the fixed version
            count = len(re.findall(r'searchParams\.get\s*\(', effect_body))
            assert count == 0, (
                f"Found {count} searchParams.get() call(s) inside useEffect. "
                "These should be extracted outside the effect to prevent unstable dependencies."
            )


def test_checkout_status_extraction():
    """checkoutStatus extracted as primitive outside useEffect (fail_to_pass).

    checkoutStatus was already being extracted correctly, but we verify it's maintained.
    """
    with open(BILLING_FILE, 'r') as f:
        content = f.read()

    # Find checkoutStatus extraction
    checkout_pattern = r'const\s+checkoutStatus\s*=\s*searchParams\.get\s*\(\s*["\']checkout["\']\s*\)'
    checkout_match = re.search(checkout_pattern, content)

    assert checkout_match, (
        "Expected 'const checkoutStatus = searchParams.get(\"checkout\")' to be extracted "
        "outside the useEffect."
    )


def test_frontend_lint_passes():
    """Frontend lint check passes (pass_to_pass)."""
    result = subprocess.run(
        ["npm", "run", "lint"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=120,
    )
    # Note: Some warnings are acceptable, but the command should succeed
    assert result.returncode == 0, f"Lint failed:\n{result.stderr[-500:]}\n{result.stdout[-500:]}"


def test_frontend_typecheck_passes():
    """Frontend TypeScript type check passes (pass_to_pass)."""
    result = subprocess.run(
        ["npm", "run", "typecheck"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"Type check failed:\n{result.stderr[-500:]}\n{result.stdout[-500:]}"


def test_frontend_build_passes():
    """Frontend production build passes (pass_to_pass)."""
    result = subprocess.run(
        ["npm", "run", "build"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert result.returncode == 0, f"Build failed:\n{result.stderr[-500:]}\n{result.stdout[-500:]}"


def test_frontend_translation_completeness():
    """Frontend translation completeness check passes (pass_to_pass)."""
    result = subprocess.run(
        ["npm", "run", "check-translation-completeness"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, f"Translation check failed:\n{result.stderr[-500:]}\n{result.stdout[-500:]}"
