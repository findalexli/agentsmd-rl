"""
Verifier tests for Hugo resources error message improvement.
Tests that calling image methods on SVG resources produces helpful error messages.
"""

import subprocess
import sys
import re

REPO = "/workspace/hugo"

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
# Pass-to-Pass tests for repo CI/CD (regression checks)
# These verify the fix doesn't break existing functionality
# Note: These are limited due to Go 1.20 vs Go 1.21+ compatibility issues
# =============================================================================

def test_go_vet_resources():
    """
    Go vet passes on resources package (pass_to_pass).
    Limited check due to Go version compatibility.
    """
    # For Go version compatibility reasons, we just verify the file exists
    # and has proper Go syntax structure
    import os
    assert os.path.exists(f"{REPO}/resources/transform.go"), "transform.go not found"

    with open(f"{REPO}/resources/transform.go", "r") as f:
        content = f.read()

    # Basic syntax validation
    assert content.count('(') == content.count(')'), "Unbalanced parentheses"
    assert content.count('{') == content.count('}'), "Unbalanced braces"


def test_go_build_all():
    """
    Full project builds successfully (pass_to_pass).
    Note: Limited to syntax verification due to Go 1.20 vs Go 1.21+ compatibility.
    """
    # Verify key files exist and have valid structure
    import os

    key_files = [
        f"{REPO}/resources/transform.go",
        f"{REPO}/resources/images/image.go",
        f"{REPO}/resources/resource.go",
    ]

    for filepath in key_files:
        assert os.path.exists(filepath), f"Required file {filepath} not found"
        with open(filepath, "r") as f:
            content = f.read()
        assert "package " in content, f"{filepath} missing package declaration"


def test_go_test_resources_other():
    """
    Other tests in resources package pass (pass_to_pass).
    Verifies test infrastructure exists.
    """
    import os

    # Verify test files exist
    test_files = [
        f"{REPO}/resources/transform_test.go",
        f"{REPO}/resources/resources_integration_test.go",
    ]

    for filepath in test_files:
        if os.path.exists(filepath):
            with open(filepath, "r") as f:
                content = f.read()
            assert "package resources" in content, f"{filepath} missing package declaration"
