"""Test containerd resolver fallback behavior for PR #13017.

This tests that transient errors from /manifests/ endpoint do NOT trigger
fallback to /blobs/ endpoint, which could pollute the content store with
incorrectly typed descriptors.

The Go tests added in the PR don't exist at base commit, so we inject them
before running the tests.
"""

import subprocess
import sys
import os
import shutil

REPO_PATH = "/workspace/containerd"
NEW_TESTS_FILE = "/workspace/tests/new_tests.go"


def inject_new_tests():
    """Inject the new test functions from the PR into resolver_test.go."""
    test_file = os.path.join(REPO_PATH, "core/remotes/docker/resolver_test.go")
    new_tests_file = NEW_TESTS_FILE

    # Read the current test file
    with open(test_file, "r") as f:
        content = f.read()

    # Check if tests already exist
    if "TestResolveTransientManifestError" in content:
        return  # Tests already present

    # Read the new tests
    with open(new_tests_file, "r") as f:
        new_tests = f.read()

    # Find the last closing brace of the file and insert before it
    # We need to insert the tests at the end, before the final closing brace of the package
    # The file likely ends with helper functions - find a good insertion point

    # Insert before the last function or at the end
    lines = content.split("\n")

    # Find a good insertion point - after the last test or helper function
    # We'll append to the end of the file
    insert_pos = len(lines)

    # Check if there's a trailing newline
    if lines[-1] == "":
        insert_pos = len(lines) - 1

    # Insert the new tests
    lines.insert(insert_pos, "")
    lines.insert(insert_pos + 1, new_tests)

    # Write back
    with open(test_file, "w") as f:
        f.write("\n".join(lines))


def run_go_test(test_name: str, timeout: int = 60) -> tuple[bool, str]:
    """Run a specific Go test and return (passed, output)."""
    cmd = [
        "go", "test",
        "-v",
        "-run", f"^{test_name}$",
        "-timeout", f"{timeout}s",
        "./core/remotes/docker/"
    ]
    result = subprocess.run(
        cmd,
        cwd=REPO_PATH,
        capture_output=True,
        text=True
    )
    return result.returncode == 0, result.stdout + result.stderr


def test_resolve_transient_manifest_error():
    """TestResolveTransientManifestError - FAIL TO PASS

    Verifies that a transient server error (5xx) from the /manifests/ endpoint
    does NOT cause containerd to fall back to the /blobs/ endpoint.

    Before the fix: a 500 from /manifests/ would cause Resolve() to silently
    retry via /blobs/, which returns "application/octet-stream" instead of
    a proper manifest media type - poisoning the descriptor.

    After the fix: 5xx from /manifests/ returns the server error, does NOT try /blobs/.
    """
    # First inject the new tests
    inject_new_tests()

    passed, output = run_go_test("TestResolveTransientManifestError")
    assert passed, f"TestResolveTransientManifestError failed:\n{output}"


def test_resolve_404_manifest_fallback():
    """TestResolve404ManifestFallback - PASS TO PASS

    Verifies that a 404 from /manifests/ DOES allow fallback to /blobs/.
    This preserves backward compatibility with non-standard registries that
    may only serve certain digests via /blobs/.
    """
    # First inject the new tests (no-op if already present)
    inject_new_tests()

    passed, output = run_go_test("TestResolve404ManifestFallback")
    assert passed, f"TestResolve404ManifestFallback failed:\n{output}"


def test_resolver_compiles():
    """Verify the resolver code compiles without errors."""
    result = subprocess.run(
        ["go", "build", "./core/remotes/docker/"],
        cwd=REPO_PATH,
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, f"Resolver compilation failed:\n{result.stderr}"


def test_blobs_fallback_check_present():
    """Verify the firstErrPriority check is present in resolver.go.

    This is a structural test gated by the behavioral tests above.
    The fix adds a check: if firstErrPriority > 2 { break }
    to prevent fallback on transient errors.
    """
    resolver_file = os.path.join(REPO_PATH, "core/remotes/docker/resolver.go")
    with open(resolver_file, "r") as f:
        content = f.read()

    # The fix adds a check for firstErrPriority > 2
    assert "firstErrPriority > 2" in content, \
        "The firstErrPriority > 2 check is missing from resolver.go"

    # Verify the break statement exists in the context of the fix
    lines = content.split("\n")
    found_priority_check = False
    for i, line in enumerate(lines):
        if "firstErrPriority > 2" in line:
            # Check that the next non-empty line has break
            for j in range(i+1, min(i+5, len(lines))):
                if lines[j].strip() == "break":
                    found_priority_check = True
                    break
            break

    assert found_priority_check, \
        "The firstErrPriority check is present but 'break' statement not found in expected location"


# =============================================================================
# Pass-to-Pass Tests: Repo CI/CD Checks
# These verify that the repo's standard CI checks pass on both base and fixed.
# =============================================================================


def test_repo_build():
    """Repo's Go build passes (pass_to_pass).

    Verifies that the core/remotes/docker package compiles without errors.
    This is the equivalent of 'make build' for the specific module.
    """
    r = subprocess.run(
        ["go", "build", "./core/remotes/docker/"],
        capture_output=True, text=True, timeout=120, cwd=REPO_PATH,
    )
    assert r.returncode == 0, f"Go build failed:\n{r.stderr}"


def test_repo_unit_tests():
    """Repo's Go unit tests pass (pass_to_pass).

    Verifies that existing tests in core/remotes/docker still pass.
    This ensures the fix doesn't break existing functionality.
    Excludes the injected fail-to-pass tests which are expected to fail on base.
    """
    r = subprocess.run(
        ["go", "test", "-v", "-count=1", "-timeout=120s",
         "-skip", "TestResolveTransientManifestError|TestResolve404ManifestFallback",
         "./core/remotes/docker/"],
        capture_output=True, text=True, timeout=120, cwd=REPO_PATH,
    )
    assert r.returncode == 0, f"Go unit tests failed:\n{r.stdout[-2000:]}\n{r.stderr[-500:]}"


def test_repo_vet():
    """Repo's Go vet passes (pass_to_pass).

    Verifies that go vet reports no issues with the code.
    This is a standard Go linting check.
    """
    r = subprocess.run(
        ["go", "vet", "./core/remotes/docker/"],
        capture_output=True, text=True, timeout=120, cwd=REPO_PATH,
    )
    assert r.returncode == 0, f"Go vet failed:\n{r.stderr}"


if __name__ == "__main__":
    # Run all tests
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
