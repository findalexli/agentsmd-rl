"""
Test suite for Git Conversation Routing feature implementation.

This validates the frontend implementation including:
- Component file creation and exports
- TypeScript type definitions
- Hook implementation with state management
- i18n key declarations and translations
- Permission integration
"""

import subprocess
import json
import os
from pathlib import Path

REPO = "/workspace/openhands"
FRONTEND = f"{REPO}/frontend"

# File paths to verify
COMPONENTS = {
    "claim_button": f"{FRONTEND}/src/components/features/org/claim-button.tsx",
    "git_org_row": f"{FRONTEND}/src/components/features/org/git-org-row.tsx",
    "git_conversation_routing": f"{FRONTEND}/src/components/features/org/git-conversation-routing.tsx",
}

HOOK = f"{FRONTEND}/src/hooks/organizations/use-git-conversation-routing.ts"
I18N_DECLARATION = f"{FRONTEND}/src/i18n/declaration.ts"
I18N_TRANSLATIONS = f"{FRONTEND}/src/i18n/translation.json"
PERMISSIONS = f"{FRONTEND}/src/utils/org/permissions.ts"
MANAGE_ORG = f"{FRONTEND}/src/routes/manage-org.tsx"

# Required i18n keys
REQUIRED_I18N_KEYS = [
    "ORG$GIT_CONVERSATION_ROUTING",
    "ORG$GIT_CONVERSATION_ROUTING_DESCRIPTION",
    "ORG$CLAIM",
    "ORG$CLAIMED",
    "ORG$DISCONNECT",
    "ORG$CLAIM_SUCCESS",
    "ORG$DISCONNECT_SUCCESS",
    "ORG$CLAIM_ERROR",
]

# Required exports from components
CLAIM_BUTTON_EXPORTS = ["ClaimButton", "getButtonState"]
GIT_ORG_ROW_EXPORTS = ["GitOrgRow"]
GIT_CONVERSATION_ROUTING_EXPORTS = ["GitConversationRouting"]
HOOK_EXPORTS = ["useGitConversationRouting", "GitOrg"]


