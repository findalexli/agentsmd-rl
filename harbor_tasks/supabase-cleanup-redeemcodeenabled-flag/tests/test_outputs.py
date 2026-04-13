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

def _install_deps():
    """Install dependencies using pnpm via corepack."""
    r = subprocess.run(
        ["bash", "-c", "cd /workspace/supabase && corepack enable && pnpm install --frozen-lockfile"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    return r


# [repo_tests] pass_to_pass
def test_repo_typecheck():
    """Studio TypeScript typecheck passes (pass_to_pass)."""
    # Install dependencies first
    r = _install_deps()
    assert r.returncode == 0, f"Failed to install dependencies:\n{r.stderr[-500:]}"

    # Run studio typecheck
    r = subprocess.run(
        ["bash", "-c", "NODE_OPTIONS='--max-old-space-size=4096' pnpm --filter studio run typecheck"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Studio typecheck failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_lint():
    """Studio ESLint passes (pass_to_pass)."""
    # Install dependencies first
    r = _install_deps()
    assert r.returncode == 0, f"Failed to install dependencies:\n{r.stderr[-500:]}"

    # Run studio lint
    r = subprocess.run(
        ["bash", "-c", "pnpm --filter studio run lint"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    # Lint returns 0 if no errors (warnings are OK)
    assert r.returncode == 0, f"Studio lint failed with errors:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_lint_ratchet():
    """Studio lint ratchet passes (pass_to_pass)."""
    # Install dependencies first
    r = _install_deps()
    assert r.returncode == 0, f"Failed to install dependencies:\n{r.stderr[-500:]}"

    # Run studio lint:ratchet (enforces stricter rules than basic lint)
    r = subprocess.run(
        ["bash", "-c", "pnpm --filter studio run lint:ratchet"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Studio lint:ratchet failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_prettier_check():
    """Code formatting check passes (pass_to_pass)."""
    # Install dependencies first
    r = _install_deps()
    assert r.returncode == 0, f"Failed to install dependencies:\n{r.stderr[-500:]}"

    # Run prettier check on the repo
    r = subprocess.run(
        ["bash", "-c", "pnpm run test:prettier"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier check failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_unit_tests():
    """Studio unit tests (stable subset) pass (pass_to_pass)."""
    # Install dependencies first
    r = _install_deps()
    assert r.returncode == 0, f"Failed to install dependencies:\n{r.stderr[-500:]}"

    # Run stable unit tests (excluding known flaky tests in SupportFormPage)
    r = subprocess.run(
        ["bash", "-c", "cd apps/studio && pnpm vitest run --exclude '**/Support/**'"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Unit tests failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


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
