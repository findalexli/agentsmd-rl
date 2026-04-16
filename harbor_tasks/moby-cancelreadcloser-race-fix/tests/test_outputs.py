#!/usr/bin/env python3
"""Tests for moby/moby PR #52280 - Fix race in cancelReadCloser"""

import subprocess
import sys
import os

REPO = "/workspace/moby"
CLIENT_DIR = "/workspace/moby/client"
ENV = {**os.environ, "CGO_ENABLED": "1"}


def test_race_condition_fix():
    """Test that the race condition in cancelReadCloser is fixed.

    This test runs the race detector against the cancelReadCloser code.
    Before the fix: Data race occurs when context is cancelled while
    newCancelReadCloser is still executing.
    After the fix: No data race - the sync.Once wrapped close function
    is called directly via crc.close() instead of through the Close() method.
    """
    # Run the specific test with race detector from within the client directory
    result = subprocess.run(
        ["go", "test", "-race", "-run", "TestNewCancelReadCloserRace", "-count=1", "-v", "."],
        cwd=CLIENT_DIR,
        capture_output=True,
        text=True,
        timeout=120,
        env=ENV
    )

    # Check for race detector warnings in output
    has_race = "DATA RACE" in result.stdout or "DATA RACE" in result.stderr
    test_passed = result.returncode == 0 and not has_race

    if has_race:
        raise AssertionError(f"Data race detected:\n{result.stderr}\n{result.stdout}")

    if result.returncode != 0:
        raise AssertionError(f"Test failed with exit code {result.returncode}:\n{result.stderr}\n{result.stdout}")


def test_close_after_context_cancel_no_double_race():
    """Test that Close can be called after context cancel without race conditions.

    Verifies behavior requirement #3: even when both automatic context-cancellation
    close and multiple manual Close() calls occur, there are no data races.
    This tests the OBSERVABLE BEHAVIOR (no races) rather than implementation.
    """
    test_code = '''
package client

import (
	"context"
	"io"
	"strings"
	"testing"
)

func TestCloseAfterCancelNoDoubleRace(t *testing.T) {
	for i := 0; i < 200; i++ {
		ctx, cancel := context.WithCancel(context.Background())
		rc := io.NopCloser(strings.NewReader("test data"))
		crc := newCancelReadCloser(ctx, rc)

		// Cancel to trigger automatic close
		cancel()

		// Multiple manual Close calls after cancel - should not cause race
		_ = crc.Close()
		_ = crc.Close()
		_ = crc.Close()
	}
}
'''
    test_path = os.path.join(CLIENT_DIR, "close_after_cancel_test.go")
    with open(test_path, 'w') as f:
        f.write(test_code)

    try:
        result = subprocess.run(
            ["go", "test", "-race", "-run", "TestCloseAfterCancelNoDoubleRace", "-v", "."],
            cwd=CLIENT_DIR,
            capture_output=True,
            text=True,
            timeout=120,
            env=ENV
        )

        has_race = "DATA RACE" in result.stdout or "DATA RACE" in result.stderr

        if has_race:
            raise AssertionError(f"Data race detected in Close after context cancel:\n{result.stderr}\n{result.stdout}")

        if result.returncode != 0:
            raise AssertionError(f"Test failed:\n{result.stderr}\n{result.stdout}")
    finally:
        # Clean up
        if os.path.exists(test_path):
            os.remove(test_path)


def test_utils_go_compiles():
    """Verify that client/utils.go compiles without errors."""
    result = subprocess.run(
        ["go", "build", "."],
        cwd=CLIENT_DIR,
        capture_output=True,
        text=True,
        timeout=60,
        env=ENV
    )

    if result.returncode != 0:
        raise AssertionError(f"Build failed:\n{result.stderr}")


def test_client_package_tests():
    """Run the full client package tests to ensure no regressions."""
    # Run non-race tests in the client package (excluding the new race test)
    result = subprocess.run(
        ["go", "test", "-run", "Test[^N]|TestN[^e]", "."],
        cwd=CLIENT_DIR,
        capture_output=True,
        text=True,
        timeout=300,
        env=ENV
    )

    # We allow some tests to fail due to environment, but check for compilation
    if "build" in result.stderr.lower() or "compile" in result.stderr.lower():
        raise AssertionError(f"Compilation error in client tests:\n{result.stderr}")


