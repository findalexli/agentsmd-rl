"""
Test suite for TanStack Router: Fix OnRendered SSR script tag removal.

Fail-to-pass tests verify the fix was applied correctly.
Pass-to-pass tests guard against regressions in unrelated functionality.
"""

import subprocess
import sys
import os
import shutil

REPO = "/workspace/router"


# =============================================================================
# FAIL-TO-PASS TESTS — fail on base commit, pass after the fix
# =============================================================================

def test_ssr_scripts_without_sentinel():
    """
    Verify SSR scripts output no longer contains the sentinel <script></script> tag.

    Patches the Scripts.test.tsx assertion to remove the expected sentinel tag,
    then runs vitest. On the base commit the component still injects the sentinel
    so the test fails; after the fix the component produces no sentinel and the
    test passes.
    """
    test_file = os.path.join(REPO, "packages/react-router/tests/Scripts.test.tsx")
    backup = test_file + ".f2p-backup"
    shutil.copy(test_file, backup)

    try:
        with open(test_file, "r") as f:
            content = f.read()
        # Remove the sentinel <script></script> from the expected HTML string
        content = content.replace(
            '<script></script><script src="script.js">',
            '<script src="script.js">',
        )
        with open(test_file, "w") as f:
            f.write(content)

        result = subprocess.run(
            [
                "pnpm", "nx", "run", "@tanstack/react-router:test:unit",
                "--", "tests/Scripts.test.tsx",
            ],
            cwd=REPO, capture_output=True, text=True, timeout=120,
        )

        assert result.returncode == 0, (
            f"Scripts test with corrected expectation failed.\n"
            f"stdout: {result.stdout[-600:]}\nstderr: {result.stderr[-600:]}"
        )
    finally:
        shutil.move(backup, test_file)


def test_match_tsx_no_script_suppress():
    """
    Verify OnRendered no longer renders a <script> tag with suppressHydrationWarning.

    Reads the Match.tsx source and asserts the old sentinel pattern is absent.
    """
    match_file = os.path.join(REPO, "packages/react-router/src/Match.tsx")
    with open(match_file, "r") as f:
        content = f.read()

    has_script_suppress = "<script" in content and "suppressHydrationWarning" in content
    assert not has_script_suppress, (
        "Match.tsx should not contain both <script and suppressHydrationWarning"
    )


def test_solid_comment_updated():
    """
    Verify solid-router Match.tsx comment was updated to describe the new approach.

    The old comment says the component "renders a dummy dom element"; the updated
    comment should indicate it needs to run after the route subtree has committed.
    """
    solid_file = os.path.join(REPO, "packages/solid-router/src/Match.tsx")
    with open(solid_file, "r") as f:
        content = f.read()

    assert ("needs to run" in content) or ("committed" in content), (
        "solid-router OnRendered comment should describe the new behavior"
    )


# =============================================================================
# PASS-TO-PASS TESTS — pass on both base and gold (regression guards)
# =============================================================================

def test_build_succeeds():
    """Build succeeds on both base and gold."""
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/react-router:build"],
        cwd=REPO, capture_output=True, text=True, timeout=180,
    )
    assert result.returncode == 0, f"Build failed:\n{result.stderr[-500:]}"


def test_eslint_passes():
    """ESLint passes on both base and gold."""
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/react-router:test:eslint"],
        cwd=REPO, capture_output=True, text=True, timeout=120,
    )
    assert result.returncode == 0, f"ESLint failed:\n{result.stderr[-500:]}"


def test_typescript_passes():
    """TypeScript type-check passes on both base and gold."""
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/react-router:test:types"],
        cwd=REPO, capture_output=True, text=True, timeout=120,
    )
    assert result.returncode == 0, f"TypeScript check failed:\n{result.stderr[-500:]}"


def test_solid_router_eslint_passes():
    """solid-router ESLint passes on both base and gold."""
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/solid-router:test:eslint"],
        cwd=REPO, capture_output=True, text=True, timeout=120,
    )
    assert result.returncode == 0, f"solid-router ESLint failed:\n{result.stderr[-500:]}"


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
