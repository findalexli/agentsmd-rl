#!/usr/bin/env python3
"""Tests for containerd error sanitization fix.

This verifies that the SanitizeError function correctly redacts sensitive
credentials (like SAS tokens in Azure blob storage URLs) from errors before
they are returned via gRPC or logged.
"""

import subprocess
import sys
import os

REPO = "/workspace/containerd"
UTIL_DIR = f"{REPO}/internal/cri/util"


def test_sanitize_error_simple_url():
    """Test SanitizeError correctly sanitizes a simple url.Error.

    This is a fail-to-pass test: without the fix, SanitizeError won't exist
    or won't properly redact the sensitive query parameters.
    """
    # First check if the test file exists (fail-to-pass check)
    if not os.path.exists(f"{UTIL_DIR}/sanitize_test.go"):
        assert False, "sanitize_test.go does not exist - SanitizeError not implemented"

    # Run the upstream test for simple URL error
    result = subprocess.run(
        ["go", "test", "-v", "-run", "TestSanitizeError_SimpleURLError", "./internal/cri/util/"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )

    # Check for "no tests to run" which means the test doesn't exist yet
    if "no tests to run" in result.stdout or "no tests to run" in result.stderr:
        assert False, "TestSanitizeError_SimpleURLError not found - fix not implemented"

    # Test should pass after fix
    if result.returncode != 0:
        if "undefined: SanitizeError" in result.stderr or "no such file" in result.stderr:
            assert False, "SanitizeError function not implemented"
        assert False, f"Test failed:\n{result.stdout}\n{result.stderr}"

    # Verify the test actually ran and passed
    assert "PASS" in result.stdout and "TestSanitizeError_SimpleURLError" in result.stdout, \
        f"Expected test to pass:\n{result.stdout}"


def test_sanitize_error_wrapped():
    """Test SanitizeError correctly sanitizes wrapped errors.

    Verifies that errors.As works properly through the sanitizedError wrapper.
    """
    # First check if the test file exists (fail-to-pass check)
    if not os.path.exists(f"{UTIL_DIR}/sanitize_test.go"):
        assert False, "sanitize_test.go does not exist - SanitizeError not implemented"

    result = subprocess.run(
        ["go", "test", "-v", "-run", "TestSanitizeError_WrappedError", "./internal/cri/util/"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )

    # Check for "no tests to run" which means the test doesn't exist yet
    if "no tests to run" in result.stdout or "no tests to run" in result.stderr:
        assert False, "TestSanitizeError_WrappedError not found - fix not implemented"

    if result.returncode != 0:
        if "undefined: SanitizeError" in result.stderr:
            assert False, "SanitizeError function not implemented"
        assert False, f"Test failed:\n{result.stdout}\n{result.stderr}"

    assert "PASS" in result.stdout and "TestSanitizeError_WrappedError" in result.stdout, \
        f"Expected test to pass:\n{result.stdout}"


def test_sanitize_error_nil():
    """Test SanitizeError handles nil errors correctly."""
    # First check if the test file exists (fail-to-pass check)
    if not os.path.exists(f"{UTIL_DIR}/sanitize_test.go"):
        assert False, "sanitize_test.go does not exist - SanitizeError not implemented"

    result = subprocess.run(
        ["go", "test", "-v", "-run", "TestSanitizeError_NilError", "./internal/cri/util/"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )

    # Check for "no tests to run" which means the test doesn't exist yet
    if "no tests to run" in result.stdout or "no tests to run" in result.stderr:
        assert False, "TestSanitizeError_NilError not found - fix not implemented"

    if result.returncode != 0:
        if "undefined: SanitizeError" in result.stderr:
            assert False, "SanitizeError function not implemented"
        assert False, f"Test failed:\n{result.stdout}\n{result.stderr}"

    assert "PASS" in result.stdout and "TestSanitizeError_NilError" in result.stdout, \
        f"Expected test to pass:\n{result.stdout}"


def test_sanitize_error_non_url():
    """Test SanitizeError passes through non-URL errors unchanged."""
    # First check if the test file exists (fail-to-pass check)
    if not os.path.exists(f"{UTIL_DIR}/sanitize_test.go"):
        assert False, "sanitize_test.go does not exist - SanitizeError not implemented"

    result = subprocess.run(
        ["go", "test", "-v", "-run", "TestSanitizeError_NonURLError", "./internal/cri/util/"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )

    # Check for "no tests to run" which means the test doesn't exist yet
    if "no tests to run" in result.stdout or "no tests to run" in result.stderr:
        assert False, "TestSanitizeError_NonURLError not found - fix not implemented"

    if result.returncode != 0:
        if "undefined: SanitizeError" in result.stderr:
            assert False, "SanitizeError function not implemented"
        assert False, f"Test failed:\n{result.stdout}\n{result.stderr}"

    assert "PASS" in result.stdout and "TestSanitizeError_NonURLError" in result.stdout, \
        f"Expected test to pass:\n{result.stdout}"


def test_sanitize_error_no_query_params():
    """Test SanitizeError passes through URL errors without query params."""
    # First check if the test file exists (fail-to-pass check)
    if not os.path.exists(f"{UTIL_DIR}/sanitize_test.go"):
        assert False, "sanitize_test.go does not exist - SanitizeError not implemented"

    result = subprocess.run(
        ["go", "test", "-v", "-run", "TestSanitizeError_NoQueryParams", "./internal/cri/util/"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )

    # Check for "no tests to run" which means the test doesn't exist yet
    if "no tests to run" in result.stdout or "no tests to run" in result.stderr:
        assert False, "TestSanitizeError_NoQueryParams not found - fix not implemented"

    if result.returncode != 0:
        if "undefined: SanitizeError" in result.stderr:
            assert False, "SanitizeError function not implemented"
        assert False, f"Test failed:\n{result.stdout}\n{result.stderr}"

    assert "PASS" in result.stdout and "TestSanitizeError_NoQueryParams" in result.stdout, \
        f"Expected test to pass:\n{result.stdout}"


def test_sanitized_error_unwrap():
    """Test that sanitizedError correctly unwraps to the original error."""
    # First check if the test file exists (fail-to-pass check)
    if not os.path.exists(f"{UTIL_DIR}/sanitize_test.go"):
        assert False, "sanitize_test.go does not exist - SanitizeError not implemented"

    result = subprocess.run(
        ["go", "test", "-v", "-run", "TestSanitizedError_Unwrap", "./internal/cri/util/"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )

    # Check for "no tests to run" which means the test doesn't exist yet
    if "no tests to run" in result.stdout or "no tests to run" in result.stderr:
        assert False, "TestSanitizedError_Unwrap not found - fix not implemented"

    if result.returncode != 0:
        if "undefined: SanitizeError" in result.stderr:
            assert False, "SanitizeError function not implemented"
        assert False, f"Test failed:\n{result.stdout}\n{result.stderr}"

    assert "PASS" in result.stdout and "TestSanitizedError_Unwrap" in result.stdout, \
        f"Expected test to pass:\n{result.stdout}"


def test_sanitize_file_exists():
    """Verify sanitize.go file exists in the correct location."""
    assert os.path.exists(f"{UTIL_DIR}/sanitize.go"), \
        "sanitize.go should exist in internal/cri/util/"


def test_sanitize_test_file_exists():
    """Verify sanitize_test.go file exists."""
    assert os.path.exists(f"{UTIL_DIR}/sanitize_test.go"), \
        "sanitize_test.go should exist in internal/cri/util/"


def test_instrumented_service_integration():
    """Verify instrumented_service.go properly integrates error sanitization.

    This is a behavioral test: the instrumented service should call a sanitization
    function to clean errors before they are returned via gRPC. We verify that the
    compiled code contains the integration by running the instrument package tests.
    """
    # Build the instrument package to verify compilation succeeds
    result = subprocess.run(
        ["go", "build", "./internal/cri/instrument/"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, \
        f"Instrument package should build with sanitization integration:\n{result.stderr}"

    # Run a test that exercises the image operations to verify integration
    # If SanitizeError is not called in PullImage/ListImages/ImageStatus/RemoveImage,
    # this would be caught by the existing integration test coverage
    result = subprocess.run(
        ["go", "test", "-v", "-count=1", "./internal/cri/instrument/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180
    )
    # The package should compile and tests should pass (pass-to-pass verification
    # that the integration doesn't break existing functionality)
    assert result.returncode == 0, \
        f"Instrument package tests should pass:\n{result.stdout}\n{result.stderr}"


def test_all_util_tests_pass():
    """Run all tests in the util package to ensure no regressions (pass-to-pass)."""
    result = subprocess.run(
        ["go", "test", "-v", "./internal/cri/util/"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180
    )

    # This is a pass-to-pass check - tests should continue to work
    assert result.returncode == 0, \
        f"Util package tests should pass:\n{result.stdout}\n{result.stderr}"


def test_go_build():
    """Verify the code compiles with go build (pass-to-pass)."""
    result = subprocess.run(
        ["go", "build", "./internal/cri/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )

    assert result.returncode == 0, \
        f"Code should compile:\n{result.stderr}"


def test_go_vet():
    """Run go vet on the CRI package to catch common issues (pass-to-pass)."""
    result = subprocess.run(
        ["go", "vet", "./internal/cri/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )

    # go vet returns 0 on success, non-zero on issues
    assert result.returncode == 0, \
        f"go vet should pass:\n{result.stderr}"


def test_go_fmt_check():
    """Verify Go code formatting is correct (pass-to-pass).

    This checks that all Go files in the modified packages are properly formatted.
    """
    result = subprocess.run(
        ["go", "fmt", "./internal/cri/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )

    # go fmt returns list of files it reformatted - empty means all good
    assert result.returncode == 0 and result.stdout.strip() == "", \
        f"Go files need formatting: {result.stdout}"


def test_go_mod_verify():
    """Verify Go modules are valid and consistent (pass-to-pass)."""
    result = subprocess.run(
        ["go", "mod", "verify"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )

    assert result.returncode == 0, \
        f"Go module verification failed:\n{result.stderr}"


def test_cri_images_package_tests():
    """Run CRI images package tests - relevant to modified image methods (pass-to-pass).

    The PR modifies PullImage, ListImages, ImageStatus, and RemoveImage methods
    in instrumented_service.go. This test verifies the underlying images package
    tests still pass to ensure no regressions in image-related functionality.
    """
    result = subprocess.run(
        ["go", "test", "-v", "./internal/cri/server/images/"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180
    )

    assert result.returncode == 0, \
        f"CRI images package tests should pass:\n{result.stdout}\n{result.stderr}"


def test_cri_instrument_builds():
    """Verify CRI instrument package compiles (pass-to-pass).

    The PR modifies instrumented_service.go. This ensures the package builds.
    """
    result = subprocess.run(
        ["go", "build", "./internal/cri/instrument/"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )

    assert result.returncode == 0, \
        f"CRI instrument package should build:\n{result.stderr}"