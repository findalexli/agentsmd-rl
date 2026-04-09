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
    """Test that SanitizeError(nil) returns nil."""
    # Write a simple test program
    test_prog = '''
package main

import (
	"fmt"
	"os"

	"github.com/containerd/containerd/internal/cri/util"
)

func main() {
	result := util.SanitizeError(nil)
	if result != nil {
		fmt.Println("FAIL: SanitizeError(nil) should return nil")
		os.Exit(1)
	}
	fmt.Println("PASS")
}
'''
    test_file = f"{REPO}/test_nil.go"
    with open(test_file, 'w') as f:
        f.write(test_prog)

    try:
        result = subprocess.run(
            ["go", "run", "test_nil.go"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=60
        )
        assert result.returncode == 0, f"Test failed: {result.stdout}{result.stderr}"
        assert "PASS" in result.stdout, "Expected PASS output"
    finally:
        os.remove(test_file)


def test_sanitize_url_redacts_query_params():
    """Test that URLs with query params are sanitized."""
    test_prog = '''
package main

import (
	"errors"
	"fmt"
	"net/url"
	"os"
	"strings"

	"github.com/containerd/containerd/internal/cri/util"
)

func main() {
	originalURL := "https://storage.blob.core.windows.net/container/blob?sig=SECRET&sv=2020"
	urlErr := &url.Error{
		Op:  "Get",
		URL: originalURL,
		Err: errors.New("connection timeout"),
	}

	sanitized := util.SanitizeError(urlErr)
	if sanitized == nil {
		fmt.Println("FAIL: SanitizeError should return non-nil")
		os.Exit(1)
	}

	errStr := sanitized.Error()

	// Check secret is redacted
	if strings.Contains(errStr, "SECRET") {
		fmt.Printf("FAIL: Secret should be sanitized, got: %s\\n", errStr)
		os.Exit(1)
	}

	// Check redacted marker exists
	if !strings.Contains(errStr, "[REDACTED]") {
		fmt.Printf("FAIL: Should contain [REDACTED] marker, got: %s\\n", errStr)
		os.Exit(1)
	}

	fmt.Println("PASS")
}
'''
    test_file = f"{REPO}/test_redact.go"
    with open(test_file, 'w') as f:
        f.write(test_prog)

    try:
        result = subprocess.run(
            ["go", "run", "test_redact.go"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=60
        )
        assert result.returncode == 0, f"Test failed: {result.stdout}{result.stderr}"
        assert "PASS" in result.stdout, "Expected PASS output"
    finally:
        os.remove(test_file)


def test_sanitize_error_non_url_error():
    """Test that non-URL errors pass through unchanged."""
    test_prog = '''
package main

import (
	"errors"
	"fmt"
	"os"

	"github.com/containerd/containerd/internal/cri/util"
)

func main() {
	regularErr := errors.New("some error occurred")
	sanitized := util.SanitizeError(regularErr)

	// Should be the exact same error
	if sanitized != regularErr {
		fmt.Println("FAIL: Non-URL error should pass through unchanged")
		os.Exit(1)
	}
	fmt.Println("PASS")
}
'''
    test_file = f"{REPO}/test_non_url.go"
    with open(test_file, 'w') as f:
        f.write(test_prog)

    try:
        result = subprocess.run(
            ["go", "run", "test_non_url.go"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=60
        )
        assert result.returncode == 0, f"Test failed: {result.stdout}{result.stderr}"
        assert "PASS" in result.stdout, "Expected PASS output"
    finally:
        os.remove(test_file)


def test_sanitize_error_unwrap():
    """Test that Unwrap() returns the original error."""
    test_prog = '''
package main

import (
	"errors"
	"fmt"
	"net/url"
	"os"

	"github.com/containerd/containerd/internal/cri/util"
)

func main() {
	originalURL := "https://storage.blob.core.windows.net/blob?sig=SECRET"
	urlErr := &url.Error{
		Op:  "Get",
		URL: originalURL,
		Err: errors.New("timeout"),
	}

	sanitized := util.SanitizeError(urlErr)
	unwrapped := errors.Unwrap(sanitized)

	if unwrapped == nil {
		fmt.Println("FAIL: Should be able to unwrap sanitized error")
		os.Exit(1)
	}

	// Should be the original url.Error
	if unwrapped != urlErr {
		fmt.Println("FAIL: Unwrapped error should match original")
		os.Exit(1)
	}

	// Verify we can still access url.Error fields through unwrapping
	var targetURLErr *url.Error
	if !errors.As(sanitized, &targetURLErr) {
		fmt.Println("FAIL: Should be able to find *url.Error in chain")
		os.Exit(1)
	}

	if targetURLErr.Op != "Get" {
		fmt.Printf("FAIL: Op should be 'Get', got '%s'\\n", targetURLErr.Op)
		os.Exit(1)
	}

	fmt.Println("PASS")
}
'''
    test_file = f"{REPO}/test_unwrap.go"
    with open(test_file, 'w') as f:
        f.write(test_prog)

    try:
        result = subprocess.run(
            ["go", "run", "test_unwrap.go"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=60
        )
        assert result.returncode == 0, f"Test failed: {result.stdout}{result.stderr}"
        assert "PASS" in result.stdout, "Expected PASS output"
    finally:
        os.remove(test_file)


def test_sanitize_error_wrapped():
    """Test that wrapped errors with URL errors are sanitized properly."""
    test_prog = '''
package main

import (
	"errors"
	"fmt"
	"net/url"
	"os"
	"strings"

	"github.com/containerd/containerd/internal/cri/util"
)

func main() {
	originalURL := "https://storage.blob.core.windows.net/blob?sig=SECRET&sv=2020"
	urlErr := &url.Error{
		Op:  "Get",
		URL: originalURL,
		Err: errors.New("timeout"),
	}

	wrappedErr := fmt.Errorf("image pull failed: %w", urlErr)
	sanitized := util.SanitizeError(wrappedErr)

	errStr := sanitized.Error()

	// Check wrapper message is preserved
	if !strings.Contains(errStr, "image pull failed") {
		fmt.Printf("FAIL: Wrapper message should be preserved, got: %s\\n", errStr)
		os.Exit(1)
	}

	// Check secret is redacted
	if strings.Contains(errStr, "SECRET") {
		fmt.Printf("FAIL: Secret should be sanitized, got: %s\\n", errStr)
		os.Exit(1)
	}

	// Should be able to unwrap and find original url.Error
	var targetURLErr *url.Error
	if !errors.As(sanitized, &targetURLErr) {
		fmt.Println("FAIL: Should be able to find *url.Error in sanitized error chain")
		os.Exit(1)
	}

	// The original url.Error should still have the secret (unwrapped version is unchanged)
	if !strings.Contains(targetURLErr.URL, "SECRET") {
		fmt.Println("FAIL: Unwrapped url.Error should preserve original URL")
		os.Exit(1)
	}

	fmt.Println("PASS")
}
'''
    test_file = f"{REPO}/test_wrapped.go"
    with open(test_file, 'w') as f:
        f.write(test_prog)

    try:
        result = subprocess.run(
            ["go", "run", "test_wrapped.go"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=60
        )
        assert result.returncode == 0, f"Test failed: {result.stdout}{result.stderr}"
        assert "PASS" in result.stdout, "Expected PASS output"
    finally:
        os.remove(test_file)


def test_instrumented_service_uses_sanitize():
    """Test that instrumented_service.go calls SanitizeError on errors."""
    instrumented_path = f"{REPO}/internal/cri/instrument/instrumented_service.go"

    with open(instrumented_path) as f:
        content = f.read()

    # Check that SanitizeError is called in image-related methods
    assert "ctrdutil.SanitizeError(err)" in content, \
        "instrumented_service.go should call ctrdutil.SanitizeError(err)"

    # Count occurrences - should be at least 4 (PullImage, ListImages, ImageStatus, RemoveImage)
    count = content.count("ctrdutil.SanitizeError(err)")
    assert count >= 4, f"Expected at least 4 SanitizeError calls, found {count}"


def test_sanitize_error_no_query_params():
    """Test that URLs without query params pass through unchanged."""
    test_prog = '''
package main

import (
	"errors"
	"fmt"
	"net/url"
	"os"

	"github.com/containerd/containerd/internal/cri/util"
)

func main() {
	// URL without query params
	urlErr := &url.Error{
		Op:  "Get",
		URL: "https://registry.example.com/v2/image/manifests/latest",
		Err: errors.New("not found"),
	}

	sanitized := util.SanitizeError(urlErr)

	// Should return the same error object (no sanitization needed)
	if sanitized != urlErr {
		fmt.Println("FAIL: Errors without query params should pass through unchanged")
		os.Exit(1)
	}
	fmt.Println("PASS")
}
'''
    test_file = f"{REPO}/test_no_query.go"
    with open(test_file, 'w') as f:
        f.write(test_prog)

    try:
        result = subprocess.run(
            ["go", "run", "test_no_query.go"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=60
        )
        assert result.returncode == 0, f"Test failed: {result.stdout}{result.stderr}"
        assert "PASS" in result.stdout, "Expected PASS output"
    finally:
        os.remove(test_file)


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
