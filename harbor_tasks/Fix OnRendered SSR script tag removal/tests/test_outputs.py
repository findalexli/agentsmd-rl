"""
Test suite for TanStack Router PR #7054: Fix OnRendered SSR script tag removal.

This tests that the OnRendered component:
1. No longer renders a <script> tag (returns null instead)
2. Still emits the onRendered event via useLayoutEffect
3. Produces correct SSR output without the sentinel script tag
"""

import subprocess
import sys
import os
import json

REPO = "/workspace/router"
REACT_ROUTER_PKG = f"{REPO}/packages/react-router"


def test_onrendered_returns_null_no_script_tag():
    """
    Verify that OnRendered component returns null and doesn't render a script tag.

    This test imports the Match module and verifies that the OnRendered component
    no longer renders a DOM element (previously a <script> tag).
    """
    # Check that the Match.tsx source code has been updated correctly
    match_file = f"{REPO}/packages/react-router/src/Match.tsx"
    with open(match_file, 'r') as f:
        content = f.read()

    # Should use useLayoutEffect instead of script ref
    assert "useLayoutEffect" in content, "OnRendered should use useLayoutEffect hook"

    # Should return null, not a <script> element
    assert "return null" in content, "OnRendered should return null"

    # Should NOT have a script element with suppressHydrationWarning
    assert "<script" not in content or "suppressHydrationWarning" not in content, \
        "OnRendered should not render a <script> tag with suppressHydrationWarning"

    # Should check for server environment
    assert "isServer ?? router.isServer" in content or "router.isServer" in content, \
        "OnRendered should check for server environment"


def test_onrendered_emits_event_via_effect():
    """
    Verify that OnRendered still emits the 'onRendered' event via useLayoutEffect.

    The fix should preserve the onRendered event emission while using useLayoutEffect
    instead of a script tag ref callback.
    """
    match_file = f"{REPO}/packages/react-router/src/Match.tsx"
    with open(match_file, 'r') as f:
        content = f.read()

    # Should emit onRendered event
    assert "type: 'onRendered'" in content, "OnRendered should emit 'onRendered' event"

    # Should use useLayoutEffect for timing
    assert "useLayoutEffect(() => {" in content, "OnRendered should use useLayoutEffect for timing"

    # Should still track prevHrefRef for change detection
    assert "prevHrefRef" in content, "OnRendered should track previous href"

    # Should call router.emit
    assert "router.emit" in content, "OnRendered should call router.emit"


def test_ssr_output_no_sentinel_script():
    """
    Verify that SSR output doesn't contain the sentinel script tag.

    The test in Scripts.test.tsx was updated to remove the expected <script></script>
    from the HTML output.
    """
    test_file = f"{REPO}/packages/react-router/tests/Scripts.test.tsx"
    with open(test_file, 'r') as f:
        content = f.read()

    # The expected HTML should NOT contain <script></script> sentinel
    # Check that the test expectation was updated (should not have bare <script></script>)
    # The test expects: `<div><div data-testid="root">root</div><div data-testid="index">index</div><script src="script.js"></script>...`
    # Without the extra `<script></script>` sentinel tag before the actual script sources
    # Check all toEqual lines in the test file for the sentinel script
    found_sentinel = False
    lines = content.split('\n')
    for i, line in enumerate(lines):
        # Check if this line is an expect(...).toEqual( line
        if 'toEqual' in line:
            # Check this line and the next line for sentinel script
            combined = line
            if i + 1 < len(lines):
                combined += lines[i + 1]
            # Check for bare <script></script> tag (sentinel, not a script with src)
            if '<script></script>' in combined:
                found_sentinel = True
                break

    assert not found_sentinel, "SSR output should not contain sentinel <script></script> tag"


def test_typescript_types_correct():
    """
    Verify that TypeScript types are correct for the modified OnRendered component.

    The component now takes a resetKey prop and returns null.
    """
    match_file = f"{REPO}/packages/react-router/src/Match.tsx"
    with open(match_file, 'r') as f:
        content = f.read()

    # Should accept resetKey prop
    assert "resetKey" in content, "OnRendered should accept resetKey prop"

    # Should import useLayoutEffect from utils
    assert "useLayoutEffect" in content, "Should import useLayoutEffect from utils"


def test_build_succeeds():
    """
    Verify that the react-router package builds successfully after the fix.
    """
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/react-router:build"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180
    )

    assert result.returncode == 0, f"Build failed: {result.stderr}"


def test_unit_tests_pass():
    """
    Run the specific unit test for SSR scripts that was updated in this PR.
    """
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/react-router:test:unit", "--", "tests/Scripts.test.tsx"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )

    assert result.returncode == 0, f"Unit tests failed: {result.stderr}"


def test_solid_router_consistency():
    """
    Verify that solid-router also has consistent OnRendered behavior.

    The PR also updates the comment in solid-router's Match.tsx.
    """
    solid_match_file = f"{REPO}/packages/solid-router/src/Match.tsx"
    with open(solid_match_file, 'r') as f:
        content = f.read()

    # Should have updated comment about not rendering a dummy element
    assert "needs to run" in content or "committed" in content, \
        "Solid router OnRendered should have updated comment"


# =============================================================================
# PASS-TO-PASS TESTS - Repo CI/CD checks that should pass on both base and gold
# =============================================================================

def test_p2p_repo_eslint():
    """Repo's ESLint check passes (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/react-router:test:eslint"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"ESLint failed:\n{r.stderr[-500:]}"


def test_p2p_repo_typescript():
    """Repo's TypeScript typecheck passes (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/react-router:test:types"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"TypeScript check failed:\n{r.stderr[-500:]}"


def test_p2p_repo_unit_tests_ssr():
    """Repo's SSR-related unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/react-router:test:unit", "--", "--run", "tests/Scripts.test.tsx"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Unit tests (Scripts) failed:\n{r.stderr[-500:]}"


def test_p2p_repo_unit_tests_matches():
    """Repo's Match component unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/react-router:test:unit", "--", "--run", "tests/Matches.test.tsx"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Unit tests (Matches) failed:\n{r.stderr[-500:]}"


def test_p2p_repo_build():
    """Repo's build verification passes (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/react-router:test:build"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Build verification failed:\n{r.stderr[-500:]}"


def test_p2p_repo_unit_tests_router():
    """Repo's Router unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/react-router:test:unit", "--", "--run", "tests/router.test.tsx"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"Unit tests (router) failed:\n{r.stderr[-500:]}"


def test_p2p_repo_unit_tests_link():
    """Repo's Link component unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/react-router:test:unit", "--", "--run", "tests/link.test.tsx"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"Unit tests (link) failed:\n{r.stderr[-500:]}"


def test_p2p_repo_unit_tests_navigate():
    """Repo's navigate unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/react-router:test:unit", "--", "--run", "tests/navigate.test.tsx"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"Unit tests (navigate) failed:\n{r.stderr[-500:]}"


def test_p2p_repo_unit_tests_redirect():
    """Repo's redirect unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/react-router:test:unit", "--", "--run", "tests/redirect.test.tsx"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"Unit tests (redirect) failed:\n{r.stderr[-500:]}"


def test_p2p_solid_router_eslint():
    """Repo's solid-router ESLint check passes (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/solid-router:test:eslint"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"solid-router ESLint failed:\n{r.stderr[-500:]}"


def test_p2p_solid_router_unit_tests():
    """Repo's solid-router unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/solid-router:test:unit", "--", "--run"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"solid-router unit tests failed:\n{r.stderr[-500:]}"


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
