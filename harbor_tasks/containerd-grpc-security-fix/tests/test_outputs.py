"""
Test suite for containerd gRPC security fix.

This validates that the security fix for the gRPC authorization bypass vulnerability
has been properly applied. The fix adds strict path checking to prevent malformed
:path headers (missing leading slash) from bypassing security policies.
"""

import os
import subprocess
import re

REPO = "/workspace/containerd"
ENVCONFIG_PATH = f"{REPO}/vendor/google.golang.org/grpc/internal/envconfig/envconfig.go"
SERVER_PATH = f"{REPO}/vendor/google.golang.org/grpc/server.go"
VERSION_PATH = f"{REPO}/vendor/google.golang.org/grpc/version.go"
GOMOD_PATH = f"{REPO}/go.mod"


def test_envconfig_has_disable_strict_path_checking():
    """
    Fail-to-pass: Verify DisableStrictPathChecking env var is added.

    The fix adds a DisableStrictPathChecking envconfig option that allows
temporarily disabling strict path checking via environment variable.
    """
    with open(ENVCONFIG_PATH, 'r') as f:
        content = f.read()

    # Check for the variable declaration
    assert "DisableStrictPathChecking" in content, \
        "DisableStrictPathChecking variable not found in envconfig.go"

    # Check for proper environment variable name
    assert "GRPC_GO_EXPERIMENTAL_DISABLE_STRICT_PATH_CHECKING" in content, \
        "GRPC_GO_EXPERIMENTAL_DISABLE_STRICT_PATH_CHECKING env var not found"

    # Check that it defaults to false (strict checking enabled by default)
    pattern = r"DisableStrictPathChecking\s*=\s*boolFromEnv\([^)]*,\s*false\)"
    assert re.search(pattern, content), \
        "DisableStrictPathChecking should default to false (strict mode on)"


def test_server_has_handle_malformed_method_name():
    """
    Fail-to-pass: Verify handleMalformedMethodName function is added.

    This helper function handles the error response for malformed method names.
    """
    with open(SERVER_PATH, 'r') as f:
        content = f.read()

    assert "func (s *Server) handleMalformedMethodName(" in content, \
        "handleMalformedMethodName function not found in server.go"

    # Check that it writes Unimplemented status
    assert "codes.Unimplemented" in content, \
        "handleMalformedMethodName should return Unimplemented status"

    # Check for malformed method name error message
    assert "malformed method name:" in content, \
        "malformed method name error message not found"


def test_server_has_strict_path_checking_logic():
    """
    Fail-to-pass: Verify strict path checking logic in handleStream.

    The fix adds logic to reject requests with paths not starting with '/'.
    """
    with open(SERVER_PATH, 'r') as f:
        content = f.read()

    # Check for the strict path checking log emission field
    assert "strictPathCheckingLogEmitted" in content, \
        "strictPathCheckingLogEmitted field not found in Server struct"

    # Check for the empty method name check
    assert 'if sm == ""' in content, \
        "Empty method name check not found"

    # Check for the leading slash validation
    assert "if sm[0] != '/'" in content, \
        "Leading slash validation not found"

    # Check that it logs a warning about rejected malformed names
    assert "rejected malformed method name" in content, \
        "Rejection warning message not found"


def test_server_imports_envconfig():
    """
    Fail-to-pass: Verify server.go imports envconfig package.

    The fix requires importing envconfig to check DisableStrictPathChecking.
    """
    with open(SERVER_PATH, 'r') as f:
        content = f.read()

    # Check import
    assert '"google.golang.org/grpc/internal/envconfig"' in content, \
        "envconfig import not found in server.go"


def test_grpc_version_updated():
    """
    Pass-to-pass: Verify gRPC version is updated to 1.79.3.

    The fix bumps the gRPC version from 1.79.2 to 1.79.3.
    """
    # Check version.go
    with open(VERSION_PATH, 'r') as f:
        version_content = f.read()

    assert 'const Version = "1.79.3"' in version_content, \
        "gRPC version not updated to 1.79.3 in version.go"

    # Check go.mod
    with open(GOMOD_PATH, 'r') as f:
        gomod_content = f.read()

    assert "google.golang.org/grpc v1.79.3" in gomod_content, \
        "go.mod not updated to gRPC v1.79.3"


def test_go_build_compiles():
    """
    Fail-to-pass: Verify the code compiles successfully.

    Run go build to ensure the modified code is syntactically correct.
    """
    result = subprocess.run(
        ["go", "build", "./..."],
        cwd=REPO,
        capture_output=True,
        timeout=120
    )

    assert result.returncode == 0, \
        f"Go build failed:\n{result.stderr.decode()}"


def test_handleStream_calls_handleMalformed_for_empty_method():
    """
    Fail-to-pass: Verify handleStream calls handleMalformedMethodName for empty method.

    The fix should handle empty method names via the helper function.
    """
    with open(SERVER_PATH, 'r') as f:
        content = f.read()

    # Find the handleStream function and check it handles empty method
    pattern = r'if sm == "" \{\s*\n\s*s\.handleMalformedMethodName\(stream, ti\)'
    assert re.search(pattern, content), \
        "handleStream should call handleMalformedMethodName for empty method names"


