#!/usr/bin/env python3
"""
Test outputs for OpenHands organization switch toast notification feature.
PR: All-Hands-AI/OpenHands#13598
"""

import json
import subprocess
import sys
from pathlib import Path

REPO = Path("/workspace/openhands")
FRONTEND = REPO / "frontend"


def run_npm_command(cmd, cwd=FRONTEND, timeout=120):
    """Helper to run npm commands."""
    result = subprocess.run(
        cmd,
        shell=True,
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=timeout
    )
    return result


def test_i18n_keys_exist():
    """F2P: i18n translation keys must exist in declaration and translation files."""
    # Check declaration.ts for the new i18n keys
    declaration_file = FRONTEND / "src" / "i18n" / "declaration.ts"
    content = declaration_file.read_text()

    assert "ORG$SWITCHED_TO_ORGANIZATION" in content, \
        "ORG$SWITCHED_TO_ORGANIZATION key missing from declaration.ts"
    assert "ORG$SWITCHED_TO_PERSONAL_WORKSPACE" in content, \
        "ORG$SWITCHED_TO_PERSONAL_WORKSPACE key missing from declaration.ts"


def test_i18n_translations_exist():
    """F2P: All 15 language translations must exist for both keys."""
    translation_file = FRONTEND / "src" / "i18n" / "translation.json"
    translations = json.loads(translation_file.read_text())

    # Check first key exists with all languages
    key1 = "ORG$SWITCHED_TO_ORGANIZATION"
    assert key1 in translations, f"{key1} missing from translations"

    expected_langs = ["en", "ja", "zh-CN", "zh-TW", "ko-KR", "no", "it",
                      "pt", "es", "ar", "fr", "tr", "de", "uk", "ca"]

    for lang in expected_langs:
        assert lang in translations[key1], \
            f"{key1} missing translation for {lang}"
        assert "{{name}}" in translations[key1][lang] or "{name}" in translations[key1][lang], \
            f"{key1}.{lang} missing {{name}} interpolation variable"

    # Check second key exists with all languages
    key2 = "ORG$SWITCHED_TO_PERSONAL_WORKSPACE"
    assert key2 in translations, f"{key2} missing from translations"

    for lang in expected_langs:
        assert lang in translations[key2], \
            f"{key2} missing translation for {lang}"


def test_use_switch_organization_imports_toast_handler():
    """F2P: use-switch-organization.ts must import displaySuccessToast."""
    hook_file = FRONTEND / "src" / "hooks" / "mutation" / "use-switch-organization.ts"
    content = hook_file.read_text()

    assert "displaySuccessToast" in content, \
        "use-switch-organization.ts must import and use displaySuccessToast"
    assert 'import { useTranslation }' in content or 'import {useTranslation}' in content, \
        "use-switch-organization.ts must import useTranslation for i18n"


def test_use_switch_organization_uses_i18n_keys():
    """F2P: use-switch-organization.ts must use the correct i18n keys."""
    hook_file = FRONTEND / "src" / "hooks" / "mutation" / "use-switch-organization.ts"
    content = hook_file.read_text()

    assert "ORG$SWITCHED_TO_ORGANIZATION" in content, \
        "use-switch-organization.ts must reference ORG$SWITCHED_TO_ORGANIZATION"
    assert "ORG$SWITCHED_TO_PERSONAL_WORKSPACE" in content, \
        "use-switch-organization.ts must reference ORG$SWITCHED_TO_PERSONAL_WORKSPACE"


def test_use_switch_organization_mutation_params():
    """F2P: useSwitchOrganization mutation must accept orgName and isPersonal params."""
    hook_file = FRONTEND / "src" / "hooks" / "mutation" / "use-switch-organization.ts"
    content = hook_file.read_text()

    # Check that mutation accepts object with orgId, orgName, isPersonal
    assert "orgName" in content, \
        "mutationFn must accept orgName parameter"
    assert "isPersonal" in content, \
        "mutationFn must accept isPersonal parameter"


def test_org_selector_passes_org_details():
    """F2P: org-selector.tsx must pass org name and is_personal flag to switchOrganization."""
    selector_file = FRONTEND / "src" / "components" / "features" / "org" / "org-selector.tsx"
    content = selector_file.read_text()

    # Check that it passes orgName
    assert "orgName:" in content or 'orgName' in content, \
        "org-selector must pass orgName to switchOrganization"

    # Check that it looks up the organization to get is_personal
    assert "is_personal" in content or "isPersonal" in content, \
        "org-selector must check is_personal flag when switching"


