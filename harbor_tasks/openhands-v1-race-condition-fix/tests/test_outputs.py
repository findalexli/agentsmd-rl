"""Tests for OpenHands PR #13628: Fix V1 race condition in conversation creation."""

import subprocess
import re
import os

REPO = "/workspace/OpenHands/frontend"


# =============================================================================
# Pass-to-Pass Tests (verify repo CI/CD passes on base and after fix)
# =============================================================================

def test_repo_typecheck():
    """Repo's TypeScript typecheck passes (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "typecheck"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Typecheck failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


def test_repo_lint():
    """Repo's lint check passes (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "lint"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    # Allow warnings (exit code 0) but not errors
    assert r.returncode == 0, f"Lint failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


def test_repo_build():
    """Repo's production build passes (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "build"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Build failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


def test_repo_tests_relevant():
    """Tests for use-create-conversation pass (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "test", "--", "--run", "__tests__/hooks/mutation/use-create-conversation.test.tsx"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Relevant tests failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


def test_repo_tests_v1_conversation_service():
    """Tests for V1 conversation service pass (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "test", "--", "--run", "__tests__/api/v1-conversation-service.test.ts"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"V1 conversation service tests failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


def test_repo_tests_settings_related():
    """Tests for settings-related hooks pass (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "test", "--", "--run", "__tests__/hooks/mutation/use-save-settings.test.tsx"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Settings-related tests failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


def test_repo_tests_all_mutation_hooks():
    """All mutation hook tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "test", "--", "--run", "__tests__/hooks/mutation/"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Mutation hook tests failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


def test_repo_tests_all_query_hooks():
    """All query hook tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "test", "--", "--run", "__tests__/hooks/query/"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Query hook tests failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


# =============================================================================
# Fail-to-Pass Tests (verify the fix)
# =============================================================================


def test_default_settings_v1_enabled():
    """DEFAULT_SETTINGS.v1_enabled must be true (not false) to align with backend default."""
    with open(f"{REPO}/src/services/settings.ts", "r") as f:
        content = f.read()

    # Find the v1_enabled line in DEFAULT_SETTINGS
    v1_match = re.search(r"v1_enabled:\s*(true|false)", content)
    assert v1_match, "v1_enabled not found in settings.ts"
    v1_value = v1_match.group(1)
    assert v1_value == "true", f"v1_enabled should be 'true', but got '{v1_value}'"


def test_getSettingsQueryFn_exported():
    """getSettingsQueryFn must be exported from use-settings.ts for use in the mutation hook."""
    with open(f"{REPO}/src/hooks/query/use-settings.ts", "r") as f:
        content = f.read()

    # Check that getSettingsQueryFn is exported (not just declared as const)
    assert "export const getSettingsQueryFn" in content, \
        "getSettingsQueryFn must be exported from use-settings.ts"


def test_use_create_conversation_uses_ensureQueryData():
    """useCreateConversation must use ensureQueryData to wait for settings before deciding V0 vs V1."""
    with open(f"{REPO}/src/hooks/mutation/use-create-conversation.ts", "r") as f:
        content = f.read()

    # Check for ensureQueryData usage (the fix uses this to wait for settings)
    assert "ensureQueryData" in content, \
        "useCreateConversation must use ensureQueryData to wait for settings"

    # Check that it imports getSettingsQueryFn
    assert "getSettingsQueryFn" in content, \
        "useCreateConversation must import getSettingsQueryFn"

    # Check that it imports DEFAULT_SETTINGS for fallback
    assert "DEFAULT_SETTINGS" in content, \
        "useCreateConversation must import DEFAULT_SETTINGS for fallback"

    # Check that it doesn't use the old !!settings?.v1_enabled pattern
    assert "!!settings?.v1_enabled" not in content, \
        "Must not use !!settings?.v1_enabled which fails when settings is undefined"

    # Check that it uses proper nullish coalescing or fallback pattern
    assert "await queryClient.ensureQueryData" in content, \
        "Must await ensureQueryData to properly wait for settings"


def test_use_create_conversation_has_fallback():
    """useCreateConversation must have try/catch fallback to DEFAULT_SETTINGS."""
    with open(f"{REPO}/src/hooks/mutation/use-create-conversation.ts", "r") as f:
        content = f.read()

    # Check for try/catch block around ensureQueryData
    assert "try {" in content and "catch" in content, \
        "useCreateConversation must have try/catch around settings fetch"

    # Check that catch block falls back to DEFAULT_SETTINGS
    # Use a simpler pattern match that looks for the catch block setting settings to DEFAULT_SETTINGS
    assert "settings = DEFAULT_SETTINGS" in content, \
        "Catch block must fall back to DEFAULT_SETTINGS when settings fetch fails"


def test_use_create_conversation_uses_organizationId():
    """useCreateConversation must use organizationId from useSelectedOrganizationId."""
    with open(f"{REPO}/src/hooks/mutation/use-create-conversation.ts", "r") as f:
        content = f.read()

    # Check for useSelectedOrganizationId import and usage
    assert "useSelectedOrganizationId" in content, \
        "useCreateConversation must import useSelectedOrganizationId"

    assert "organizationId" in content, \
        "useCreateConversation must use organizationId"

    # Check that queryKey includes organizationId (should be in the form ["settings", organizationId])
    querykey_match = re.search(r'queryKey:\s*\[["\']settings["\'],\s*organizationId\]', content)
    assert querykey_match, \
        "queryKey must include organizationId for proper caching"


def test_use_create_conversation_imports():
    """useCreateConversation must import all required dependencies."""
    with open(f"{REPO}/src/hooks/mutation/use-create-conversation.ts", "r") as f:
        content = f.read()

    # Verify all required imports are present
    assert 'import { Provider, Settings } from "#/types/settings"' in content or \
           "import { Provider, Settings } from '#/types/settings'" in content, \
        "Missing Settings import from #/types/settings"

    assert 'import { getSettingsQueryFn } from "#/hooks/query/use-settings"' in content or \
           "import { getSettingsQueryFn } from '#/hooks/query/use-settings'" in content, \
        "Missing getSettingsQueryFn import from #/hooks/query/use-settings"

    assert 'import { DEFAULT_SETTINGS } from "#/services/settings"' in content or \
           "import { DEFAULT_SETTINGS } from '#/services/settings'" in content, \
        "Missing DEFAULT_SETTINGS import from #/services/settings"

    assert 'import { useSelectedOrganizationId } from "#/context/use-selected-organization"' in content or \
           "import { useSelectedOrganizationId } from '#/context/use-selected-organization'" in content, \
        "Missing useSelectedOrganizationId import from #/context/use-selected-organization"


def test_typescript_no_new_errors():
    """The fix must not introduce new TypeScript errors in modified files."""
    # We check for syntax errors that would indicate the fix is malformed
    # Path alias errors are environment issues, not fix issues

    files_to_check = [
        "src/services/settings.ts",
        "src/hooks/query/use-settings.ts",
        "src/hooks/mutation/use-create-conversation.ts"
    ]

    for filepath in files_to_check:
        full_path = f"{REPO}/{filepath}"
        with open(full_path, "r") as f:
            content = f.read()

        # Check for obvious syntax errors that would be introduced by the fix
        # Count braces to check for balance
        open_braces = content.count("{")
        close_braces = content.count("}")
        assert open_braces == close_braces, \
            f"{filepath}: Mismatched braces (open: {open_braces}, close: {close_braces})"

        open_parens = content.count("(")
        close_parens = content.count(")")
        assert open_parens == close_parens, \
            f"{filepath}: Mismatched parentheses (open: {open_parens}, close: {close_parens})"

        # Check for common fix patterns that indicate the change was made
        if filepath == "src/services/settings.ts":
            assert "v1_enabled: true" in content, \
                "settings.ts: v1_enabled should be true"

        if filepath == "src/hooks/mutation/use-create-conversation.ts":
            # Verify the fix patterns
            assert "ensureQueryData" in content, \
                "use-create-conversation.ts: ensureQueryData not found"
            assert "try {" in content and "catch" in content, \
                "use-create-conversation.ts: try/catch not found"


def test_use_create_conversation_structure():
    """Verify the useCreateConversation hook has the correct structure for the fix."""
    with open(f"{REPO}/src/hooks/mutation/use-create-conversation.ts", "r") as f:
        content = f.read()

    # Check that useSettings is NOT used (replaced by ensureQueryData pattern)
    assert "useSettings()" not in content, \
        "useSettings() should not be called directly - use ensureQueryData instead"

    # Check that the hook imports and uses useSelectedOrganizationId
    assert "useSelectedOrganizationId" in content, \
        "Must use useSelectedOrganizationId to get organization context"

    # Check for the proper useV1 logic (not !!settings?.v1_enabled)
    assert "settings.v1_enabled" in content, \
        "Must use settings.v1_enabled (not !!settings?.v1_enabled)"

    # Verify the mutation function exists
    assert "mutationFn:" in content, \
        "Mutation function should be defined"

    # Verify DEFAULT_SETTINGS is used as fallback (check directly in catch block area)
    # Look for the pattern where catch block assigns DEFAULT_SETTINGS
    assert "settings = DEFAULT_SETTINGS" in content, \
        "Catch block must set settings = DEFAULT_SETTINGS as fallback"


def test_repo_translation_completeness():
    """Translation completeness check passes (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "check-translation-completeness"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Translation completeness check failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


def test_repo_tests_organization_scoped_queries():
    """Tests for organization-scoped query hooks pass (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "test", "--", "--run", "__tests__/hooks/query/organization-scoped-queries.test.tsx"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Organization-scoped query tests failed:{r.stdout[-1000:]}{r.stderr[-500:]}"


def test_repo_tests_new_conversation_command():
    """Tests for use-new-conversation-command hook pass (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "test", "--", "--run", "__tests__/hooks/mutation/use-new-conversation-command.test.tsx"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"New conversation command tests failed:{r.stdout[-1000:]}{r.stderr[-500:]}"


def test_repo_prettier_check():
    """Prettier formatting check passes (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "prettier", "--check", "src/**/*.{ts,tsx}"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier check failed:{r.stdout[-500:]}{r.stderr[-500:]}"


def test_repo_tests_all_api():
    """All API service tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "test", "--", "--run", "__tests__/api/"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"API tests failed:{r.stdout[-1000:]}{r.stderr[-500:]}"
