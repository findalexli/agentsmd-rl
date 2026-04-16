#!/usr/bin/env python3
"""
Test suite for Hugo permalink deprecation fix.
Tests that deprecated :filename and :slugorfilename tokens are replaced
with :contentbasename and :slugorcontentbasename.
"""

import subprocess
import sys

REPO = "/workspace/hugo"

def run_go_test(test_pattern, package="", cwd=REPO, timeout=120):
    """Run a Go test and return the result."""
    if package:
        cmd = ["go", "test", "-run", test_pattern, "-v", package]
    else:
        cmd = ["go", "test", "-run", test_pattern, "-v"]
    result = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=timeout
    )
    return result

def test_page_path_disable_path_to_lower():
    """
    TestPagePathDisablePathToLower should pass with :contentbasename instead of :filename.
    This is the primary fail-to-pass test for the deprecated :filename token.
    """
    result = run_go_test("TestPagePathDisablePathToLower", "./hugolib", timeout=60)

    # Check for deprecation error about :filename
    if ':filename" permalink token was deprecated' in result.stdout:
        assert False, "Test uses deprecated :filename token - needs to be updated to :contentbasename"

    # Check for deprecation error about :filename
    if ':filename" permalink token was deprecated' in result.stderr:
        assert False, "Test uses deprecated :filename token - needs to be updated to :contentbasename"

    assert result.returncode == 0, f"TestPagePathDisablePathToLower failed:\n{result.stdout[-2000:]}\n{result.stderr[-500:]}"

def test_page_bundler_slug_or_content_basename():
    """
    TestHTMLFilesIsue11999 should pass with :slugorcontentbasename instead of :slugorfilename.
    This is the primary fail-to-pass test for the deprecated :slugorfilename token.
    """
    result = run_go_test("TestHTMLFilesIsue11999", "./hugolib", timeout=60)

    # Check for deprecation error about :slugorfilename
    if ':slugorfilename" permalink token was deprecated' in result.stdout:
        assert False, "Test uses deprecated :slugorfilename token - needs to be updated to :slugorcontentbasename"

    if ':slugorfilename" permalink token was deprecated' in result.stderr:
        assert False, "Test uses deprecated :slugorfilename token - needs to be updated to :slugorcontentbasename"

    assert result.returncode == 0, f"TestHTMLFilesIsue11999 failed:\n{result.stdout[-2000:]}\n{result.stderr[-500:]}"

def test_multi_host_permalinks():
    """
    TestMultiHost should pass without deprecation errors.
    Tests that :contentbasename is used instead of :filename.
    """
    result = run_go_test("TestMultiHost", "./hugolib", timeout=120)

    # These tests pass even with deprecation warnings in some cases
    # But if there's a deprecation error (not warning), fail
    if 'ERROR deprecated' in result.stdout or 'ERROR deprecated' in result.stderr:
        assert False, "Test has deprecation errors - needs to use non-deprecated tokens"

    assert result.returncode == 0, f"TestMultiHost failed:\n{result.stdout[-2000:]}\n{result.stderr[-500:]}"

def test_check_sh_failfast_flag():
    """
    Verify check.sh contains -failfast flag in the test command.
    This is a structural check that validates the fix was applied.
    """
    with open(f"{REPO}/check.sh", "r") as f:
        content = f.read()

    # Check that -failfast is present in the go test command
    assert "-failfast" in content, "check.sh should use -failfast flag for go test"

    # Make sure it's in the right context
    assert "go test -failfast" in content or "go test -failfast $PACKAGES" in content, \
        "-failfast should be in the go test command"