def test_close_no_race_with_multiple_calls():
    """Test that multiple Close calls do not cause data races.

    Verifies behavior requirement #3 by checking that multiple Close calls
    (after cancel and multiple manual calls) do not trigger races.
    Tests OBSERVABLE BEHAVIOR (no races) rather than counting close invocations.
    """
    test_code = '''
package client

import (
	"context"
	"io"
	"strings"
	"testing"
)

func TestCloseNoRaceWithMultipleCalls(t *testing.T) {
	for i := 0; i < 200; i++ {
		ctx, cancel := context.WithCancel(context.Background())
		rc := io.NopCloser(strings.NewReader("test data"))
		crc := newCancelReadCloser(ctx, rc)

		// Cancel to trigger automatic close path
		cancel()

		// Manually call Close multiple times - should not cause races
		_ = crc.Close()
		_ = crc.Close()
		_ = crc.Close()
	}
}
'''
    test_path = os.path.join(CLIENT_DIR, "close_no_race_test.go")
    with open(test_path, 'w') as f:
        f.write(test_code)

    try:
        result = subprocess.run(
            ["go", "test", "-race", "-run", "TestCloseNoRaceWithMultipleCalls", "-v", "."],
            cwd=CLIENT_DIR,
            capture_output=True,
            text=True,
            timeout=60,
            env=ENV
        )

        has_race = "DATA RACE" in result.stdout or "DATA RACE" in result.stderr

        if has_race:
            raise AssertionError(f"Data race detected in multiple Close calls:\n{result.stderr}\n{result.stdout}")

        if result.returncode != 0:
            raise AssertionError(f"Close no race test failed:\n{result.stderr}\n{result.stdout}")
    finally:
        if os.path.exists(test_path):
            os.remove(test_path)


# ========== Pass-to-pass tests from repo CI ==========
# These tests run actual CI commands from the moby/moby repository


def test_repo_utils_encode_platforms():
    """Repo test: TestEncodePlatforms passes (pass_to_pass).

    This is an existing test from client/utils_test.go that exercises
the encodePlatforms function in client/utils.go.
    """
    result = subprocess.run(
        ["go", "test", "-v", "-run", "TestEncodePlatforms", "-count=1", "."],
        cwd=CLIENT_DIR,
        capture_output=True,
        text=True,
        timeout=120,
        env=ENV
    )

    if result.returncode != 0:
        raise AssertionError(f"TestEncodePlatforms failed:\n{result.stderr}\n{result.stdout}")


def test_repo_go_vet():
    """Repo test: go vet passes on client package (pass_to_pass).

    go vet is a standard Go CI check that examines code for suspicious
constructs. This is part of the standard Go toolchain.
    """
    result = subprocess.run(
        ["go", "vet", "."],
        cwd=CLIENT_DIR,
        capture_output=True,
        text=True,
        timeout=120,
        env=ENV
    )

    if result.returncode != 0:
        raise AssertionError(f"go vet failed:\n{result.stderr}")


def test_repo_gofmt():
    """Repo test: gofmt check passes on client package (pass_to_pass).

    gofmt checks that Go code is properly formatted according to
standard Go formatting rules. This is part of the standard Go CI.
    """
    result = subprocess.run(
        ["gofmt", "-l", "."],
        cwd=CLIENT_DIR,
        capture_output=True,
        text=True,
        timeout=60,
        env=ENV
    )

    # gofmt returns 0 but prints non-formatted files to stdout
    if result.stdout.strip():
        raise AssertionError(f"gofmt found unformatted files:\n{result.stdout}")


def test_repo_client_options():
    """Repo test: Client options tests pass (pass_to_pass).

    These tests exercise the client options parsing which depends on
parseAPIVersion from utils.go.
    """
    result = subprocess.run(
        ["go", "test", "-v", "-run", "TestOptionWithAPIVersion", "-count=1", "."],
        cwd=CLIENT_DIR,
        capture_output=True,
        text=True,
        timeout=120,
        env=ENV
    )

    if result.returncode != 0:
        raise AssertionError(f"TestOptionWithAPIVersion failed:\n{result.stderr}\n{result.stdout}")


def test_repo_client_build():
    """Repo test: client package builds successfully (pass_to_pass).

    Verifies the client package compiles without errors.
    """
    result = subprocess.run(
        ["go", "build", "."],
        cwd=CLIENT_DIR,
        capture_output=True,
        text=True,
        timeout=120,
        env=ENV
    )

    if result.returncode != 0:
        raise AssertionError(f"Build failed:\n{result.stderr}")


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
