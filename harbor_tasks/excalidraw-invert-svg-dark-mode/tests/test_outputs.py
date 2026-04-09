"""
Tests for excalidraw dark mode SVG inversion fix.

This verifies that SVG images are properly inverted when rendered in dark mode,
both in canvas rendering and SVG export.
"""

import subprocess
import sys
import os

REPO = "/workspace/excalidraw"


def test_dark_theme_filter_constant_exists():
    """Verify DARK_THEME_FILTER constant is exported from common package."""
    result = subprocess.run(
        ["grep", "DARK_THEME_FILTER", f"{REPO}/packages/common/src/constants.ts"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, "DARK_THEME_FILTER not found in constants.ts"
    assert "invert(93%) hue-rotate(180deg)" in result.stdout, \
        "DARK_THEME_FILTER has incorrect value"


def test_render_element_imports_filter():
    """Verify renderElement.ts imports DARK_THEME_FILTER."""
    result = subprocess.run(
        ["grep", "DARK_THEME_FILTER", f"{REPO}/packages/element/src/renderElement.ts"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, "DARK_THEME_FILTER not used in renderElement.ts"
    # Check that it's imported from constants
    content = open(f"{REPO}/packages/element/src/renderElement.ts").read()
    assert "DARK_THEME_FILTER" in content


def test_render_element_has_dark_mode_check():
    """Verify canvas rendering checks for dark mode and SVG mime type."""
    content = open(f"{REPO}/packages/element/src/renderElement.ts").read()

    # Should check for dark theme
    assert "THEME.DARK" in content or 'theme === "dark"' in content, \
        "Missing dark theme check in renderElement.ts"

    # Should check for SVG mime type
    assert "MIME_TYPES.svg" in content, \
        "Missing SVG mime type check in renderElement.ts"

    # Should apply filter when both conditions are true
    assert "context.filter = DARK_THEME_FILTER" in content, \
        "Missing filter application in renderElement.ts"

    # Should save and restore context state
    assert "context.save()" in content, "Missing context.save() in renderElement.ts"
    assert "context.restore()" in content, "Missing context.restore() in renderElement.ts"


def test_static_svg_scene_imports_filter():
    """Verify staticSvgScene.ts imports DARK_THEME_FILTER."""
    result = subprocess.run(
        ["grep", "DARK_THEME_FILTER", f"{REPO}/packages/excalidraw/renderer/staticSvgScene.ts"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, "DARK_THEME_FILTER not used in staticSvgScene.ts"


def test_static_svg_scene_has_dark_mode_filter():
    """Verify SVG export applies dark mode filter to SVG images."""
    content = open(f"{REPO}/packages/excalidraw/renderer/staticSvgScene.ts").read()

    # Should check for dark theme
    assert "THEME.DARK" in content or 'theme === "dark"' in content, \
        "Missing dark theme check in staticSvgScene.ts"

    # Should check for SVG mime type
    assert "MIME_TYPES.svg" in content, \
        "Missing SVG mime type check in staticSvgScene.ts"

    # Should set filter attribute on g element
    assert 'g.setAttribute("filter"' in content, \
        "Missing filter attribute setting in staticSvgScene.ts"

    # Should use DARK_THEME_FILTER value
    assert "DARK_THEME_FILTER" in content, \
        "Should use DARK_THEME_FILTER constant in staticSvgScene.ts"


def test_static_svg_scene_imports_mime_types():
    """Verify staticSvgScene.ts imports MIME_TYPES."""
    content = open(f"{REPO}/packages/excalidraw/renderer/staticSvgScene.ts").read()
    assert "MIME_TYPES" in content, "MIME_TYPES not imported in staticSvgScene.ts"


def test_typescript_compiles():
    """Verify TypeScript compiles without errors."""
    result = subprocess.run(
        ["yarn", "test:typecheck"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"TypeScript compilation failed:\n{result.stdout}\n{result.stderr}"


def test_repo_typecheck():
    """Repo's TypeScript typecheck passes (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "test:typecheck"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Typecheck failed:\n{r.stderr[-500:]}"


def test_repo_lint():
    """Repo's ESLint check passes (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "test:code"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Lint check failed:\n{r.stderr[-500:]}"


def test_repo_prettier():
    """Repo's Prettier formatting check passes (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "test:other"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier check failed:\n{r.stderr[-500:]}"


def test_repo_unit_element():
    """Repo's element package unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "test:app", "--watch=false", "packages/element"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Element package tests failed:\n{r.stderr[-500:]}"


def test_repo_unit_excalidraw():
    """Repo's excalidraw package unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "test:app", "--watch=false", "packages/excalidraw"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Excalidraw package tests failed:\n{r.stderr[-500:]}"


def test_distinctive_line_pattern():
    """
    Verify the specific implementation pattern from the fix:
    context.filter = DARK_THEME_FILTER in the image rendering case.
    """
    content = open(f"{REPO}/packages/element/src/renderElement.ts").read()

    # This is the distinctive pattern from the gold patch
    assert "context.filter = DARK_THEME_FILTER" in content, \
        "Missing the key fix: context.filter = DARK_THEME_FILTER in renderElement.ts"


def test_filter_only_applied_to_svgs_in_dark_mode():
    """
    Verify the logic correctly restricts filter application:
    Only SVGs AND only in dark mode.
    """
    content = open(f"{REPO}/packages/element/src/renderElement.ts").read()

    # Look for the combined condition pattern
    # The fix uses: renderConfig.theme === THEME.DARK && cacheEntry?.mimeType === MIME_TYPES.svg
    has_theme_check = "THEME.DARK" in content
    has_mime_check = "MIME_TYPES.svg" in content

    assert has_theme_check, "Missing THEME.DARK check"
    assert has_mime_check, "Missing MIME_TYPES.svg check"

    # Verify the specific combined condition exists
    # The fix creates shouldInvertImage with both conditions
    assert "shouldInvertImage" in content, "Missing shouldInvertImage variable"
    assert "renderConfig.theme === THEME.DARK &&" in content, \
        "Missing THEME.DARK in combined condition"
    assert "cacheEntry?.mimeType === MIME_TYPES.svg" in content, \
        "Missing MIME_TYPES.svg check with cacheEntry"
    assert "if (shouldInvertImage)" in content, \
        "Missing gated if block for shouldInvertImage"
    assert "context.filter = DARK_THEME_FILTER" in content, \
        "Missing filter application in shouldInvertImage block"


def test_svg_export_filter_only_for_svgs():
    """
    Verify SVG export also correctly filters by mime type.
    """
    content = open(f"{REPO}/packages/excalidraw/renderer/staticSvgScene.ts").read()

    # Should have both checks near each other in the SVG export
    has_theme_check = "THEME.DARK" in content
    has_mime_check = "MIME_TYPES.svg" in content
    has_filter_set = 'g.setAttribute("filter"' in content

    assert has_theme_check, "Missing THEME.DARK check in SVG export"
    assert has_mime_check, "Missing MIME_TYPES.svg check in SVG export"
    assert has_filter_set, "Missing filter attribute setting in SVG export"
