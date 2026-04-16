"""
Test outputs for Hugo PR #14602: Prefer early suffixes when media type matches.

This tests that when multiple templates differ only in their file extension
and both extensions are valid suffixes for the same media type,
the template with the earlier suffix in the media type's suffix list is preferred.
"""

import subprocess
import sys
import os

REPO = "/workspace/hugo"


def test_template_selection_first_media_type_suffix():
    """
    Issue #13877: Template selection should prefer earlier suffixes in media type list.

    This is a behavioral f2p test - it runs the Go test that verifies the fix.
    Without the fix, TestTemplateSelectionFirstMediaTypeSuffix does not exist
    and this test will fail.
    """
    # Run the specific test added in the PR
    r = subprocess.run(
        ["go", "test", "-v", "-run", "TestTemplateSelectionFirstMediaTypeSuffix", "./hugolib/"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )

    if r.returncode != 0:
        print(f"Test output:\n{r.stdout}")
        print(f"Test stderr:\n{r.stderr}")

    # Fail if no tests ran - the fix hasn't been applied yet
    assert "no tests to run" not in r.stdout.lower(), \
        "TestTemplateSelectionFirstMediaTypeSuffix does not exist - fix not applied"

    assert r.returncode == 0, f"TestTemplateSelectionFirstMediaTypeSuffix failed: {r.stderr[-1000:] if r.stderr else 'no error output'}"


def test_template_store_compiles():
    """
    The template store package should compile without errors.
    This verifies the fix compiles correctly.
    """
    r = subprocess.run(
        ["go", "build", "./tpl/tplimpl/"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )

    assert r.returncode == 0, f"tpl/tplimpl build failed:\n{r.stderr}"


def test_hugolib_package_tests():
    """
    The hugolib package tests should pass (pass-to-pass check).
    We run a subset of tests related to templates to verify the package works.
    """
    # Run template-related tests in hugolib (subset that's reasonably fast)
    r = subprocess.run(
        ["go", "test", "-run", "TestTemplate", "./hugolib/", "-timeout", "5m"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=320
    )

    assert r.returncode == 0, f"hugolib template tests failed:\n{r.stderr[-500:] if r.stderr else 'no error'}"


def test_repo_gofmt():
    """
    Repo code should be properly formatted with gofmt (pass_to_pass).
    This is a standard CI check for Go projects.
    """
    r = subprocess.run(
        ["./check_gofmt.sh"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )

    assert r.returncode == 0, f"gofmt check failed:\n{r.stdout[-500:] if r.stdout else ''}"


def test_repo_go_vet_tplimpl():
    """
    Go vet should pass on the tplimpl package (pass_to_pass).
    This is a static analysis check for common Go issues.
    """
    r = subprocess.run(
        ["go", "vet", "./tpl/tplimpl/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )

    assert r.returncode == 0, f"go vet failed:\n{r.stderr[-500:] if r.stderr else ''}"


def test_repo_tplimpl_tests():
    """
    All tests in the tplimpl package should pass (pass_to_pass).
    This covers the template implementation where the fix is applied.
    """
    r = subprocess.run(
        ["go", "test", "./tpl/tplimpl/...", "-timeout", "2m"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180
    )

    assert r.returncode == 0, f"tplimpl tests failed:\n{r.stderr[-500:] if r.stderr else 'no error'}"


if __name__ == "__main__":
    # Run all tests
    test_functions = [
        test_template_store_compiles,
        test_template_selection_first_media_type_suffix,
        test_hugolib_package_tests,
        test_repo_gofmt,
        test_repo_go_vet_tplimpl,
        test_repo_tplimpl_tests,
    ]

    failures = []
    for test_func in test_functions:
        try:
            print(f"Running {test_func.__name__}...")
            test_func()
            print(f"  ✓ PASSED")
        except AssertionError as e:
            print(f"  ✗ FAILED: {e}")
            failures.append((test_func.__name__, str(e)))
        except Exception as e:
            print(f"  ✗ ERROR: {e}")
            failures.append((test_func.__name__, f"Error: {e}"))

    if failures:
        print(f"\n{len(failures)} test(s) failed:")
        for name, error in failures:
            print(f"  - {name}: {error}")
        sys.exit(1)
    else:
        print(f"\nAll tests passed!")
        sys.exit(0)
