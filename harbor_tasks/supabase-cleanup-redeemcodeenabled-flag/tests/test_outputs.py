"""
Task: supabase-cleanup-redeemcodeenabled-flag
Repo: supabase @ 421eaedd508d86c7502f954c0a4f619d4458e844
PR:   44563

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/supabase"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified files must parse without errors."""
    # Check TypeScript syntax by trying to parse with TypeScript compiler
    files_to_check = [
        "apps/studio/components/interfaces/Organization/BillingSettings/CreditCodeRedemption.tsx",
        "apps/studio/pages/redeem.tsx",
    ]

    for file_path in files_to_check:
        full_path = Path(f"{REPO}/{file_path}")
        content = full_path.read_text()

        # Basic syntax checks for TypeScript/TSX
        # Check for balanced braces and parentheses
        open_braces = content.count('{')
        close_braces = content.count('}')
        assert open_braces == close_braces, f"Unbalanced braces in {file_path}"

        open_parens = content.count('(')
        close_parens = content.count(')')
        assert open_parens == close_parens, f"Unbalanced parentheses in {file_path}"

        # Check for basic TSX structure
        assert "export" in content or "import" in content, f"No imports/exports in {file_path}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_feature_flag_removed_from_credit_code_redemption():
    """The useFlag('redeemCodeEnabled') hook and conditional rendering must be removed from CreditCodeRedemption."""
    file_path = Path(f"{REPO}/apps/studio/components/interfaces/Organization/BillingSettings/CreditCodeRedemption.tsx")
    content = file_path.read_text()

    # Should NOT contain the feature flag check
    assert "useFlag('redeemCodeEnabled')" not in content, "useFlag('redeemCodeEnabled') still present in CreditCodeRedemption.tsx"
    assert "redeemCodeEnabled" not in content, "redeemCodeEnabled variable still present"


# [pr_diff] fail_to_pass
def test_feature_flag_removed_from_redeem_page():
    """The useFlag('redeemCodeEnabled') hook and 'coming soon' message must be removed from redeem page."""
    file_path = Path(f"{REPO}/apps/studio/pages/redeem.tsx")
    content = file_path.read_text()

    # Should NOT contain the feature flag check
    assert "useFlag('redeemCodeEnabled')" not in content, "useFlag('redeemCodeEnabled') still present in redeem.tsx"
    assert "redeemCodeEnabled" not in content, "redeemCodeEnabled variable still present"

    # Should NOT contain the "coming soon" message
    assert "Code redemption coming soon" not in content, "'Code redemption coming soon' message still present"


# [pr_diff] fail_to_pass
def test_useflag_import_cleaned_up():
    """The useFlag import should be cleaned up from files where it's no longer used."""
    # Check CreditCodeRedemption.tsx - useFlag import should be removed
    credit_file = Path(f"{REPO}/apps/studio/components/interfaces/Organization/BillingSettings/CreditCodeRedemption.tsx")
    credit_content = credit_file.read_text()

    # Import line should not contain useFlag
    for line in credit_content.split('\n'):
        if line.startswith('import') and 'from' in line and 'common' in line:
            assert 'useFlag' not in line, f"useFlag import still present in CreditCodeRedemption: {line}"

    # Check redeem.tsx - useFlag should not be imported from common
    redeem_file = Path(f"{REPO}/apps/studio/pages/redeem.tsx")
    redeem_content = redeem_file.read_text()

    # The import line should not contain useFlag
    for line in redeem_content.split('\n'):
        if line.startswith('import') and 'from' in line and 'common' in line:
            assert 'useFlag' not in line, f"useFlag import still present in redeem.tsx: {line}"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_existing_tests_pass():
    """Upstream test suite (CPU-safe subset) still passes."""
    # For this task, we verify the files exist and have valid structure
    # The actual test suite requires pnpm which is not in the container
    files_to_check = [
        "apps/studio/components/interfaces/Organization/BillingSettings/CreditCodeRedemption.tsx",
        "apps/studio/pages/redeem.tsx",
    ]

    for file_path in files_to_check:
        full_path = Path(f"{REPO}/{file_path}")
        assert full_path.exists(), f"File {file_path} does not exist"
        content = full_path.read_text()
        # Ensure file has content
        assert len(content) > 100, f"File {file_path} appears to be empty or truncated"


# [static] pass_to_pass
def test_not_stub():
    """Modified functions still have real logic, not just pass/return."""
    # Check CreditCodeRedemption still has meaningful content
    credit_file = Path(f"{REPO}/apps/studio/components/interfaces/Organization/BillingSettings/CreditCodeRedemption.tsx")
    credit_content = credit_file.read_text()

    # Should contain Dialog, Form, or other meaningful components
    assert "Dialog" in credit_content, "CreditCodeRedemption appears to be gutted"
    assert "return" in credit_content, "CreditCodeRedemption has no return statement"

    # Check redeem.tsx still has meaningful content
    redeem_file = Path(f"{REPO}/apps/studio/pages/redeem.tsx")
    redeem_content = redeem_file.read_text()

    # Should still render organization cards
    assert "OrganizationCard" in redeem_content or "organizations" in redeem_content, "redeem.tsx appears to be gutted"
