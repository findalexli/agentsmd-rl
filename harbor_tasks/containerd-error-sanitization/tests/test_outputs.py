"""Test outputs for containerd error sanitization fix.

These tests verify that the SanitizeError function correctly redacts
sensitive URL query parameters from errors before they are returned
to prevent credential leaks.
"""

import subprocess
import os

REPO = "/workspace/containerd"
SANITIZE_GO = f"{REPO}/internal/cri/util/sanitize.go"
SANITIZE_TEST = f"{REPO}/internal/cri/util/sanitize_test.go"


def run_go_test(test_filter=None):
    """Run Go tests in the cri/util package."""
    cmd = ["go", "test", "-v", "./internal/cri/util/..."]
    if test_filter:
        cmd.extend(["-run", test_filter])
    result = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, timeout=120)
    return result


def test_sanitize_error_file_exists():
    """Verify sanitize.go exists with expected content."""
    assert os.path.exists(SANITIZE_GO), f"sanitize.go not found at {SANITIZE_GO}"

    with open(SANITIZE_GO) as f:
        content = f.read()

    # Verify key function exists
    assert "func SanitizeError(err error) error" in content, "SanitizeError function not found"
    assert "func sanitizeURL(rawURL string) string" in content, "sanitizeURL function not found"
    assert "type sanitizedError struct" in content, "sanitizedError type not found"


def test_sanitize_error_nil_input():
    """Test that SanitizeError(nil) returns nil using the repo's unit tests."""
    # Use the repo's unit test
    result = subprocess.run(
        ["go", "test", "-v", "-run", "TestSanitizeError_NilError", "./internal/cri/util/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )
    assert result.returncode == 0, f"Test failed: {result.stdout}{result.stderr}"
    assert "PASS" in result.stdout or "PASS" in result.stderr, "Expected test to pass"


def test_sanitize_url_redacts_query_params():
    """Test that URLs with query params are sanitized using the repo's unit tests."""
    result = subprocess.run(
        ["go", "test", "-v", "-run", "TestSanitizeError_SimpleURLError", "./internal/cri/util/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )
    assert result.returncode == 0, f"Test failed: {result.stdout}{result.stderr}"
    assert "PASS" in result.stdout or "PASS" in result.stderr, "Expected test to pass"


def test_sanitize_error_non_url_error():
    """Test that non-URL errors pass through unchanged using the repo's unit tests."""
    result = subprocess.run(
        ["go", "test", "-v", "-run", "TestSanitizeError_NonURLError", "./internal/cri/util/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )
    assert result.returncode == 0, f"Test failed: {result.stdout}{result.stderr}"
    assert "PASS" in result.stdout or "PASS" in result.stderr, "Expected test to pass"


def test_sanitize_error_unwrap():
    """Test that Unwrap() returns the original error using the repo's unit tests."""
    result = subprocess.run(
        ["go", "test", "-v", "-run", "TestSanitizedError_Unwrap", "./internal/cri/util/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )
    assert result.returncode == 0, f"Test failed: {result.stdout}{result.stderr}"
    assert "PASS" in result.stdout or "PASS" in result.stderr, "Expected test to pass"


def test_sanitize_error_wrapped():
    """Test that wrapped errors with URL errors are sanitized properly using repo's unit tests."""
    result = subprocess.run(
        ["go", "test", "-v", "-run", "TestSanitizeError_WrappedError", "./internal/cri/util/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )
    assert result.returncode == 0, f"Test failed: {result.stdout}{result.stderr}"
    assert "PASS" in result.stdout or "PASS" in result.stderr, "Expected test to pass"


def test_instrumented_service_uses_sanitize():
    """Test that instrumented_service.go calls SanitizeError on errors."""
    instrumented_path = f"{REPO}/internal/cri/instrument/instrumented_service.go"

    with open(instrumented_path) as f:
        content = f.read()

    # Check that SanitizeError is called in image-related methods
    assert "ctrdutil.SanitizeError(err)" in content, "instrumented_service.go should call ctrdutil.SanitizeError(err)" 
    # Count occurrences - should be at least 4 (PullImage, ListImages, ImageStatus, RemoveImage)
    count = content.count("ctrdutil.SanitizeError(err)")
    assert count >= 4, f"Expected at least 4 SanitizeError calls, found {count}"


def test_sanitize_error_no_query_params():
    """Test that URLs without query params pass through unchanged using the repo's unit tests."""
    result = subprocess.run(
        ["go", "test", "-v", "-run", "TestSanitizeError_NoQueryParams", "./internal/cri/util/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )
    assert result.returncode == 0, f"Test failed: {result.stdout}{result.stderr}"
    assert "PASS" in result.stdout or "PASS" in result.stderr, "Expected test to pass"


def test_code_compiles():
    """Verify the code compiles without errors."""
    result = subprocess.run(
        ["go", "build", "./internal/cri/util/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"Code compilation failed: {result.stderr}"


# =============================================================================
# PASS-TO-PASS TESTS: Repo CI/CD checks that should pass on both base and gold
# =============================================================================

def test_repo_unit_tests_cri_util():
    """Repo's unit tests for cri/util package pass (pass_to_pass)."""
    r = subprocess.run(
        ["go", "test", "-timeout=120s", "./internal/cri/util/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert r.returncode == 0, f"Unit tests for cri/util failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


def test_repo_go_vet_cri_util():
    """Repo's go vet for cri/util package passes (pass_to_pass)."""
    r = subprocess.run(
        ["go", "vet", "./internal/cri/util/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert r.returncode == 0, f"go vet for cri/util failed:\n{r.stderr[-500:]}"


def test_repo_gofmt_cri_util():
    """Repo's gofmt for cri/util package passes (pass_to_pass)."""
    r = subprocess.run(
        ["gofmt", "-l", "internal/cri/util/*.go"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )
    # gofmt -l outputs file names if they need formatting; empty output means clean
    assert r.stdout.strip() == "", f"gofmt check failed - files need formatting:\n{r.stdout}"


def test_repo_build_cri_util():
    """Repo's cri/util package builds successfully (pass_to_pass)."""
    r = subprocess.run(
        ["go", "build", "./internal/cri/util/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert r.returncode == 0, f"Build for cri/util failed:\n{r.stderr[-500:]}"


def test_repo_build_cri_instrument():
    """Repo's cri/instrument package builds successfully (pass_to_pass)."""
    r = subprocess.run(
        ["go", "build", "./internal/cri/instrument/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert r.returncode == 0, f"Build for cri/instrument failed:\n{r.stderr[-500:]}"