def test_handleStream_calls_handleMalformed_for_missing_slash():
    """
    Fail-to-pass: Verify handleStream calls handleMalformedMethodName for paths without leading slash.

    When strict path checking is enabled (default), requests without leading slash should be rejected.
    """
    with open(SERVER_PATH, 'r') as f:
        content = f.read()

    # Look for the else branch that handles missing leading slash
    # After checking sm[0] != '/', it should call handleMalformedMethodName in the else branch
    # when DisableStrictPathChecking is false (default)

    # Check that handleMalformedMethodName is called when strict checking rejects
    pattern = r's\.handleMalformedMethodName\(stream, ti\)\s*\n\s*return'
    matches = re.findall(pattern, content)
    assert len(matches) >= 2, \
        f"handleMalformedMethodName should be called in multiple rejection cases, found {len(matches)} calls"


def test_envconfig_has_documentation():
    """
    Pass-to-pass: Verify DisableStrictPathChecking has proper documentation.

    The security fix should include documentation explaining the purpose.
    """
    with open(ENVCONFIG_PATH, 'r') as f:
        content = f.read()

    # Check for security-related documentation
    assert "security" in content.lower(), \
        "DisableStrictPathChecking should mention security in documentation"

    assert "path traversal" in content.lower() or "vulnerabilit" in content.lower(), \
        "Should mention path traversal or vulnerability in documentation"


# =============================================================================
# Repo CI/CD Pass-to-Pass Tests
# These tests ensure the repo's standard CI checks pass on both base and fixed commits.
# =============================================================================


def test_repo_go_build():
    """
    Pass-to-pass: Repo code compiles with `go build ./...`.

    This is the standard Go build check that containerd CI runs.
    """
    result = subprocess.run(
        ["go", "build", "./..."],
        cwd=REPO,
        capture_output=True,
        timeout=120
    )
    assert result.returncode == 0, \
        f"Go build failed:\n{result.stderr.decode()[-500:]}"


def test_repo_go_vet():
    """
    Pass-to-pass: gRPC vendor packages pass `go vet` checks.

    Runs go vet on the vendored gRPC packages modified by the fix.
    Full `go vet ./...` is excluded because the integration/ package has a
    pre-existing vet issue (lock copy) unrelated to this fix.
    """
    result = subprocess.run(
        ["go", "vet", "./vendor/google.golang.org/grpc/..."],
        cwd=REPO,
        capture_output=True,
        timeout=120
    )
    assert result.returncode == 0, \
        f"Go vet failed:\n{result.stderr.decode()[-500:]}"


def test_repo_vendor_modules():
    """
    Pass-to-pass: Vendor directory has consistent modules.

    Runs go mod verify to check that dependencies haven't been tampered with.
    """
    result = subprocess.run(
        ["go", "mod", "verify"],
        cwd=REPO,
        capture_output=True,
        timeout=60
    )
    assert result.returncode == 0, \
        f"Go mod verify failed:\n{result.stderr.decode()[-500:]}"


def test_repo_unit_tests_non_root():
    """
    Pass-to-pass: Core containerd unit tests pass.

    Runs tests for the core/ subtree which covers runtime, remotes, snapshots,
    and transfer packages. Vendored gRPC packages have no test files, so we
    test the core containerd packages that use gRPC instead.
    """
    result = subprocess.run(
        ["go", "test", "-count=1", "-timeout=120s", "./core/..."],
        cwd=REPO,
        capture_output=True,
        timeout=180
    )
    assert result.returncode == 0, \
        f"Core tests failed:\n{result.stderr.decode()[-500:]}"


def test_repo_go_mod_tidy():
    """
    Pass-to-pass: go.mod and go.sum are consistent.

    Verifies that the module files don't need to be updated.
    """
    result = subprocess.run(
        ["go", "mod", "tidy", "-diff"],
        cwd=REPO,
        capture_output=True,
        timeout=60
    )
    # -diff flag returns 0 if no changes needed, 1 if changes needed
    assert result.returncode == 0, \
        f"go.mod/go.sum need tidying:\n{result.stdout.decode()[-500:]}"


def test_repo_make_binaries():
    """
    Pass-to-pass: containerd binaries build successfully.

    Runs `make binaries` to verify the full containerd build works,
    which exercises the vendored gRPC packages that are modified.
    """
    result = subprocess.run(
        ["make", "binaries"],
        cwd=REPO,
        capture_output=True,
        timeout=180
    )
    assert result.returncode == 0, \
        f"make binaries failed:\n{result.stderr.decode()[-500:]}"


def test_repo_grpc_packages_build():
    """
    Pass-to-pass: Modified gRPC vendor packages compile.

    Specifically builds the envconfig and server packages that are
    modified by the security fix to ensure they compile correctly.
    """
    result = subprocess.run(
        ["go", "build", "./vendor/google.golang.org/grpc/internal/envconfig"],
        cwd=REPO,
        capture_output=True,
        timeout=60
    )
    assert result.returncode == 0, \
        f"grpc/envconfig build failed:\n{result.stderr.decode()[-500:]}"

    result = subprocess.run(
        ["go", "build", "./vendor/google.golang.org/grpc"],
        cwd=REPO,
        capture_output=True,
        timeout=60
    )
    assert result.returncode == 0, \
        f"grpc build failed:\n{result.stderr.decode()[-500:]}"
