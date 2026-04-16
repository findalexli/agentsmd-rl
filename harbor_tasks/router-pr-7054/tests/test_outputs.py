"""
Tests for TanStack Router SSR OnRendered script removal fix.

PR: TanStack/router#7054
Issue: OnRendered component renders an extra empty <script></script> tag during SSR
Fix: Return null on server side instead of rendering the script tag
"""

import subprocess
import os
import re

REPO = "/workspace/router"


def test_ssr_scripts_test_passes():
    """
    The repo's Scripts.test.tsx SSR test should pass (fail_to_pass).

    This test verifies that the SSR output does not include an extra empty
    <script></script> tag that was previously rendered by the OnRendered component.
    """
    result = subprocess.run(
        [
            "pnpm", "nx", "run", "@tanstack/react-router:test:unit",
            "--", "tests/Scripts.test.tsx", "-t", "should inject scripts in order"
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )

    # The test checks that container.innerHTML equals expected string without extra script
    # If it fails, it means the extra <script></script> is still being rendered
    assert result.returncode == 0, (
        f"SSR scripts test failed - the OnRendered component may still be rendering "
        f"an extra script tag during SSR.\n"
        f"stdout: {result.stdout[-2000:]}\n"
        f"stderr: {result.stderr[-2000:]}"
    )


def test_onrendered_returns_null_on_server():
    """
    The OnRendered component should return null on the server (fail_to_pass).

    This test verifies that the Match.tsx file contains the server-side
    null return check that prevents the extra script tag from being rendered.
    """
    match_file = os.path.join(REPO, "packages/react-router/src/Match.tsx")

    with open(match_file, "r") as f:
        content = f.read()

    # The fix adds a server-side check that returns null
    # Pattern: if (isServer ?? router.isServer) { return null }
    server_null_pattern = r"if\s*\(\s*isServer\s*\?\?\s*router\.isServer\s*\)\s*\{\s*return\s+null"

    assert re.search(server_null_pattern, content), (
        "OnRendered component should check for server environment and return null. "
        "Expected pattern: if (isServer ?? router.isServer) { return null }"
    )


def test_onrendered_uses_layout_effect():
    """
    The OnRendered component should use useLayoutEffect on client (fail_to_pass).

    This test verifies that the fix properly uses useLayoutEffect instead of
    the script tag ref callback for firing onRendered events.
    """
    match_file = os.path.join(REPO, "packages/react-router/src/Match.tsx")

    with open(match_file, "r") as f:
        content = f.read()

    # The fix should import useLayoutEffect
    assert "useLayoutEffect" in content, (
        "Match.tsx should import and use useLayoutEffect for the OnRendered component"
    )

    # The fix should use useLayoutEffect to emit the onRendered event
    assert "useLayoutEffect(() =>" in content or "useLayoutEffect((" in content, (
        "OnRendered component should use useLayoutEffect to fire onRendered events"
    )


def test_onrendered_no_script_tag_rendering():
    """
    The OnRendered component should NOT render a script tag (fail_to_pass).

    This verifies that the OnRendered function no longer returns a <script> element.
    """
    match_file = os.path.join(REPO, "packages/react-router/src/Match.tsx")

    with open(match_file, "r") as f:
        content = f.read()

    # Find the OnRendered function and check it doesn't return a script element
    # The old code had: return ( <script key={...} ... /> )
    # The new code has: return null

    # Look for the OnRendered function definition
    onrendered_match = re.search(
        r"function\s+OnRendered\s*\([^)]*\)\s*\{([\s\S]*?)^\}",
        content,
        re.MULTILINE
    )

    assert onrendered_match, "Could not find OnRendered function definition"

    onrendered_body = onrendered_match.group(1)

    # The fixed version should NOT have <script in the OnRendered function body
    # (except in comments)
    # Remove comments before checking
    body_no_comments = re.sub(r'//.*$', '', onrendered_body, flags=re.MULTILINE)
    body_no_comments = re.sub(r'/\*[\s\S]*?\*/', '', body_no_comments)

    assert "<script" not in body_no_comments, (
        "OnRendered component should not render a <script> element. "
        "It should return null on server and use useLayoutEffect on client."
    )


def test_solid_router_onrendered_comment_updated():
    """
    The Solid Router OnRendered comment should be updated (fail_to_pass).

    The PR also updates the comment in solid-router to remove the reference
    to rendering a dummy DOM element.
    """
    solid_match_file = os.path.join(REPO, "packages/solid-router/src/Match.tsx")

    with open(solid_match_file, "r") as f:
        content = f.read()

    # The old comment mentioned "renders a dummy dom element"
    # The new comment does not mention this
    assert "renders a dummy dom element" not in content.lower(), (
        "Solid Router Match.tsx should have updated comments that don't mention "
        "'renders a dummy dom element'"
    )


def test_react_router_unit_tests_pass():
    """
    The react-router unit tests should pass (pass_to_pass).

    Ensures the fix doesn't break other functionality.
    """
    result = subprocess.run(
        [
            "pnpm", "nx", "run", "@tanstack/react-router:test:unit"
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )

    assert result.returncode == 0, (
        f"react-router unit tests failed.\n"
        f"stdout: {result.stdout[-2000:]}\n"
        f"stderr: {result.stderr[-2000:]}"
    )


def test_react_router_type_check_passes():
    """
    The react-router type check should pass (pass_to_pass).

    Verifies TypeScript compilation is successful.
    """
    result = subprocess.run(
        [
            "pnpm", "nx", "run", "@tanstack/react-router:test:types"
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )

    assert result.returncode == 0, (
        f"react-router type check failed.\n"
        f"stdout: {result.stdout[-2000:]}\n"
        f"stderr: {result.stderr[-2000:]}"
    )


def test_react_router_build_succeeds():
    """
    The react-router package should build successfully (pass_to_pass).
    """
    result = subprocess.run(
        [
            "pnpm", "nx", "run", "@tanstack/react-router:build", "--skip-nx-cache"
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )

    assert result.returncode == 0, (
        f"react-router build failed.\n"
        f"stdout: {result.stdout[-2000:]}\n"
        f"stderr: {result.stderr[-2000:]}"
    )


def test_solid_router_unit_tests_pass():
    """
    The solid-router unit tests should pass (pass_to_pass).

    The PR modifies solid-router/src/Match.tsx so we verify solid-router tests pass.
    """
    result = subprocess.run(
        [
            "pnpm", "nx", "run", "@tanstack/solid-router:test:unit"
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )

    assert result.returncode == 0, (
        f"solid-router unit tests failed.\n"
        f"stdout: {result.stdout[-2000:]}\n"
        f"stderr: {result.stderr[-2000:]}"
    )


def test_solid_router_type_check_passes():
    """
    The solid-router type check should pass (pass_to_pass).

    Verifies TypeScript compilation is successful for solid-router.
    """
    result = subprocess.run(
        [
            "pnpm", "nx", "run", "@tanstack/solid-router:test:types"
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )

    assert result.returncode == 0, (
        f"solid-router type check failed.\n"
        f"stdout: {result.stdout[-2000:]}\n"
        f"stderr: {result.stderr[-2000:]}"
    )


def test_solid_router_build_succeeds():
    """
    The solid-router package should build successfully (pass_to_pass).
    """
    result = subprocess.run(
        [
            "pnpm", "nx", "run", "@tanstack/solid-router:build", "--skip-nx-cache"
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )

    assert result.returncode == 0, (
        f"solid-router build failed.\n"
        f"stdout: {result.stdout[-2000:]}\n"
        f"stderr: {result.stderr[-2000:]}"
    )


def test_react_router_eslint_passes():
    """
    The react-router ESLint check should pass (pass_to_pass).

    This runs the repo's ESLint configuration on react-router.
    """
    result = subprocess.run(
        [
            "pnpm", "nx", "run", "@tanstack/react-router:test:eslint"
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )

    assert result.returncode == 0, (
        f"react-router ESLint check failed.\n"
        f"stdout: {result.stdout[-2000:]}\n"
        f"stderr: {result.stderr[-2000:]}"
    )


def test_solid_router_eslint_passes():
    """
    The solid-router ESLint check should pass (pass_to_pass).

    This runs the repo's ESLint configuration on solid-router.
    """
    result = subprocess.run(
        [
            "pnpm", "nx", "run", "@tanstack/solid-router:test:eslint"
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )

    assert result.returncode == 0, (
        f"solid-router ESLint check failed.\n"
        f"stdout: {result.stdout[-2000:]}\n"
        f"stderr: {result.stderr[-2000:]}"
    )
