"""
Tests for containerd parallel unpack fix with overlayfs.

This PR fixes issue #13030 where parallel image unpacking with the overlayfs
snapshotter causes whiteout files to not be properly processed.

The fix adds a bindToOverlay function that converts bind mounts to overlay mounts
during parallel unpack, allowing the applier to correctly process whiteouts.

These tests verify BEHAVIOR, not implementation:
- The Go unit tests actually execute the bindToOverlay function with various inputs
- Build/vet/fmt verify the code compiles and is correct
"""

import subprocess
import os
import pytest

REPO = "/workspace/containerd"


def test_bind_to_overlay_unit_tests():
    """
    Run the Go unit tests for bindToOverlay.
    This actually IMPORTS and CALLS the code, verifying the function exists
    and produces correct output for various inputs.

    behavioral: runs go test which compiles and executes the test binary,
    which imports the unpack package and calls bindToOverlay with test inputs,
    asserting on return values.

    MUST fail on base code (where TestBindToOverlay doesn't exist).
    """
    result = subprocess.run(
        ["go", "test", "-v", "./core/unpack/...", "-run", "TestBindToOverlay"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    # Check that tests actually ran (not "no tests to run")
    combined = result.stdout + result.stderr
    assert "no tests to run" not in combined.lower(), (
        f"TestBindToOverlay does not exist in the base code. "
        f"The fix must add TestBindToOverlay to verify bindToOverlay behavior.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )
    assert result.returncode == 0, (
        f"TestBindToOverlay tests failed.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )


def test_unpacker_package_tests():
    """
    Run all unpacker package unit tests.
    Verifies the unpacker works correctly as a whole.
    """
    result = subprocess.run(
        ["go", "test", "-v", "./core/unpack/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180
    )
    assert result.returncode == 0, (
        f"Unpacker package tests failed.\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )


def test_build():
    """Verify the project builds successfully."""
    result = subprocess.run(
        ["go", "build", "./..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )
    assert result.returncode == 0, (
        f"Build failed - the code doesn't compile.\n"
        f"stderr:\n{result.stderr}"
    )


def test_vet():
    """Run go vet to check for code issues."""
    result = subprocess.run(
        ["go", "vet", "./core/unpack/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, (
        f"Go vet found issues.\n"
        f"stderr:\n{result.stderr}"
    )


def test_go_mod_verify():
    """Verify Go modules are valid (pass-to-pass test)."""
    result = subprocess.run(
        ["go", "mod", "verify"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, (
        f"Go mod verify failed.\n"
        f"stderr:\n{result.stderr}"
    )


def test_go_fmt():
    """Verify Go code is properly formatted (pass-to-pass test)."""
    result = subprocess.run(
        ["go", "fmt", "./core/unpack/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    # go fmt returns 0 and outputs file names if changes needed
    assert result.returncode == 0, (
        f"Go fmt failed.\n"
        f"stderr:\n{result.stderr}"
    )
    # If output is empty, no files need formatting
    assert result.stdout.strip() == "", (
        f"Go formatting issues in:\n{result.stdout}"
    )
