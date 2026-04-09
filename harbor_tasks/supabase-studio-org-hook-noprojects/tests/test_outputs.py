"""
Task: supabase-studio-org-hook-noprojects
Repo: supabase/supabase @ e7bec24021de77053a9b9b05c06ab17789f1269b
PR:   44572

The NoProjectsOnPaidOrgInfo component was not receiving the 'organization' prop,
causing it to always return null. The fix switches to using useSelectedOrganizationQuery()
hook instead of receiving organization via props.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/supabase"
TARGET_FILE = "apps/studio/components/interfaces/Billing/NoProjectsOnPaidOrgInfo.tsx"
FILE_PATH = f"{REPO}/{TARGET_FILE}"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_typescript_valid():
    """Modified TypeScript/TSX file must be valid (balanced braces, no syntax errors)."""
    src = Path(FILE_PATH).read_text()

    # Check for basic TypeScript/TSX validity indicators
    # File should have balanced braces (basic sanity check)
    open_count = src.count('{')
    close_count = src.count('}')
    assert open_count == close_count, f"Unbalanced braces: {open_count} open vs {close_count} close"

    # Check for TypeScript/React component structure
    assert "export const NoProjectsOnPaidOrgInfo" in src, "Component should be exported as const"
    assert "return" in src, "Component should have a return statement"

    # Verify no obvious syntax issues (unmatched parentheses)
    paren_open = src.count('(')
    paren_close = src.count(')')
    assert paren_open == paren_close, f"Unbalanced parentheses: {paren_open} open vs {paren_close} close"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_uses_org_hook_not_props():
    """Component should use useSelectedOrganizationQuery hook, not receive org via props."""
    src = Path(FILE_PATH).read_text()

    # Should import the hook
    assert "useSelectedOrganizationQuery" in src, \
        "Component should import and use useSelectedOrganizationQuery hook"

    # Should NOT have props interface anymore
    assert "NoProjectsOnPaidOrgInfoProps" not in src, \
        "Component should not have a props interface (NoProjectsOnPaidOrgInfoProps)"

    # Should NOT receive organization as a prop
    assert "{ organization }" not in src, \
        "Component should not destructure organization from props"


# [pr_diff] fail_to_pass
def test_component_has_no_params():
    """Component should take no parameters (uses hook instead of props)."""
    src = Path(FILE_PATH).read_text()

    # Look for the component definition - should be `export const NoProjectsOnPaidOrgInfo = () => {`
    # and NOT `export const NoProjectsOnPaidOrgInfo = ({ organization }: NoProjectsOnPaidOrgInfoProps) => {`
    lines = src.split("\n")
    component_line = None
    for i, line in enumerate(lines):
        if "export const NoProjectsOnPaidOrgInfo" in line:
            component_line = line
            break

    assert component_line is not None, "Could not find component definition"
    assert "organization" not in component_line, \
        "Component should not have 'organization' in its parameter list"
    assert "NoProjectsOnPaidOrgInfoProps" not in component_line, \
        "Component should not reference props type"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub():
    """Component is not a stub - has the actual implementation logic."""
    src = Path(FILE_PATH).read_text()

    # Should have the actual implementation (not just pass/return null)
    assert "EXCLUDED_PLANS" in src, "Component should have EXCLUDED_PLANS logic"
    assert "isEligible" in src, "Component should have isEligible logic"
    assert "useOrgProjectsInfiniteQuery" in src, "Component should use useOrgProjectsInfiniteQuery"

    # Should have real JSX content, not empty
    assert "Admonition" in src, "Component should render Admonition"
    assert "organization.plan.name" in src or "organization?.plan?.name" in src, \
        "Component should reference organization plan name"


# [static] pass_to_pass
def test_imports_correct():
    """Component imports required dependencies correctly."""
    src = Path(FILE_PATH).read_text()

    # Should have required imports
    assert "import Link from 'next/link'" in src, "Should import Link from next/link"
    assert "import { Admonition } from 'ui-patterns'" in src, "Should import Admonition"
    assert "import { useOrgProjectsInfiniteQuery }" in src, \
        "Should import useOrgProjectsInfiniteQuery"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD regression tests
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_lint():
    """Repo's ESLint passes on studio app (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", "cd /workspace/supabase/apps/studio && npm install -g pnpm && pnpm install --frozen-lockfile && pnpm lint"],
        capture_output=True, text=True, timeout=120
    )
    assert r.returncode == 0, f"ESLint failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_tests_billing():
    """Repo's Billing component tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", "cd /workspace/supabase/apps/studio && npm install -g pnpm && pnpm install --frozen-lockfile && pnpm vitest --run tests/components/Billing"],
        capture_output=True, text=True, timeout=120
    )
    assert r.returncode == 0, f"Billing tests failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"
