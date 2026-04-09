#!/usr/bin/env python3
"""
Test that deprecated permalink tokens have been replaced with new tokens.

This tests:
1. :filename → :contentbasename in permalinks
2. :slugorfilename → :slugorcontentbasename in permalinks
3. .Site.Data → hugo.Data in templates

The tests verify both that the source code uses the new tokens and that
the Go tests pass with the updated code.
"""

import subprocess
import sys
from pathlib import Path

REPO = Path("/workspace/hugo")


def run_go_test(test_pattern: str, pkg: str = "./...", cwd: Path = REPO, timeout: int = 120) -> tuple[int, str, str]:
    """Run a Go test and return (exit_code, stdout, stderr)."""
    result = subprocess.run(
        ["go", "test", "-v", "-run", test_pattern, pkg],
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    return result.returncode, result.stdout, result.stderr


def test_permalink_tokens_updated():
    """
    Fail-to-pass: Verify that deprecated :filename token is replaced with :contentbasename.

    Checks multiple test files that were using the deprecated :filename token.
    """
    files_to_check = [
        ("hugolib/hugo_sites_multihost_test.go", ":contentbasename"),
        ("hugolib/page_test.go", ":contentbasename"),
        ("hugolib/pagebundler_test.go", ":slugorcontentbasename"),
        ("resources/page/permalinks_integration_test.go", ":contentbasename"),
    ]

    errors = []
    for filepath, expected_token in files_to_check:
        full_path = REPO / filepath
        if not full_path.exists():
            errors.append(f"File not found: {filepath}")
            continue

        content = full_path.read_text()

        # Check for the old deprecated token
        if ":filename" in content and ":contentbasename" not in content:
            errors.append(f"{filepath}: still uses deprecated :filename token")

        # Check for the new token (should be present after fix)
        if expected_token not in content:
            errors.append(f"{filepath}: missing expected token {expected_token}")

    if errors:
        raise AssertionError("Permalink token updates failed:\n" + "\n".join(errors))


def test_site_data_updated():
    """
    Fail-to-pass: Verify that .Site.Data is replaced with hugo.Data.

    This change was needed because .Site.Data was deprecated.
    """
    filepath = REPO / "hugolib/hugo_modules_test.go"
    content = filepath.read_text()

    # The old deprecated pattern should not be present
    if ".Site.Data" in content:
        raise AssertionError("hugolib/hugo_modules_test.go: still uses deprecated .Site.Data")

    # The new pattern should be present
    if "hugo.Data" not in content:
        raise AssertionError("hugolib/hugo_modules_test.go: missing hugo.Data")


def test_permalink_integration_tests_pass():
    """
    Pass-to-pass: Run the permalink integration tests to verify they pass.

    These tests verify that the permalink configuration works correctly
    with the new :contentbasename token.
    """
    # Run the specific permalink integration tests in resources/page package
    exit_code, stdout, stderr = run_go_test("TestPermalinks", pkg="./resources/page/...", timeout=180)

    if exit_code != 0:
        # Check if it's due to deprecation errors
        combined = stdout + stderr
        if ":filename" in combined or "deprecated" in combined.lower():
            raise AssertionError(
                f"Permalink tests failed due to deprecated tokens:\n{combined[:2000]}"
            )
        raise AssertionError(
            f"Permalink integration tests failed:\nstdout: {stdout[:1000]}\nstderr: {stderr[:1000]}"
        )


def test_pagebundler_tests_pass():
    """
    Pass-to-pass: Run the page bundler tests to verify they pass.

    Tests the :slugorcontentbasename token replacement.
    """
    exit_code, stdout, stderr = run_go_test("TestHTMLFilesIsue11999", pkg="./hugolib/...", timeout=180)

    if exit_code != 0:
        combined = stdout + stderr
        if ":slugorfilename" in combined:
            raise AssertionError(
                f"Page bundler tests failed due to deprecated :slugorfilename token:\n{combined[:2000]}"
            )
        raise AssertionError(
            f"Page bundler tests failed:\nstdout: {stdout[:1000]}\nstderr: {stderr[:1000]}"
        )


def test_multihost_tests_pass():
    """
    Pass-to-pass: Run the multihost tests to verify :contentbasename works.
    """
    exit_code, stdout, stderr = run_go_test("TestMultiHost", pkg="./hugolib/...", timeout=180)

    if exit_code != 0:
        combined = stdout + stderr
        if ":filename" in combined:
            raise AssertionError(
                f"Multihost tests failed due to deprecated :filename token:\n{combined[:2000]}"
            )
        raise AssertionError(
            f"Multihost tests failed:\nstdout: {stdout[:1000]}\nstderr: {stderr[:1000]}"
        )


def test_hugo_modules_data_access():
    """
    Pass-to-pass: Run the hugo modules tests to verify hugo.Data works.

    Tests the .Site.Data → hugo.Data replacement.
    """
    exit_code, stdout, stderr = run_go_test("TestMount", pkg="./hugolib/...", timeout=180)

    if exit_code != 0:
        combined = stdout + stderr
        if ".Site.Data" in combined:
            raise AssertionError(
                f"Hugo modules tests failed due to deprecated .Site.Data:\n{combined[:2000]}"
            )
        raise AssertionError(
            f"Hugo modules tests failed:\nstdout: {stdout[:1000]}\nstderr: {stderr[:1000]}"
        )


def test_page_path_tests_pass():
    """
    Pass-to-pass: Run page path tests with disablePathToLower and permalinks.
    """
    exit_code, stdout, stderr = run_go_test("TestPagePathDisablePathToLower", pkg="./hugolib/...", timeout=180)

    if exit_code != 0:
        combined = stdout + stderr
        if ":filename" in combined:
            raise AssertionError(
                f"Page path tests failed due to deprecated :filename token:\n{combined[:2000]}"
            )
        raise AssertionError(
            f"Page path tests failed:\nstdout: {stdout[:1000]}\nstderr: {stderr[:1000]}"
        )


def test_repo_go_build():
    """
    Pass-to-pass: Verify the repo builds successfully.

    This ensures the codebase compiles without errors on both base and fixed commits.
    """
    r = subprocess.run(
        ["go", "build", "./..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"Go build failed:\n{r.stderr[-1000:]}"


def test_repo_go_vet():
    """
    Pass-to-pass: Verify go vet passes without issues on key packages.

    This runs static analysis checks on packages relevant to the PR changes.
    """
    # Run go vet on specific packages that are relevant to the changes
    key_packages = [
        "./common/hugo/...",
        "./hugolib/...",
        "./resources/page/...",
    ]
    for pkg in key_packages:
        r = subprocess.run(
            ["go", "vet", pkg],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=60,
        )
        assert r.returncode == 0, f"Go vet failed for {pkg}:\n{r.stderr[-500:]}"


def test_repo_gofmt():
    """
    Pass-to-pass: Verify all Go files are properly formatted.

    This checks that gofmt doesn't report any formatting issues.
    """
    r = subprocess.run(
        ["gofmt", "-l", "."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    # gofmt -l returns a list of files that need formatting
    # Empty output means all files are properly formatted
    if r.stdout.strip():
        raise AssertionError(f"gofmt found formatting issues in:\n{r.stdout}")


if __name__ == "__main__":
    import pytest

    sys.exit(pytest.main([__file__, "-v"]))
