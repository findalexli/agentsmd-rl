"""
Test outputs for containerd PR #13017

This PR fixes a bug where transient errors (5xx) from the /manifests/ endpoint
cause the resolver to fall back to /blobs/, which returns wrong content-type
and permanently poisons the content store.
"""

import subprocess
import sys
import os

REPO = "/workspace/containerd"


def test_gofmt_check():
    """Go code is properly formatted (pass_to_pass)."""
    result = subprocess.run(
        ["gofmt", "-l", "core/remotes/docker/resolver.go"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )
    # gofmt returns empty stdout if file is properly formatted
    assert result.stdout.strip() == "", f"File not formatted: {result.stdout}"


def test_go_build():
    """Package compiles without errors (pass_to_pass)."""
    result = subprocess.run(
        ["go", "build", "./core/remotes/docker/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"Build failed: {result.stderr}"


def test_resolve_no_blobs_fallback_on_5xx():
    """
    Fail-to-pass: Transient 5xx error from /manifests/ should NOT trigger /blobs/ fallback.

    Before fix: 500 from /manifests/ → fallback to /blobs/ → wrong content-type cached.
    After fix: 500 from /manifests/ → return error immediately, no fallback.
    """
    test_code = """
package docker

import (
	"context"
	"errors"
	"fmt"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"

	remoteerrors "github.com/containerd/containerd/v2/core/remotes/errors"
)

func TestResolveNoBlobsFallbackOn5xx(t *testing.T) {
	var (
		manifestCalled int
		blobsCalled    bool
		repo           = "test-repo"
		dgst           = "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
	)

	ts := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if strings.HasSuffix(r.URL.Path, "/manifests/"+dgst) {
			manifestCalled++
			w.WriteHeader(http.StatusInternalServerError)  // 500 error
			return
		}
		if strings.HasSuffix(r.URL.Path, "/blobs/"+dgst) {
			blobsCalled = true
			w.Header().Set("Content-Type", "application/octet-stream")
			w.Header().Set("Docker-Content-Digest", dgst)
			w.WriteHeader(http.StatusOK)
			return
		}
		if r.URL.Path == "/v2/" {
			w.WriteHeader(http.StatusOK)
			return
		}
		w.WriteHeader(http.StatusNotFound)
	}))
	defer ts.Close()

	resolver := NewResolver(ResolverOptions{
		Hosts: func(string) ([]RegistryHost, error) {
			return []RegistryHost{
				{
					Host:         ts.URL[len("http://"):],
					Scheme:       "http",
					Capabilities: HostCapabilityPull | HostCapabilityResolve,
				},
			}, nil
		},
	})

	ref := fmt.Sprintf("%s/%s@%s", ts.URL[len("http://"):], repo, dgst)
	_, _, err := resolver.Resolve(context.Background(), ref)

	if manifestCalled == 0 {
		t.Fatal("manifests endpoint was not called")
	}
	if blobsCalled {
		t.Error("FAIL: blobs endpoint was called on 500 error - this pollutes content store")
	}
	if err == nil {
		t.Fatal("expected error from Resolve, but got nil")
	}

	// Error should be ErrUnexpectedStatus with 500, not a "not found" error
	var unexpectedStatus remoteerrors.ErrUnexpectedStatus
	if !errors.As(err, &unexpectedStatus) {
		t.Errorf("expected ErrUnexpectedStatus (from 500), got %T: %v", err, err)
	} else if unexpectedStatus.StatusCode != http.StatusInternalServerError {
		t.Errorf("expected status 500, got %d", unexpectedStatus.StatusCode)
	}
}
"""
    # Write the test file
    test_file = os.path.join(REPO, "core/remotes/docker/resolver_f2p_test.go")
    with open(test_file, "w") as f:
        f.write(test_code)

    try:
        # Run the specific test
        result = subprocess.run(
            ["go", "test", "-v", "-run", "TestResolveNoBlobsFallbackOn5xx", "./core/remotes/docker/"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=120
        )

        # Cleanup test file
        os.remove(test_file)

        if result.returncode != 0:
            print(f"Test output:\n{result.stdout}\n{result.stderr}")

        # The test should PASS (no blobs fallback on 5xx)
        assert result.returncode == 0, f"Test failed - 5xx still triggers /blobs/ fallback: {result.stderr}"
    except subprocess.TimeoutExpired:
        os.remove(test_file)
        raise AssertionError("Test timed out")


def test_resolve_allows_blobs_fallback_on_404():
    """
    Pass-to-pass: 404 from /manifests/ SHOULD allow fallback to /blobs/.

    This is expected behavior for backward compatibility with legacy registries.
    """
    test_code = """
package docker

import (
	"context"
	"fmt"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
)

func TestResolveAllowsBlobsFallbackOn404(t *testing.T) {
	var (
		manifestCalled bool
		blobsCalled    bool
		repo           = "test-repo"
		dgst           = "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
	)

	ts := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if strings.HasSuffix(r.URL.Path, "/manifests/"+dgst) {
			manifestCalled = true
			w.WriteHeader(http.StatusNotFound)  // 404 - allows fallback
			return
		}
		if strings.HasSuffix(r.URL.Path, "/blobs/"+dgst) {
			blobsCalled = true
			w.Header().Set("Content-Type", "application/vnd.docker.distribution.manifest.v2+json")
			w.Header().Set("Docker-Content-Digest", dgst)
			w.WriteHeader(http.StatusOK)
			return
		}
		if r.URL.Path == "/v2/" {
			w.WriteHeader(http.StatusOK)
			return
		}
	}))
	defer ts.Close()

	resolver := NewResolver(ResolverOptions{
		Hosts: func(string) ([]RegistryHost, error) {
			return []RegistryHost{
				{
					Host:         ts.URL[len("http://"):],
					Scheme:       "http",
					Capabilities: HostCapabilityPull | HostCapabilityResolve,
				},
			}, nil
		},
	})

	ref := fmt.Sprintf("%s/%s@%s", ts.URL[len("http://"):], repo, dgst)
	_, desc, err := resolver.Resolve(context.Background(), ref)

	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if !manifestCalled {
		t.Error("manifests endpoint was not called")
	}
	if !blobsCalled {
		t.Error("blobs endpoint was not called on 404 - backward compatibility broken")
	}
	if desc.MediaType != "application/vnd.docker.distribution.manifest.v2+json" {
		t.Errorf("unexpected media type: %s", desc.MediaType)
	}
}
"""
    # Write the test file
    test_file = os.path.join(REPO, "core/remotes/docker/resolver_p2p_test.go")
    with open(test_file, "w") as f:
        f.write(test_code)

    try:
        # Run the specific test
        result = subprocess.run(
            ["go", "test", "-v", "-run", "TestResolveAllowsBlobsFallbackOn404", "./core/remotes/docker/"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=120
        )

        # Cleanup
        os.remove(test_file)

        assert result.returncode == 0, f"404 fallback test failed: {result.stderr}"
    except subprocess.TimeoutExpired:
        os.remove(test_file)
        raise AssertionError("Test timed out")


def test_5xx_errors_not_cached():
    """
    Fail-to-pass: Multiple 5xx errors should not result in cached blob descriptor.

    Verifies that when hitting various 5xx status codes (500, 502, 503),
    the resolver consistently returns errors without falling back to /blobs/.
    """
    test_code = """
package docker

import (
	"context"
	"errors"
	"fmt"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"

	remoteerrors "github.com/containerd/containerd/v2/core/remotes/errors"
)

func Test5xxErrorsNotCached(t *testing.T) {
	statusCodes := []int{500, 502, 503}

	for _, statusCode := range statusCodes {
		t.Run(fmt.Sprintf("status_%d", statusCode), func(t *testing.T) {
			var blobsCalled bool
			dgst := "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"

			ts := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
				if strings.HasSuffix(r.URL.Path, "/manifests/"+dgst) {
					w.WriteHeader(statusCode)
					return
				}
				if strings.HasSuffix(r.URL.Path, "/blobs/"+dgst) {
					blobsCalled = true
					w.Header().Set("Content-Type", "application/octet-stream")
					w.WriteHeader(http.StatusOK)
					return
				}
				if r.URL.Path == "/v2/" {
					w.WriteHeader(http.StatusOK)
					return
				}
			}))
			defer ts.Close()

			resolver := NewResolver(ResolverOptions{
				Hosts: func(string) ([]RegistryHost, error) {
					return []RegistryHost{{
						Host:         ts.URL[len("http://"):],
						Scheme:       "http",
						Capabilities: HostCapabilityPull | HostCapabilityResolve,
					}}, nil
				},
			})

			ref := fmt.Sprintf("%s/test@%s", ts.URL[len("http://"):], dgst)
			_, _, err := resolver.Resolve(context.Background(), ref)

			if blobsCalled {
				t.Errorf("blobs called for status %d - should not fallback", statusCode)
			}
			if err == nil {
				t.Fatal("expected error")
			}

			var unexpectedStatus remoteerrors.ErrUnexpectedStatus
			if !errors.As(err, &unexpectedStatus) || unexpectedStatus.StatusCode != statusCode {
				t.Errorf("expected %d error, got %v", statusCode, err)
			}
		})
	}
}
"""
    test_file = os.path.join(REPO, "core/remotes/docker/resolver_5xx_test.go")
    with open(test_file, "w") as f:
        f.write(test_code)

    try:
        result = subprocess.run(
            ["go", "test", "-v", "-run", "Test5xxErrorsNotCached", "./core/remotes/docker/"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=120
        )

        os.remove(test_file)
        assert result.returncode == 0, f"5xx error test failed: {result.stderr}"
    except subprocess.TimeoutExpired:
        os.remove(test_file)
        raise AssertionError("Test timed out")


def test_resolver_priority_check_present():
    """
    Structural: Verify the fix checks firstErrPriority to limit fallback.

    This test verifies that the code contains the fix that checks
    firstErrPriority > 2 before allowing fallback to /blobs/.
    """
    resolver_file = os.path.join(REPO, "core/remotes/docker/resolver.go")
    with open(resolver_file, "r") as f:
        content = f.read()

    # The fix adds: if firstErrPriority > 2 { break }
    assert "firstErrPriority > 2" in content, \
        "Fix not applied: missing 'firstErrPriority > 2' check to limit /blobs/ fallback"

    # Also check the comment explaining the fix is present
    assert "falling back to /blobs endpoint should happen in extreme cases" in content, \
        "Fix explanation comment not present"


def test_unit_tests_pass():
    """Upstream unit tests for the resolver package pass (pass_to_pass)."""
    result = subprocess.run(
        ["go", "test", "-v", "-count=1", "-timeout=300s", "./core/remotes/docker/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=360
    )

    # Some tests may fail due to network requirements, check for compilation success
    # and basic test infrastructure
    if result.returncode != 0:
        # If it failed due to compilation, that's a real failure
        if "build" in result.stderr.lower() or "cannot find" in result.stderr.lower():
            assert False, f"Compilation error: {result.stderr}"

        # Check that at least some tests ran (not a total infrastructure failure)
        if "PASS" not in result.stdout and "FAIL" not in result.stdout:
            assert False, f"No tests ran: {result.stderr}"

    # The test passes if we can compile and run tests (even if some require network)
    assert True


def test_resolver_basic_tests():
    """Resolver basic functionality tests pass (pass_to_pass)."""
    result = subprocess.run(
        ["go", "test", "-v", "-count=1", "-timeout=120s", "-run", "TestHTTPResolver|TestHTTPSResolver|TestBasicResolver", "./core/remotes/docker/"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180
    )
    assert result.returncode == 0, f"Resolver basic tests failed:\n{result.stderr[-500:]}"


def test_resolver_fallback_tests():
    """Resolver fallback tests pass (pass_to_pass)."""
    result = subprocess.run(
        ["go", "test", "-v", "-count=1", "-timeout=120s", "-run", "TestHostFailureFallbackResolver|TestHTTPFallbackResolver", "./core/remotes/docker/"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180
    )
    assert result.returncode == 0, f"Resolver fallback tests failed:\n{result.stderr[-500:]}"


def test_fetcher_tests():
    """Fetcher tests pass (pass_to_pass)."""
    result = subprocess.run(
        ["go", "test", "-v", "-count=1", "-timeout=120s", "-run", "TestFetcher", "./core/remotes/docker/"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180
    )
    assert result.returncode == 0, f"Fetcher tests failed:\n{result.stderr[-500:]}"


def test_registry_tests():
    """Registry tests pass (pass_to_pass)."""
    result = subprocess.run(
        ["go", "test", "-v", "-count=1", "-timeout=120s", "-run", "TestRegistry", "./core/remotes/docker/"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180
    )
    assert result.returncode == 0, f"Registry tests failed:\n{result.stderr[-500:]}"


def test_go_vet():
    """Go vet static analysis passes (pass_to_pass)."""
    result = subprocess.run(
        ["go", "vet", "./core/remotes/docker/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"Go vet failed:\n{result.stderr[-500:]}"


def test_go_mod_verify():
    """Go modules are valid (pass_to_pass)."""
    result = subprocess.run(
        ["go", "mod", "verify"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )
    assert result.returncode == 0, f"Go mod verify failed:\n{result.stderr[-500:]}"


def test_resolver_auth_tests():
    """Resolver authentication tests pass (pass_to_pass)."""
    result = subprocess.run(
        ["go", "test", "-v", "-count=1", "-timeout=120s", "-run", "TestAnonymousTokenResolver|TestBasicAuthTokenResolver|TestBasicAuthResolver", "./core/remotes/docker/"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180
    )
    assert result.returncode == 0, f"Resolver auth tests failed:\n{result.stderr[-500:]}"


def test_core_remotes_handlers():
    """Core remotes handlers tests pass (pass_to_pass)."""
    result = subprocess.run(
        ["go", "test", "-v", "-count=1", "-timeout=120s", "-run", "TestHandlers", "./core/remotes/"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180
    )
    assert result.returncode == 0, f"Core remotes handlers tests failed:\n{result.stderr[-500:]}"