def run_npm_test(test_pattern: str, timeout: int = 120) -> tuple[bool, str]:
    """Run npm test with a specific pattern and return (success, output)."""
    try:
        result = subprocess.run(
            ["npm", "run", "test", "--", "--run", "-t", test_pattern],
            cwd=FRONTEND,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return result.returncode == 0, result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return False, "Test timed out"
    except Exception as e:
        return False, str(e)


def test_claim_button_component_exists():
    """F2P: Verify claim-button.tsx component file exists with required exports."""
    assert os.path.exists(COMPONENTS["claim_button"]), \
        f"claim-button.tsx not found at {COMPONENTS['claim_button']}"

    content = Path(COMPONENTS["claim_button"]).read_text()

    # Check for required exports
    for export in CLAIM_BUTTON_EXPORTS:
        assert f"export function {export}" in content or f"export {{ {export} }}" in content or f"export {export}" in content, \
            f"Required export '{export}' not found in claim-button.tsx"

    # Check for ButtonState type
    assert "type ButtonState" in content, "ButtonState type not found"

    # Check for proper state handling
    assert "unclaimed" in content, "unclaimed state not handled"
    assert "claimed" in content, "claimed state not handled"
    assert "claiming" in content, "claiming state not handled"


def test_git_org_row_component_exists():
    """F2P: Verify git-org-row.tsx component file exists with required exports."""
    assert os.path.exists(COMPONENTS["git_org_row"]), \
        f"git-org-row.tsx not found at {COMPONENTS['git_org_row']}"

    content = Path(COMPONENTS["git_org_row"]).read_text()

    # Check for required exports
    for export in GIT_ORG_ROW_EXPORTS:
        assert f"export function {export}" in content or f"export {{ {export} }}" in content, \
            f"Required export '{export}' not found in git-org-row.tsx"

    # Check for props interface
    assert "interface GitOrgRowProps" in content, "GitOrgRowProps interface not found"

    # Check for org prop usage
    assert "org." in content, "org prop not used in component"
    assert "org.id" in content or "org.provider" in content or "org.name" in content, \
        "org properties not accessed"


def test_git_conversation_routing_component_exists():
    """F2P: Verify git-conversation-routing.tsx component file exists with required exports."""
    assert os.path.exists(COMPONENTS["git_conversation_routing"]), \
        f"git-conversation-routing.tsx not found at {COMPONENTS['git_conversation_routing']}"

    content = Path(COMPONENTS["git_conversation_routing"]).read_text()

    # Check for required exports
    for export in GIT_CONVERSATION_ROUTING_EXPORTS:
        assert f"export function {export}" in content or f"export {{ {export} }}" in content, \
            f"Required export '{export}' not found in git-conversation-routing.tsx"

    # Check for hook usage
    assert "useGitConversationRouting" in content, "Hook not used in component"

    # Check for GitOrgRow usage
    assert "GitOrgRow" in content, "GitOrgRow not rendered"

    # Check for proper data mapping
    assert "orgs.map" in content, "orgs not mapped to rows"


def test_hook_exists():
    """F2P: Verify use-git-conversation-routing.ts hook file exists with required exports."""
    assert os.path.exists(HOOK), f"Hook file not found at {HOOK}"

    content = Path(HOOK).read_text()

    # Check for required exports
    for export in HOOK_EXPORTS:
        assert f"export function {export}" in content or f"export interface {export}" in content or f"export type {export}" in content, \
            f"Required export '{export}' not found in hook"

    # Check for GitOrg interface/type
    assert "interface GitOrg" in content or "type GitOrg" in content, \
        "GitOrg type definition not found"

    # Check for state management
    assert "useState" in content, "useState not used for state management"
    assert "setOrgs" in content, "setOrgs not used to update state"

    # Check for claim/disconnect functions
    assert "claimOrg" in content, "claimOrg function not found"
    assert "disconnectOrg" in content, "disconnectOrg function not found"

    # Check for proper status types
    assert "unclaimed" in content, "unclaimed status not defined"
    assert "claimed" in content, "claimed status not defined"
    assert "claiming" in content, "claiming status not defined"
    assert "disconnecting" in content, "disconnecting status not defined"


def test_i18n_keys_declared():
    """F2P: Verify all required i18n keys are declared in declaration.ts."""
    content = Path(I18N_DECLARATION).read_text()

    for key in REQUIRED_I18N_KEYS:
        assert key in content, f"Required i18n key '{key}' not found in declaration.ts"


def test_i18n_translations_exist():
    """F2P: Verify all required i18n translations exist in translation.json."""
    with open(I18N_TRANSLATIONS, "r") as f:
        translations = json.load(f)

    for key in REQUIRED_I18N_KEYS:
        # Convert key format from ORG$KEY to ORG$KEY for JSON lookup
        json_key = key
        assert json_key in translations, f"Required translation key '{json_key}' not found in translation.json"

        # Check for English translation at minimum
        assert "en" in translations[json_key], f"English translation missing for '{json_key}'"


def test_permission_added():
    """F2P: Verify manage_org_claims permission is added to permissions.ts."""
    content = Path(PERMISSIONS).read_text()

    # Check for permission type definition
    assert 'type ManageOrgClaimsPermission = "manage_org_claims"' in content or \
           '"manage_org_claims"' in content, \
        "manage_org_claims permission type not defined"

    # Check for permission in PermissionKey union
    assert "ManageOrgClaimsPermission" in content or "manage_org_claims" in content, \
        "Permission not added to PermissionKey union"

    # Check for permission in adminOnly array
    lines = content.split("\n")
    in_admin_only = False
    found_permission = False
    for line in lines:
        if "const adminOnly" in line:
            in_admin_only = True
        if in_admin_only and "manage_org_claims" in line:
            found_permission = True
        if in_admin_only and line.strip().endswith("]",):
            in_admin_only = False

    assert found_permission, "manage_org_claims not found in adminOnly permissions array"


def test_manage_org_integration():
    """F2P: Verify GitConversationRouting is integrated into manage-org.tsx."""
    content = Path(MANAGE_ORG).read_text()

    # Check for import
    assert "GitConversationRouting" in content, "GitConversationRouting not imported or used"

    # Check for permission check
    assert "canManageOrgClaims" in content or "manage_org_claims" in content, \
        "Permission check for manage_org_claims not found"

    # Check for component rendering
    assert "<GitConversationRouting" in content, "GitConversationRouting component not rendered"


def test_typescript_compiles():
    """F2P: Verify TypeScript compilation succeeds with no errors."""
    try:
        result = subprocess.run(
            ["npx", "tsc", "--noEmit"],
            cwd=FRONTEND,
            capture_output=True,
            text=True,
            timeout=180,
        )

        # Check for errors related to our new files
        stderr = result.stderr or ""
        stdout = result.stdout or ""
        combined = stderr + stdout

        # Filter for errors in our new files
        relevant_errors = []
        for line in combined.split("\n"):
            if any(path in line for path in [
                "claim-button",
                "git-org-row",
                "git-conversation-routing",
                "use-git-conversation-routing",
            ]):
                relevant_errors.append(line)

        if relevant_errors:
            error_msg = "TypeScript errors in new files:\n" + "\n".join(relevant_errors[:10])
            assert False, error_msg

    except subprocess.TimeoutExpired:
        assert False, "TypeScript compilation timed out"
    except Exception as e:
        assert False, f"TypeScript compilation failed: {str(e)}"


def test_unit_tests_pass():
    """P2P: Verify the unit tests for new components pass (or no tests exist)."""
    test_patterns = [
        "claim-button",
        "git-org-row",
        "git-conversation-routing",
    ]

    # Check if test files exist for each component
    # If no test files exist, the test passes (no tests to run)
    # If test files exist, they must pass
    import glob

    test_base = f"{REPO}/frontend/__tests__"
    all_tests_found = True

    for pattern in test_patterns:
        # Look for test files matching the pattern
        test_files = glob.glob(f"{test_base}/**/*{pattern}*.test.*", recursive=True)
        if not test_files:
            # No test file found for this component - that's OK for P2P
            # The feature is new and may not have tests yet
            all_tests_found = False

    if not all_tests_found:
        # No tests found for new components - pass the test
        # This is acceptable for new features
        return

    # If tests exist, run them
    failures = []
    for pattern in test_patterns:
        success, output = run_npm_test(pattern, timeout=60)
        if not success:
            failures.append(f"Tests for '{pattern}' failed:\n{output[:500]}")

    if failures:
        assert False, "\n\n".join(failures[:3])


def test_component_exports_valid():
    """P2P: Verify component exports can be resolved."""
    # Check that our imports reference the correct paths
    hook_content = Path(HOOK).read_text() if os.path.exists(HOOK) else ""

    # Check GitOrg import in components
    for component_path in COMPONENTS.values():
        if os.path.exists(component_path):
            content = Path(component_path).read_text()
            # Should import GitOrg from the hook
            if "GitOrg" in content:
                assert "use-git-conversation-routing" in content, \
                    f"GitOrg imported but not from hook in {component_path}"


def test_repo_typecheck():
    """P2P: Repo TypeScript typecheck passes (react-router typegen && tsc)."""
    r = subprocess.run(
        ["npm", "run", "typecheck"],
        capture_output=True, text=True, timeout=600, cwd=FRONTEND,
    )
    assert r.returncode == 0, f"TypeScript typecheck failed:\n{r.stderr[-1000:]}{r.stdout[-500:]}"


def test_repo_build():
    """P2P: Repo production build passes (npm run build)."""
    r = subprocess.run(
        ["npm", "run", "build"],
        capture_output=True, text=True, timeout=600, cwd=FRONTEND,
    )
    assert r.returncode == 0, f"Production build failed:\n{r.stderr[-1000:]}{r.stdout[-500:]}"


def test_repo_translations():
    """P2P: Repo translation completeness check passes."""
    r = subprocess.run(
        ["npm", "run", "check-translation-completeness"],
        capture_output=True, text=True, timeout=120, cwd=FRONTEND,
    )
    assert r.returncode == 0, f"Translation check failed:\n{r.stderr[-500:]}{r.stdout[-500:]}"
