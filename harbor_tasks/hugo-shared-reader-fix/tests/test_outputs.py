"""
Test suite for Hugo PR #14685: Fix shared reader in Source.ValueAsOpenReadSeekCloser

The bug: ValueAsOpenReadSeekCloser returned a closure that shared the same
reader instance. When multiple readers were opened, they would interfere with
each other's position.

The fix: Each call to the opener must return a new independent reader.
"""

import subprocess
import sys
import os
import io
import tempfile

REPO = "/workspace/hugo"


def test_reader_independence_f2p():
    """
    Fail-to-pass test: Verifies that multiple readers from ValueAsOpenReadSeekCloser
    are independent and don't share position state.

    This test creates a Go program that directly tests the behavior and verifies
    that the fix is in place (readers must be independent).
    """
    # Create a Go test file that directly tests the behavior
    test_code = '''package main

import (
	"fmt"
	"io"
	"os"
	"github.com/gohugoio/hugo/resources/page/pagemeta"
)

func main() {
	s := pagemeta.Source{Value: "abcdefgh"}
	opener := s.ValueAsOpenReadSeekCloser()

	r1, err := opener()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Failed to open r1: %v\\n", err)
		os.Exit(1)
	}
	defer r1.Close()

	// Partially consume r1 (read first 4 bytes)
	buf := make([]byte, 4)
	_, err = io.ReadFull(r1, buf)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Failed to read from r1: %v\\n", err)
		os.Exit(1)
	}
	if string(buf) != "abcd" {
		fmt.Fprintf(os.Stderr, "Expected 'abcd', got '%s'\\n", string(buf))
		os.Exit(1)
	}

	// Open a second reader and fully consume it
	r2, err := opener()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Failed to open r2: %v\\n", err)
		os.Exit(1)
	}
	defer r2.Close()

	all, err := io.ReadAll(r2)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Failed to read from r2: %v\\n", err)
		os.Exit(1)
	}
	if string(all) != "abcdefgh" {
		fmt.Fprintf(os.Stderr, "Expected 'abcdefgh', got '%s'\\n", string(all))
		os.Exit(1)
	}

	// r1's position must be unaffected; it should yield the remaining half (efgh)
	rest, err := io.ReadAll(r1)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Failed to read rest from r1: %v\\n", err)
		os.Exit(1)
	}
	if string(rest) != "efgh" {
		fmt.Fprintf(os.Stderr, "BUG: Readers are NOT independent! Expected 'efgh', got '%s'\\n", string(rest))
		os.Exit(1)
	}

	fmt.Println("SUCCESS: Readers are independent")
}
'''

    # Write the test file
    test_file = os.path.join(REPO, "test_independence.go")
    with open(test_file, "w") as f:
        f.write(test_code)

    try:
        # Run the test
        result = subprocess.run(
            ["go", "run", "test_independence.go"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=120
        )

        # After the fix, this should pass (exit code 0 with "SUCCESS")
        # Before the fix, this should fail (exit code 1 with "BUG: Readers are NOT independent")
        if result.returncode == 0 and "SUCCESS" in result.stdout:
            return  # Test passed - fix is in place

        # Check if it's the expected bug behavior
        if "BUG: Readers are NOT independent" in result.stderr:
            raise AssertionError(
                "Bug detected: Readers from ValueAsOpenReadSeekCloser are NOT independent. "
                "This is the bug that needs to be fixed. "
                f"Output: {result.stderr}"
            )

        # Some other error
        raise AssertionError(
            f"Test failed with unexpected error:\n"
            f"Stdout: {result.stdout}\n"
            f"Stderr: {result.stderr}"
        )
    finally:
        # Clean up
        if os.path.exists(test_file):
            os.remove(test_file)


def test_opener_returns_new_reader_f2p():
    """
    Fail-to-pass test: Verifies that each call to the opener returns a new reader.

    This tests the specific implementation detail that was buggy - the old code
    returned a closure that captured a pre-created reader, while the fix creates
    a new reader on each call.
    """
    # Create a Go test file
    test_code = '''package main

import (
	"fmt"
	"io"
	"os"
	"github.com/gohugoio/hugo/resources/page/pagemeta"
)

func main() {
	s := pagemeta.Source{Value: "test content"}
	opener := s.ValueAsOpenReadSeekCloser()

	// Open two readers
	r1, err := opener()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Failed to open r1: %v\\n", err)
		os.Exit(1)
	}
	defer r1.Close()

	r2, err := opener()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Failed to open r2: %v\\n", err)
		os.Exit(1)
	}
	defer r2.Close()

	// Read all from both
	content1, err := io.ReadAll(r1)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Failed to read r1: %v\\n", err)
		os.Exit(1)
	}

	content2, err := io.ReadAll(r2)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Failed to read r2: %v\\n", err)
		os.Exit(1)
	}

	// Both should have the full content
	expected := "test content"
	if string(content1) != expected || string(content2) != expected {
		fmt.Fprintf(os.Stderr, "BUG: Readers don't have full content: r1='%s', r2='%s'\\n",
			string(content1), string(content2))
		os.Exit(1)
	}

	fmt.Println("SUCCESS")
}
'''

    test_file = os.path.join(REPO, "test_opener.go")
    with open(test_file, "w") as f:
        f.write(test_code)

    try:
        result = subprocess.run(
            ["go", "run", "test_opener.go"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=120
        )

        if result.returncode == 0 and "SUCCESS" in result.stdout:
            return

        if "BUG" in result.stderr:
            raise AssertionError(
                f"Bug detected: {result.stderr}"
            )

        raise AssertionError(
            f"Test failed:\nStdout: {result.stdout}\nStderr: {result.stderr}"
        )
    finally:
        if os.path.exists(test_file):
            os.remove(test_file)


def test_pagemeta_package_p2p():
    """
    Pass-to-pass test: The repo's own pagemeta package tests must continue to pass.
    """
    result = subprocess.run(
        ["go", "test", "-v", "./resources/page/pagemeta/"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )

    assert result.returncode == 0, (
        f"Package tests failed!\n"
        f"Stdout: {result.stdout[-1000:]}\n"
        f"Stderr: {result.stderr[-1000:]}"
    )


def test_go_build_p2p():
    """
    Pass-to-pass test: Hugo must build successfully.
    """
    result = subprocess.run(
        ["go", "build", "-o", "/tmp/hugo_test", "./"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180
    )

    assert result.returncode == 0, (
        f"Build failed!\n"
        f"Stdout: {result.stdout[-1000:]}\n"
        f"Stderr: {result.stderr[-1000:]}"
    )


def test_code_compiles_p2p():
    """
    Pass-to-pass test: Code must pass go vet checks.
    """
    result = subprocess.run(
        ["go", "vet", "./resources/page/pagemeta/"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )

    assert result.returncode == 0, (
        f"go vet failed!\n"
        f"Stderr: {result.stderr[-1000:]}"
    )


def test_specific_unit_tests_p2p():
    """
    Pass-to-pass test: Run existing pagemeta tests (excluding the new ones that don't exist yet).
    """
    result = subprocess.run(
        ["go", "test", "-v", "-run", "TestFrontMatter|TestSource", "./resources/page/pagemeta/"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )

    assert result.returncode == 0, (
        f"Unit tests failed!\n"
        f"Stdout: {result.stdout[-1000:]}\n"
        f"Stderr: {result.stderr[-1000:]}"
    )


def test_gofmt_check_p2p():
    """
    Pass-to-pass test: Repo code must pass gofmt check.
    CI enforces this via check_gofmt.sh.
    """
    result = subprocess.run(
        ["gofmt", "-l", "."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )

    # gofmt returns 0 even if it finds issues, but outputs file names
    assert result.returncode == 0, f"gofmt check failed:\n{result.stderr}"
    assert result.stdout.strip() == "", (
        f"gofmt found formatting issues in:\n{result.stdout}"
    )


def test_go_mod_verify_p2p():
    """
    Pass-to-pass test: Go module dependencies must verify.
    Ensures go.sum is consistent with go.mod.
    """
    result = subprocess.run(
        ["go", "mod", "verify"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )

    assert result.returncode == 0, (
        f"Go module verification failed!\n"
        f"Stderr: {result.stderr[-500:]}"
    )


def test_pagemeta_staticcheck_p2p():
    """
    Pass-to-pass test: staticcheck passes on pagemeta package.
    CI runs staticcheck on all packages.
    """
    # Install staticcheck first
    install_result = subprocess.run(
        ["go", "install", "honnef.co/go/tools/cmd/staticcheck@latest"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )

    # Run staticcheck on pagemeta package
    result = subprocess.run(
        ["staticcheck", "./resources/page/pagemeta/"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )

    assert result.returncode == 0, (
        f"staticcheck failed!\n"
        f"Stderr: {result.stderr[-500:]}\n"
        f"Stdout: {result.stdout[-500:]}"
    )
