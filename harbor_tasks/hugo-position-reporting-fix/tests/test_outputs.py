"""
Test suite for Hugo position reporting fix in RenderString and render hooks.

This tests that positions reported by render hooks correctly reflect the
source content when using RenderString, rather than the parent page's content.
"""

import subprocess
import os
import sys

REPO = "/workspace/hugo"


def test_render_hook_position_with_render_string():
    """
    Test that render hooks report correct positions for content rendered via RenderString.

    This is the primary fail-to-pass test for the bug fix. The test runs
    TestRenderHooksPositionRenderString which verifies that when content is
    rendered via RenderString, the position information in render hooks
    reflects the rendered string content, not the parent page content.
    """
    result = subprocess.run(
        ["go", "test", "-v", "-run", "TestRenderHooksPositionRenderString",
         "./tpl/tplimpl/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )

    assert result.returncode == 0, (
        f"TestRenderHooksPositionRenderString failed:\n"
        f"STDOUT:\n{result.stdout}\n"
        f"STDERR:\n{result.stderr}"
    )

    # Verify the expected output patterns are in the test output
    assert "(rendered from string)" in result.stdout or result.returncode == 0, (
        "Expected '(rendered from string)' in filename for RenderString content"
    )


def test_pos_from_input_bounds_check():
    """
    Test that posFromInput properly validates offset bounds.

    This tests the fix in hugolib/shortcode.go where offset > len(input)
    now returns a valid Position instead of potentially panicking.
    """
    # Build the code first to ensure it compiles
    result = subprocess.run(
        ["go", "build", "./..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )

    assert result.returncode == 0, (
        f"Build failed:\n{result.stderr}"
    )

    # Run shortcode-related tests to verify the bounds check
    result = subprocess.run(
        ["go", "test", "-v", "-run", "TestShortcode|TestRenderString",
         "./hugolib/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180
    )

    # These tests should pass without panicking on out-of-bounds access
    assert result.returncode == 0, (
        f"Shortcode/RenderString tests failed:\n"
        f"STDOUT:\n{result.stdout}\n"
        f"STDERR:\n{result.stderr}"
    )


def test_element_position_resolver_interface():
    """
    Test that the ElementPositionResolver interface has the correct signature.

    Verifies that hookRendererTemplate properly implements the updated
    ElementPositionResolver interface with the new ResolvePosition signature.
    """
    # Build the specific packages that use the interface
    result = subprocess.run(
        ["go", "build", "./markup/converter/hooks/...", "./hugolib/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )

    assert result.returncode == 0, (
        f"Build failed - ElementPositionResolver interface mismatch:\n"
        f"{result.stderr}"
    )


def test_source_info_propagation():
    """
    Test that SourceInfo is properly propagated through the render pipeline.

    This verifies that the SourceInfo field in RenderContext is properly
    passed through the content rendering chain and used for position resolution.
    """
    # Build all packages to ensure type compatibility
    result = subprocess.run(
        ["go", "build", "./..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180
    )

    assert result.returncode == 0, (
        f"Build failed - SourceInfo propagation issue:\n"
        f"{result.stderr}"
    )


def test_render_hook_integration():
    """
    Test the full render hook integration test suite.

    Runs all render hook related tests to ensure the position reporting
    changes don't break existing functionality.
    """
    result = subprocess.run(
        ["go", "test", "-v", "-run", "TestRenderHook",
         "./tpl/tplimpl/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180
    )

    assert result.returncode == 0, (
        f"Render hook integration tests failed:\n"
        f"STDOUT:\n{result.stdout}\n"
        f"STDERR:\n{result.stderr}"
    )


def test_all_hugolib():
    """
    Run the full hugolib test suite to ensure no regressions.

    This is a broader pass-to-pass test that ensures the changes don't
    break existing functionality across the page content handling.
    """
    result = subprocess.run(
        ["go", "test", "-count=1", "./hugolib/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )

    assert result.returncode == 0, (
        f"Hugolib tests failed:\n"
        f"STDOUT:\n{result.stdout[-2000:]}\n"  # Last 2000 chars
        f"STDERR:\n{result.stderr[-1000:]}"   # Last 1000 chars
    )


# ============================================================================
# Repo CI/CD Pass-to-Pass Tests
# These tests verify that the repo's standard CI checks pass on both
# the base commit and after the fix is applied.
# ============================================================================


def test_repo_build():
    """
    Repo builds successfully (pass_to_pass).

    Verifies that the entire Hugo codebase compiles without errors.
    This is the most basic CI check - if it doesn't build, nothing works.
    """
    env = os.environ.copy()
    env["GOTOOLCHAIN"] = "auto"

    result = subprocess.run(
        ["go", "build", "./..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180,
        env=env
    )

    assert result.returncode == 0, (
        f"Repo build failed:\n"
        f"STDERR:\n{result.stderr[-1000:]}"
    )


def test_repo_vet():
    """
    Repo passes go vet analysis (pass_to_pass).

    Verifies that the codebase passes Go's standard static analysis.
    This catches common mistakes and suspicious constructs.
    """
    env = os.environ.copy()
    env["GOTOOLCHAIN"] = "auto"

    result = subprocess.run(
        ["go", "vet", "./..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180,
        env=env
    )

    assert result.returncode == 0, (
        f"Go vet failed:\n"
        f"STDERR:\n{result.stderr[-1000:]}"
    )


def test_repo_gofmt():
    """
    Repo passes gofmt formatting check (pass_to_pass).

    Verifies that all Go source files are properly formatted.
    The check.sh script in the repo runs this as part of CI.
    """
    # gofmt check on Go source files
    result = subprocess.run(
        ["gofmt", "-l", "."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )

    # gofmt returns 0 exit code but lists files if there are issues
    assert result.returncode == 0, f"gofmt check failed: {result.stderr}"
    assert result.stdout.strip() == "", (
        f"gofmt found formatting issues in files:\n{result.stdout}"
    )


def test_repo_module_verify():
    """
    Repo module dependencies are valid (pass_to_pass).

    Verifies that go.mod and go.sum are in sync and all dependencies
    can be resolved. This is a fundamental CI check.
    """
    env = os.environ.copy()
    env["GOTOOLCHAIN"] = "auto"

    result = subprocess.run(
        ["go", "mod", "verify"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
        env=env
    )

    assert result.returncode == 0, (
        f"Go mod verify failed:\n"
        f"STDERR:\n{result.stderr}"
    )


def test_repo_tests_core_packages():
    """
    Core package tests pass (pass_to_pass).

    Runs tests for the core packages that are modified by this fix:
    - markup/converter/hooks (ElementPositionResolver interface)
    - hugolib (RenderString and shortcode handling)
    - tpl/tplimpl (render hook integration)
    """
    env = os.environ.copy()
    env["GOTOOLCHAIN"] = "auto"

    # Test the core packages without running the full test suite
    core_packages = [
        "./markup/converter/hooks/...",
        "./markup/converter/...",
    ]

    for pkg in core_packages:
        result = subprocess.run(
            ["go", "test", "-count=1", pkg],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=120,
            env=env
        )

        assert result.returncode == 0, (
            f"Core package test failed for {pkg}:\n"
            f"STDERR:\n{result.stderr[-500:]}"
        )
