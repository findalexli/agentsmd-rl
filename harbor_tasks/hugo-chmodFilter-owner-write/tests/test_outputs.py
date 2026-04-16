"""Behavioral tests for Hugo chmodFilter fix.

This tests that the chmodFilter function correctly:
1. Skips permission syncing for directories (existing behavior)
2. Skips permission syncing for files without owner-write permission (new behavior)

The bug was that files from Go module cache (typically 0444 permissions) were
being synced with read-only permissions, making the output files non-writable.

These tests verify BEHAVIOR by compiling and running a Go test that exercises
the chmodFilter function with actual file system operations (temp files/dirs).
"""

import subprocess
import os
import pytest
import tempfile

REPO = "/workspace/hugo"


def test_chmodFilter_behavior():
    """Test chmodFilter actual behavior with file system simulation.

    This test:
    1. Creates a Go test file inside the Hugo commands package
    2. Runs the Go test which creates temp files/dirs and tests
       whether chmodFilter correctly identifies which to skip

    The Go test file exercises three scenarios:
    - Directory: should return true (skip permission sync)
    - File mode 0444 (no owner-write): should return true (skip)
    - File mode 0644 (has owner-write): should return false (sync)
    """
    # Go test content that will be injected into Hugo's commands package
    go_test_content = '''package commands

import (
	"os"
	"path/filepath"
	"testing"
)

func TestChmodFilterBehavior(t *testing.T) {
	// Create temp directory for test files
	tmpDir, err := os.MkdirTemp("", "chmodfilter_test")
	if err != nil {
		t.Fatal("cannot create temp dir:", err)
	}
	defer os.RemoveAll(tmpDir)

	// Test case 1: directory should return true (skip)
	dirPath := filepath.Join(tmpDir, "testdir")
	if err := os.Mkdir(dirPath, 0755); err != nil {
		t.Fatal("cannot create temp dir:", err)
	}
	dirInfo, err := os.Stat(dirPath)
	if err != nil {
		t.Fatal("cannot stat dir:", err)
	}
	if !chmodFilter(nil, dirInfo) {
		t.Error("chmodFilter should return true for directories")
	}

	// Test case 2: file with mode 0444 (no owner-write) should return true (skip)
	// This is the bug case - files from Go module cache
	file0444 := filepath.Join(tmpDir, "file0444.txt")
	if err := os.WriteFile(file0444, []byte("test"), 0444); err != nil {
		t.Fatal("cannot create 0444 file:", err)
	}
	info0444, err := os.Stat(file0444)
	if err != nil {
		t.Fatal("cannot stat 0444 file:", err)
	}
	if !chmodFilter(nil, info0444) {
		t.Error("chmodFilter should return true for 0444 files (no owner-write)")
	}

	// Test case 3: file with mode 0644 (has owner-write) should return false (sync)
	file0644 := filepath.Join(tmpDir, "file0644.txt")
	if err := os.WriteFile(file0644, []byte("test"), 0644); err != nil {
		t.Fatal("cannot create 0644 file:", err)
	}
	info0644, err := os.Stat(file0644)
	if err != nil {
		t.Fatal("cannot stat 0644 file:", err)
	}
	if chmodFilter(nil, info0644) {
		t.Error("chmodFilter should return false for 0644 files (has owner-write)")
	}
}
'''

    # Write the Go test file
    test_file = os.path.join(REPO, "commands", "chmodfilter_behavior_test.go")
    with open(test_file, "w") as f:
        f.write(go_test_content)

    try:
        # Run the Go test
        result = subprocess.run(
            ["go", "test", "-v", "-count=1", "-run", "TestChmodFilterBehavior", "./commands/"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=120
        )

        # Assert test passed
        assert result.returncode == 0, \
            f"chmodFilter behavioral tests failed:\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"

        # Verify specific test passed
        assert "TestChmodFilterBehavior" in result.stdout, \
            f"TestChmodFilterBehavior did not run. stdout:\n{result.stdout}"

        # Verify all assertions passed (no Error calls)
        assert "chmodFilter should return true for directories" not in result.stdout, \
            f"Directory test failed:\n{result.stdout}"
        assert "chmodFilter should return true for 0444 files" not in result.stdout, \
            f"0444 file test failed:\n{result.stdout}"
        assert "chmodFilter should return false for 0644 files" not in result.stdout, \
            f"0644 file test failed:\n{result.stdout}"
    finally:
        # Clean up the test file
        if os.path.exists(test_file):
            os.unlink(test_file)


def test_compilation():
    """Verify Hugo compiles successfully."""
    result = subprocess.run(
        ["go", "build", "-o", "/tmp/hugo_test", "."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"Hugo compilation failed:\n{result.stderr}"


def test_staticcheck():
    """Run staticcheck on the commands package."""
    result = subprocess.run(
        ["staticcheck", "./commands/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )
    assert result.returncode == 0, f"staticcheck failed:\n{result.stdout}\n{result.stderr}"


def test_commands_tests():
    """Run Go tests for the commands package."""
    result = subprocess.run(
        ["go", "test", "-v", "./commands/...", "-run", "TestServer"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )
    if result.returncode != 0:
        if "no tests" in result.stderr.lower() or "no tests" in result.stdout.lower():
            pytest.skip("No matching tests found")
        assert False, f"Go tests failed:\n{result.stderr}"


def test_gofmt():
    """Verify Go code is properly formatted."""
    result = subprocess.run(
        ["gofmt", "-l", "."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )
    assert result.returncode == 0, f"gofmt check failed:\n{result.stderr}"
    assert result.stdout.strip() == "", f"Unformatted Go files found:\n{result.stdout}"


def test_go_vet():
    """Run go vet on the commands package."""
    result = subprocess.run(
        ["go", "vet", "./commands/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"go vet failed:\n{result.stdout}\n{result.stderr}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])