"""
Test suite for payloadcms/payload#16117
Fix: admin.meta.title object form renders [object Object] in browser tab

The bug: When admin.meta.title is set to a Next.js TemplateString object like
{ default: 'Dashboard', template: '%s | Dashboard' }, the browser tab shows
"[object Object]" instead of properly rendering the title with suffix.

Tests verify that generateMetadata correctly handles:
1. String titles with titleSuffix
2. TemplateString objects (with default/template fields) with titleSuffix
3. TemplateString objects with absolute field with titleSuffix
4. OpenGraph title from TemplateString objects
"""

import subprocess
import sys
import os

REPO = "/workspace/payload"
META_SPEC = "packages/next/src/utilities/meta.spec.ts"


def test_meta_spec_file_exists():
    """The meta.spec.ts test file must exist after fix is applied."""
    path = os.path.join(REPO, META_SPEC)
    assert os.path.exists(path), f"Test file does not exist: {path}"


def test_generateMetadata_string_title_with_suffix():
    """String title with titleSuffix produces correct concatenated title."""
    # This is a fail-to-pass test that should FAIL on base commit (where join(' ') works for strings)
    # and PASS on fixed commit
    r = subprocess.run(
        ["pnpm", "vitest", "run", "--project", "unit", META_SPEC, "-t",
         "should handle a string title with titleSuffix"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    # On base commit, the test passes (string + suffix works with simple join)
    # On fixed commit, the test also passes (appendTitleSuffix handles strings)
    # So this is actually a pass-to-pass test - both pass
    # We need to verify the actual behavior
    assert r.returncode == 0, f"Test failed:\nstdout: {r.stdout[-1000:]}\nstderr: {r.stderr[-1000:]}"


def test_generateMetadata_templateString_default_and_template():
    """
    TemplateString title object with default and template fields gets titleSuffix applied to both.
    This is a FAIL-TO-PASS test: on base commit this test FAILS because the buggy join('[object Object]') is returned.
    """
    r = subprocess.run(
        ["pnpm", "vitest", "run", "--project", "unit", META_SPEC, "-t",
         "should apply titleSuffix to default and template fields"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    # On base commit: FAILS - the buggy code returns '[object Object] - My CMS'
    # On fixed commit: PASSES - appendTitleSuffix properly handles TemplateString
    assert r.returncode == 0, (
        f"TemplateString titleSuffix handling failed. "
        f"stdout: {r.stdout[-1000:]}\nstderr: {r.stderr[-1000:]}"
    )


def test_generateMetadata_ogTitle_from_templateString_default():
    """
    OpenGraph title uses TemplateString.default and appends titleSuffix.
    FAIL-TO-PASS: on base commit this FAILS because incomingMetadata.title object
    becomes '[object Object]' in the ogTitle string.
    """
    r = subprocess.run(
        ["pnpm", "vitest", "run", "--project", "unit", META_SPEC, "-t",
         "should use the TemplateString default for ogTitle"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, (
        f"OG title from TemplateString.default failed. "
        f"stdout: {r.stdout[-1000:]}\nstderr: {r.stderr[-1000:]}"
    )


def test_generateMetadata_ogTitle_from_templateString_absolute():
    """
    OpenGraph title uses TemplateString.absolute and appends titleSuffix.
    FAIL-TO-PASS: on base commit this FAILS.
    """
    r = subprocess.run(
        ["pnpm", "vitest", "run", "--project", "unit", META_SPEC, "-t",
         "should use the TemplateString absolute for ogTitle"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, (
        f"OG title from TemplateString.absolute failed. "
        f"stdout: {r.stdout[-1000:]}\nstderr: {r.stderr[-1000:]}"
    )


def test_generateMetadata_absolute_field_with_suffix():
    """
    TemplateString with absolute field gets titleSuffix applied to absolute.
    FAIL-TO-PASS: on base commit this FAILS.
    """
    r = subprocess.run(
        ["pnpm", "vitest", "run", "--project", "unit", META_SPEC, "-t",
         "should apply titleSuffix to the absolute field"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, (
        f"Absolute field titleSuffix handling failed. "
        f"stdout: {r.stdout[-1000:]}\nstderr: {r.stderr[-1000:]}"
    )


def test_generateMetadata_ogTitle_string_preference():
    """
    When openGraph.title is a string, it takes precedence for OG title over incomingMetadata.title.
    This is a PASS-TO-PASS test - works on both base and fixed commits.
    """
    r = subprocess.run(
        ["pnpm", "vitest", "run", "--project", "unit", META_SPEC, "-t",
         "should use openGraph.title string over incomingMetadata.title for ogTitle"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"OG title string preference failed:\n{r.stderr[-1000:]}"


def test_generateMetadata_no_title_no_suffix():
    """
    When no title and no titleSuffix are set, title is undefined.
    PASS-TO-PASS: works on both commits.
    """
    r = subprocess.run(
        ["pnpm", "vitest", "run", "--project", "unit", META_SPEC, "-t",
         "should return undefined for metaTitle when no title and no titleSuffix"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"No title case failed:\n{r.stderr[-1000:]}"


def test_generateMetadata_title_without_suffix():
    """
    When no titleSuffix is set, title is returned as-is.
    PASS-TO-PASS: works on both commits.
    """
    r = subprocess.run(
        ["pnpm", "vitest", "run", "--project", "unit", META_SPEC, "-t",
         "should return just the title when no titleSuffix"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"Title without suffix failed:\n{r.stderr[-1000:]}"


def test_appendTitleSuffix_function_exists():
    """
    The fixed code must contain the appendTitleSuffix helper function.
    This is a structural check that ensures the fix was applied.
    """
    meta_ts = os.path.join(REPO, "packages/next/src/utilities/meta.ts")
    with open(meta_ts, 'r') as f:
        content = f.read()
    assert "appendTitleSuffix" in content, (
        "appendTitleSuffix function not found in meta.ts - fix not applied"
    )


def test_getTitleString_function_exists():
    """
    The fixed code must contain the getTitleString helper function.
    This is a structural check that ensures the fix was applied.
    """
    meta_ts = os.path.join(REPO, "packages/next/src/utilities/meta.ts")
    with open(meta_ts, 'r') as f:
        content = f.read()
    assert "getTitleString" in content, (
        "getTitleString function not found in meta.ts - fix not applied"
    )


def test_repo_eslint_meta_ts():
    """Repo's linter passes on the modified meta.ts (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "eslint", "packages/next/src/utilities/meta.ts"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    # Exit code 0 means no errors (only warnings on base commit)
    assert r.returncode == 0, f"ESLint failed:\nstdout: {r.stdout[-500:]}\nstderr: {r.stderr[-500:]}"


def test_repo_vitest_next_package():
    """Repo's unit tests for @payloadcms/next package pass (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "vitest", "run", "--project", "unit", "packages/next"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, f"Vitest unit tests failed:\nstdout: {r.stdout[-1000:]}\nstderr: {r.stderr[-1000:]}"