def test_repo_go_build():
    """
    Repo should build successfully (pass-to-pass).
    """
    result = subprocess.run(
        ["go", "build", "-o", "/tmp/hugo", "."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"Build failed:\n{result.stderr[-500:]}"


def test_repo_go_vet_hugolib():
    """
    Go vet on hugolib package should pass (pass-to-pass).
    """
    result = subprocess.run(
        ["go", "vet", "./hugolib/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"go vet hugolib failed:\n{result.stderr[-500:]}"


def test_repo_go_vet_resources_page():
    """
    Go vet on resources/page package should pass (pass-to-pass).
    """
    result = subprocess.run(
        ["go", "vet", "./resources/page/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"go vet resources/page failed:\n{result.stderr[-500:]}"


def test_repo_gofmt_check():
    """
    Go fmt check should pass (pass-to-pass).
    """
    result = subprocess.run(
        ["bash", "-c", f"gofmt -l {REPO}/hugolib {REPO}/resources/page | head -5"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )
    assert result.stdout.strip() == "", f"gofmt found issues:\n{result.stdout}"


def test_repo_multihost_related_tests():
    """
    Related multihost tests that don't use deprecated tokens (pass-to-pass).
    """
    result = subprocess.run(
        ["go", "test", "-run", "TestMultihostResourcePerLanguageMultihostMinify|TestResourcePerLanguageIssue12163|TestMultihostResourceOneBaseURLWithSubPath", "-v", "./hugolib"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"Multihost related tests failed:\n{result.stderr[-500:]}"


def test_repo_permalinks_non_deprecated_tests():
    """
    Permalink tests that use non-deprecated tokens (pass-to-pass).
    """
    result = subprocess.run(
        ["go", "test", "-run", "TestPermalinksOldSetup|TestPermalinksContentbasenameWithAndWithoutFile|TestPermalinksUrlCascade", "-v", "./resources/page"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"Permalinks non-deprecated tests failed:\n{result.stderr[-500:]}"


def test_repo_permalinks_contentbasename_adapter():
    """
    Permalink contentbasename content adapter test (pass-to-pass).
    Tests :contentbasename and :slugorcontentbasename tokens with content adapter.
    """
    result = subprocess.run(
        ["go", "test", "-run", "TestPermalinksContentbasenameContentAdapter", "-v", "./resources/page"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"TestPermalinksContentbasenameContentAdapter failed:\n{result.stderr[-500:]}"


def test_repo_permalinks_nested_sections_slugs():
    """
    Permalink nested sections with slugs test (pass-to-pass).
    Tests permalinks with nested sections and slug configurations.
    """
    result = subprocess.run(
        ["go", "test", "-run", "TestPermalinksNestedSectionsWithSlugs", "-v", "./resources/page"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"TestPermalinksNestedSectionsWithSlugs failed:\n{result.stderr[-500:]}"


def test_repo_permalinks_escaped_colons():
    """
    Permalink escaped colons test (pass-to-pass).
    Tests permalinks with escaped colon patterns.
    """
    result = subprocess.run(
        ["go", "test", "-run", "TestPermalinksWithEscapedColons", "-v", "./resources/page"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"TestPermalinksWithEscapedColons failed:\n{result.stderr[-500:]}"


def test_repo_page_bundler_basic():
    """
    Page bundler basic tests (pass-to-pass).
    Tests core page bundler functionality.
    """
    result = subprocess.run(
        ["go", "test", "-run", "TestPageBundlerBasic|TestPageBundlerBundleInRoot|TestPageBundlerShortcodeInBundledPage", "-v", "./hugolib"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"Page bundler basic tests failed:\n{result.stderr[-500:]}"


def test_repo_hugo_info():
    """
    Hugo info tests (pass-to-pass).
    Tests Hugo info and version functionality from common/hugo.
    """
    result = subprocess.run(
        ["go", "test", "-run", "TestNewHugoInfo|TestHugoSites", "-v", "./common/hugo"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"Hugo info tests failed:\n{result.stderr[-500:]}"


def test_repo_page_permalink():
    """
    Page permalink tests (pass-to-pass).
    Tests permalink functionality in hugolib.
    """
    result = subprocess.run(
        ["go", "test", "-run", "TestPermalink|TestRelativeURLInFrontMatter", "-v", "./hugolib"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"Page permalink tests failed:\n{result.stderr[-500:]}"

def test_permalinks_integration_no_deprecation_errors():
    """
    Permalink integration tests should not have deprecation errors.
    Tests that :contentbasename is used instead of :filename in permalinks.
    """
    result = run_go_test("TestPermalinks", "./resources/page", timeout=120)

    # Check for deprecation errors
    if 'ERROR deprecated' in result.stdout or 'ERROR deprecated' in result.stderr:
        assert False, "Permalinks test has deprecation errors - needs to use :contentbasename"

    assert result.returncode == 0, f"TestPermalinks failed:\n{result.stdout[-2000:]}\n{result.stderr[-500:]}"

def test_permalinks_nested_sections_no_deprecation_errors():
    """
    Permalink nested sections tests should not have deprecation errors.
    Tests that :contentbasename is used instead of :filename in nested sections.
    """
    result = run_go_test("TestPermalinksNestedSections", "./resources/page", timeout=120)

    # Check for deprecation errors
    if 'ERROR deprecated' in result.stdout or 'ERROR deprecated' in result.stderr:
        assert False, "PermalinksNestedSections test has deprecation errors - needs to use :contentbasename"

    assert result.returncode == 0, f"TestPermalinksNestedSections failed:\n{result.stdout[-2000:]}\n{result.stderr[-500:]}"

if __name__ == "__main__":
    # Run all tests
    import pytest
    sys.exit(pytest.main([__file__, "-v", "--tb=short"]))
