#!/usr/bin/env python3
"""Tests for OpenHands PR #13606: LoginCTA with source prop for device verify."""

import subprocess
import sys
import os

REPO = "/workspace/openhands"
FRONTEND = f"{REPO}/frontend"


def test_login_cta_has_source_prop():
    """LoginCTA component should accept source prop with device_verify option."""
    login_cta_path = f"{FRONTEND}/src/components/features/auth/login-cta.tsx"
    content = open(login_cta_path).read()

    # Check for LoginCTAProps type definition
    assert "type LoginCTAProps" in content, "Missing LoginCTAProps type"
    assert 'source?: "login_page" | "device_verify"' in content, "Missing source prop type"

    # Check for ENTERPRISE_URL constant
    assert 'ENTERPRISE_URL = "https://openhands.dev/enterprise"' in content, "Missing ENTERPRISE_URL constant"

    # Check for conditional rendering based on source
    assert "isDeviceVerifySource" in content, "Missing isDeviceVerifySource logic"
    assert "Use <a> for external destination" in content, "Missing comment about external <a> tag usage"


def test_login_cta_renders_external_link_for_device_verify():
    """LoginCTA should render external <a> tag with enterprise URL when source=device_verify."""
    login_cta_path = f"{FRONTEND}/src/components/features/auth/login-cta.tsx"
    content = open(login_cta_path).read()

    # Check for external link attributes
    assert 'href={ENTERPRISE_URL}' in content, "Missing href to enterprise URL"
    assert 'target="_blank"' in content, "Missing target=_blank for external link"
    assert 'rel="noopener noreferrer"' in content, "Missing rel=noopener noreferrer"

    # Check for conditional rendering
    assert "isDeviceVerifySource ? (" in content, "Missing conditional for device verify source"
    assert '<a' in content and '</a>' in content, "Missing <a> tag for external link"


def test_device_verify_uses_login_cta():
    """Device verify page should import and use LoginCTA instead of EnterpriseBanner."""
    device_verify_path = f"{FRONTEND}/src/routes/device-verify.tsx"
    content = open(device_verify_path).read()

    # Check for LoginCTA import
    assert 'import { LoginCTA } from "#/components/features/auth/login-cta"' in content, \
        "Missing LoginCTA import in device-verify.tsx"

    # Check that EnterpriseBanner import is removed (not checking variable name which may still exist)
    assert "#/components/features/device-verify/enterprise-banner" not in content, \
        "EnterpriseBanner import should be removed from device-verify.tsx"
    assert "<EnterpriseBanner" not in content, \
        "EnterpriseBanner component should not be used in device-verify.tsx"


def test_device_verify_passes_correct_props():
    """Device verify page should pass source='device_verify' and stretch className."""
    device_verify_path = f"{FRONTEND}/src/routes/device-verify.tsx"
    content = open(device_verify_path).read()

    # Check for LoginCTA with source prop
    assert 'source="device_verify"' in content, "Missing source='device_verify' prop"
    assert 'className="lg:self-stretch"' in content, "Missing lg:self-stretch className"


def test_layout_classes_updated():
    """Layout classes should support stretching cards to equal height."""
    device_verify_path = f"{FRONTEND}/src/routes/device-verify.tsx"
    content = open(device_verify_path).read()

    # Check for lg:items-stretch class
    assert "lg:items-stretch" in content, "Missing lg:items-stretch for flex container"

    # Check for rounded-2xl and border-[#242424] on card
    assert "rounded-2xl" in content, "Missing rounded-2xl class"
    assert "border-[#242424]" in content, "Missing border-[#242424] class"


def test_repo_frontend_tests():
    """Repo's frontend unit tests for LoginCTA and device-verify should pass (pass_to_pass)."""
    # Run only specific tests related to this PR to save time
    result = subprocess.run(
        [
            "npm", "run", "test", "--", "--run", "--reporter=dot",
            "-t", "LoginCTA",
        ],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=180,
    )
    assert result.returncode == 0, f"LoginCTA tests failed:\n{result.stdout[-2000:]}\n{result.stderr[-1000:]}"


def test_repo_lint():
    """Repo's frontend linter should pass (pass_to_pass)."""
    result = subprocess.run(
        ["npm", "run", "lint"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"Lint failed:\n{result.stdout[-1000:]}\n{result.stderr[-1000:]}"


def test_repo_typescript_compile():
    """TypeScript typecheck should succeed (pass_to_pass)."""
    # Use npm run typecheck which includes react-router typegen + tsc
    result = subprocess.run(
        ["npm", "run", "typecheck"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"TypeScript typecheck failed:\n{result.stderr[-1500:]}"


def test_repo_build():
    """Frontend production build should succeed (pass_to_pass)."""
    result = subprocess.run(
        ["npm", "run", "build"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=180,
    )
    assert result.returncode == 0, f"Build failed:\n{result.stdout[-1500:]}\n{result.stderr[-1000:]}"


def test_repo_translation_completeness():
    """Translation completeness check should pass (pass_to_pass)."""
    result = subprocess.run(
        ["npm", "run", "check-translation-completeness"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, f"Translation check failed:\n{result.stderr[-1000:]}"


def test_repo_tests_login_cta():
    """LoginCTA and device-verify specific tests should pass (pass_to_pass)."""
    # Run only tests directly related to the PR changes for faster feedback
    result = subprocess.run(
        [
            "npm", "run", "test", "--", "--run",
            "__tests__/components/features/auth/login-cta.test.tsx",
            "__tests__/routes/device-verify.test.tsx",
        ],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"LoginCTA/device-verify tests failed:\n{result.stdout[-2000:]}\n{result.stderr[-1000:]}"


def test_repo_prettier_format():
    """Frontend code formatting should follow Prettier rules (pass_to_pass)."""
    # Check Prettier formatting on source files
    result = subprocess.run(
        ["npx", "prettier", "--check", "src/**/*.{ts,tsx}"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, f"Prettier format check failed:\n{result.stderr[-1000:]}"


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v", "--tb=short"]))