def test_org_selector_finds_org_by_id():
    """F2P: org-selector.tsx must find the organization by ID before switching."""
    selector_file = FRONTEND / "src" / "components" / "features" / "org" / "org-selector.tsx"
    content = selector_file.read_text()

    # Should be looking up the organization in the organizations array
    assert "organizations?.find" in content or "organizations.find" in content, \
        "org-selector must find the organization in the list before switching"


def test_org_selector_tests_include_toast_assertions():
    """F2P: org-selector tests must verify toast notifications are displayed."""
    test_file = FRONTEND / "__tests__" / "components" / "features" / "org" / "org-selector.test.tsx"
    content = test_file.read_text()

    # Check for displaySuccessToast spy
    assert "displaySuccessToast" in content, \
        "Tests must spy on and verify displaySuccessToast calls"

    # Check for specific toast message assertions
    assert "You have switched to organization:" in content, \
        "Tests must verify the organization switch toast message"
    assert "You have switched to your personal workspace." in content, \
        "Tests must verify the personal workspace switch toast message"


def test_org_selector_tests_cover_team_org():
    """F2P: Tests must cover switching to a team organization."""
    test_file = FRONTEND / "__tests__" / "components" / "features" / "org" / "org-selector.test.tsx"
    content = test_file.read_text()

    # Count test cases for team org switch
    team_tests = content.count("should display toast with organization name")
    assert team_tests >= 1, \
        "Must have at least one test for team organization switch toast"


def test_org_selector_tests_cover_personal_workspace():
    """F2P: Tests must cover switching to personal workspace."""
    test_file = FRONTEND / "__tests__" / "components" / "features" / "org" / "org-selector.test.tsx"
    content = test_file.read_text()

    # Count test cases for personal workspace switch
    personal_tests = content.count("should display toast for personal workspace")
    assert personal_tests >= 1, \
        "Must have at least one test for personal workspace switch toast"


def test_org_selector_test_accepts_params_in_translation():
    """F2P: Test translation mock must accept params for interpolated strings."""
    test_file = FRONTEND / "__tests__" / "components" / "features" / "org" / "org-selector.test.tsx"
    content = test_file.read_text()

    # Check that the mock t function accepts params
    assert "params?: Record<string, string>" in content, \
        "Test translation mock must accept params for string interpolation"
    assert "params?.name" in content or "params.name" in content, \
        "Test translation mock must handle name parameter"


def test_repo_unit_tests():
    """P2P: Repo unit tests for org-selector must pass."""
    result = run_npm_command("npm run test -- __tests__/components/features/org/org-selector.test.tsx --reporter=verbose", timeout=120)

    assert result.returncode == 0, \
        f"Org-selector unit tests failed:\n{result.stdout}\n{result.stderr}"


def test_repo_org_component_tests():
    """P2P: All org component tests must pass (pass_to_pass)."""
    result = run_npm_command("npm run test -- --run __tests__/components/features/org/", timeout=120)

    assert result.returncode == 0, \
        f"Org component tests failed:\n{result.stderr[-1000:]}"


def test_repo_mutation_hook_tests():
    """P2P: Mutation hook tests must pass (pass_to_pass)."""
    result = run_npm_command("npm run test -- --run __tests__/hooks/mutation/", timeout=120)

    assert result.returncode == 0, \
        f"Mutation hook tests failed:\n{result.stderr[-1000:]}"


def test_repo_lint():
    """P2P: Frontend linting must pass."""
    result = run_npm_command("npm run lint", timeout=120)

    assert result.returncode == 0, \
        f"Frontend linting failed:\n{result.stderr[-1000:]}"


def test_repo_typecheck():
    """P2P: Frontend type checking must pass."""
    result = run_npm_command("npm run typecheck", timeout=120)

    assert result.returncode == 0, \
        f"Frontend type check failed:\n{result.stderr[-1000:]}"


def test_i18n_completeness():
    """P2P: All translations must be complete."""
    result = run_npm_command("npm run check-translation-completeness", timeout=60)

    assert result.returncode == 0, \
        f"Translation completeness check failed:\n{result.stderr}"


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v", "--tb=short"]))
