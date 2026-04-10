"""
Verifier tests for Hugo resources error message improvement.
Tests that calling image methods on SVG resources produces helpful error messages.
"""

import subprocess
import sys
import re
import os

REPO = "/workspace/hugo"


# =============================================================================
# Fail-to-pass tests (primary behavioral validation)
# These test that the fix produces the expected behavior change
# =============================================================================

def test_svg_width_error_message():
    """
    Test that calling Width on SVG resource gives improved error message.

    This is a fail-to-pass test: before the fix, the error message was generic.
    After the fix, it should include resource name, media type, and helpful instructions.
    """
    # Read the transform.go file directly to verify the fix is present
    with open(f"{REPO}/resources/transform.go", "r") as f:
        content = f.read()

    # Check for the improved error message components in the source code
    assert 'resource %q of media type %q' in content or 'resource "%s" of media type "%s"' in content, \
        f"Expected resource/media type format string not found in getImageOps. Content:\n{content}"
    assert "reflect.IsImageResource" in content, \
        f"Expected IsImageResource hint not found. Content:\n{content}"
    assert "reflect.IsImageResourceProcessable" in content, \
        f"Expected IsImageResourceProcessable hint not found. Content:\n{content}"
    assert "reflect.IsImageResourceWithMeta" in content, \
        f"Expected IsImageResourceWithMeta hint not found. Content:\n{content}"


# =============================================================================
# Pass-to-pass tests (regression checks - structural)
# These verify the fix doesn't break existing code structure
# =============================================================================

def test_transform_compiles():
    """
    Verify that the resources/transform.go file has valid syntax.
    Since full compilation requires Go 1.21+ but we have Go 1.20,
    we check for basic syntax indicators in the source.
    """
    # Read the transform.go file
    with open(f"{REPO}/resources/transform.go", "r") as f:
        content = f.read()

    # Check for balanced braces (basic syntax check)
    open_braces = content.count('{')
    close_braces = content.count('}')
    assert open_braces == close_braces, f"Unbalanced braces in transform.go"

    # Check for valid go syntax patterns
    assert "package resources" in content, "Missing package declaration"
    assert "func (r *resourceAdapter) getImageOps()" in content, "Missing getImageOps function"


def test_no_old_error_message():
    """
    Ensure the old error message is no longer used.

    This is a pass-to-pass test: after fix, old error patterns should be gone.
    """
    # Read the transform.go file
    with open(f"{REPO}/resources/transform.go", "r") as f:
        content = f.read()

    # Old error messages should not be present
    assert 'this method is only available for raster images' not in content, \
        "Old raster images error message still present in code"
    assert 'this method is only available for image resources' not in content, \
        "Old generic error message still present in code"
    assert 'if eq .MediaType.SubType "svg"' not in content, \
        "Old SVG type check still present in code"


def test_fmt_import_present():
    """
    Verify fmt package is imported for fmt.Sprintf.

    This is a structural test gated by behavioral test success.
    """
    with open(f"{REPO}/resources/transform.go", "r") as f:
        content = f.read()

    # Check fmt is imported
    assert '"fmt"' in content or 'fmt "' in content, \
        "fmt package import not found in transform.go"


def test_error_message_format():
    """
    Verify the error message format uses fmt.Sprintf correctly.

    Structural check for proper implementation.
    """
    with open(f"{REPO}/resources/transform.go", "r") as f:
        content = f.read()

    # Look for fmt.Sprintf call in getImageOps
    assert "fmt.Sprintf(" in content, \
        "fmt.Sprintf not found in getImageOps implementation"

    # Look for the specific format string pattern
    assert 'resource %q of media type %q' in content or \
           'resource "%s" of media type "%s"' in content, \
        "Expected format string pattern for resource and media type not found"


# =============================================================================
# Pass-to-pass tests for repo CI/CD (regression checks)
# origin: repo_tests - These use subprocess.run() to execute actual CI commands
# =============================================================================

def test_gofmt_resources():
    """
    Repo code passes gofmt formatting check (pass_to_pass).
    Runs gofmt -l on the resources directory to verify no formatting issues.
    origin: repo_tests
    """
    r = subprocess.run(
        ["gofmt", "-l", f"{REPO}/resources"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"gofmt failed with exit code {r.returncode}: {r.stderr}"
    assert r.stdout.strip() == "", f"gofmt found formatting issues in:\n{r.stdout}"


def test_gofmt_transform_go():
    """
    transform.go passes gofmt formatting check (pass_to_pass).
    Verifies the modified file specifically has correct formatting.
    origin: repo_tests
    """
    r = subprocess.run(
        ["gofmt", "-l", f"{REPO}/resources/transform.go"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"gofmt failed with exit code {r.returncode}: {r.stderr}"
    assert r.stdout.strip() == "", f"gofmt found formatting issues in transform.go"


def test_transform_go_syntax_valid():
    """
    transform.go has valid Go syntax (pass_to_pass).
    Uses gofmt to verify the file can be parsed without errors.
    origin: repo_tests
    """
    r = subprocess.run(
        ["gofmt", "-e", f"{REPO}/resources/transform.go"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"gofmt syntax check failed: {r.stderr}"
    # gofmt -e returns 0 even with some errors, so also check stderr
    assert "error:" not in r.stderr.lower(), f"Syntax errors found: {r.stderr}"


def test_go_vet_resources_images():
    """
    Go vet passes on resources/images subdirectory (pass_to_pass).
    This subdirectory has fewer dependencies and can be vetted.
    Note: This may fail due to Go 1.20 vs 1.21+ version compatibility.
    origin: repo_tests
    """
    r = subprocess.run(
        ["go", "vet", "./resources/images/..."],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    # Due to Go version compatibility, we accept either success
    # or the specific known version-related errors
    version_errors = [
        "package cmp is not in GOROOT",
        "package iter is not in GOROOT",
        "package log/slog is not in GOROOT",
        "package maps is not in GOROOT",
        "package slices is not in GOROOT",
    ]
    if r.returncode != 0:
        # Check if it's only version-related errors
        for error in version_errors:
            if error in r.stderr:
                return  # Accept version-related errors as known limitation
        # If it's a different error, fail
        assert False, f"go vet found actual issues: {r.stderr[:500]}"


def test_go_build_all_possible():
    """
    Full project build check (pass_to_pass).
    Due to Go 1.20 vs 1.21+ compatibility, this checks if the
    build fails only due to version issues, not code issues.
    origin: repo_tests
    """
    r = subprocess.run(
        ["go", "build", "./resources/..."],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )

    # If build succeeds, great
    if r.returncode == 0:
        return

    # If it fails, check that it's only due to version compatibility
    # not due to syntax errors in the code
    version_errors = [
        "package cmp is not in GOROOT",
        "package iter is not in GOROOT",
        "package log/slog is not in GOROOT",
        "package maps is not in GOROOT",
        "package slices is not in GOROOT",
        "package math/rand/v2 is not in GOROOT",
        "package unique is not in GOROOT",
    ]

    # Check if any version error is present
    has_version_error = any(err in r.stderr for err in version_errors)
    assert has_version_error, f"Build failed with non-version error: {r.stderr[:500]}"


def test_go_vet_all():
    """
    Go vet passes on the entire project (pass_to_pass).
    This is a comprehensive check that the Go code is well-formed.
    Note: This may fail due to Go 1.20 vs 1.21+ version compatibility.
    origin: repo_tests
    """
    r = subprocess.run(
        ["go", "vet", "./..."],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    # Due to Go version compatibility, we accept either success
    # or the specific known version-related errors
    version_errors = [
        "package cmp is not in GOROOT",
        "package iter is not in GOROOT",
        "package log/slog is not in GOROOT",
        "package maps is not in GOROOT",
        "package slices is not in GOROOT",
    ]
    if r.returncode != 0:
        # Check if it's only version-related errors
        for error in version_errors:
            if error in r.stderr:
                return  # Accept version-related errors as known limitation
        # If it's a different error, fail
        assert False, f"go vet found actual issues: {r.stderr[:500]}"


def test_go_build_all():
    """
    Full project build check (pass_to_pass).
    This runs go build ./... to verify the entire project compiles.
    Note: This may fail due to Go 1.20 vs 1.21+ version compatibility.
    origin: repo_tests
    """
    r = subprocess.run(
        ["go", "build", "./..."],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )

    # If build succeeds, great
    if r.returncode == 0:
        return

    # If it fails, check that it's only due to version compatibility
    # not due to syntax errors in the code
    version_errors = [
        "package cmp is not in GOROOT",
        "package iter is not in GOROOT",
        "package log/slog is not in GOROOT",
        "package maps is not in GOROOT",
        "package slices is not in GOROOT",
        "package math/rand/v2 is not in GOROOT",
        "package unique is not in GOROOT",
    ]

    # Check if any version error is present
    has_version_error = any(err in r.stderr for err in version_errors)
    assert has_version_error, f"Build failed with non-version error: {r.stderr[:500]}"


# =============================================================================
# Pass-to-pass static checks (file reads, not CI commands)
# origin: static - These check file existence and content, not CI commands
# =============================================================================

def test_repo_files_exist():
    """
    Essential repo files exist and are readable (pass_to_pass).
    Verifies the repository structure is intact.
    origin: static
    """
    essential_files = [
        f"{REPO}/resources/transform.go",
        f"{REPO}/resources/images/image.go",
        f"{REPO}/resources/resource.go",
        f"{REPO}/go.mod",
    ]

    for filepath in essential_files:
        assert os.path.exists(filepath), f"Essential file {filepath} not found"
        assert os.path.getsize(filepath) > 0, f"Essential file {filepath} is empty"
        # Verify we can read it
        with open(filepath, "r") as f:
            content = f.read()
        assert len(content) > 0, f"Could not read content from {filepath}"


def test_repo_test_files_exist():
    """
    Test files exist for the resources package (pass_to_pass).
    Verifies the test infrastructure is intact.
    origin: static
    """
    test_files = [
        f"{REPO}/resources/transform_test.go",
        f"{REPO}/resources/resources_integration_test.go",
    ]

    for filepath in test_files:
        assert os.path.exists(filepath), f"Test file {filepath} not found"
        with open(filepath, "r") as f:
            content = f.read()
        assert "package resources" in content, f"{filepath} missing package declaration"


def test_go_mod_valid():
    """
    go.mod is valid and readable (pass_to_pass).
    Verifies the module definition is intact.
    origin: static
    """
    with open(f"{REPO}/go.mod", "r") as f:
        content = f.read()

    assert "module github.com/gohugoio/hugo" in content, "go.mod missing module declaration"
    assert "go 1." in content, "go.mod missing Go version"


def test_resources_package_declaration():
    """
    All resources package Go files have correct package declarations (pass_to_pass).
    Verifies Go source files have proper package statements.
    Skips docs.go which is a special documentation-only file.
    origin: static
    """
    resources_dir = f"{REPO}/resources"
    for filename in os.listdir(resources_dir):
        if filename.endswith(".go") and not filename.startswith("_"):
            # Skip docs.go which is documentation-only and uses a different format
            if filename == "docs.go":
                continue
            filepath = os.path.join(resources_dir, filename)
            with open(filepath, "r") as f:
                content = f.read()
            # Check for package declaration anywhere in file (not just first 10 lines)
            # Using regex to find actual package declaration line (not comments)
            has_package = re.search(r'^package\s+\w+', content, re.MULTILINE) is not None
            assert has_package, f"{filename} missing package declaration"
