#!/usr/bin/env python3
"""
Tests for Hugo PR #14651: Fix Vimeo shortcode test

This PR fixes the Vimeo shortcode test by:
1. Replacing an unavailable video ID with a working one
2. Re-enabling the simple mode tests that were commented out

Tests verify BEHAVIOR, not specific gold values.
"""

import subprocess
import re
import sys

REPO = "/workspace/hugo"


def test_vimeo_shortcode_passes():
    """Vimeo shortcode integration test passes (fail_to_pass)."""
    result = subprocess.run(
        ["go", "test", "-v", "-run", "TestVimeoShortcode", "./tpl/tplimpl/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert result.returncode == 0, f"TestVimeoShortcode failed:\n{result.stdout}\n{result.stderr}"


def test_vimeo_video_id_updated():
    """Vimeo template uses a different (non-broken) video ID (fail_to_pass)."""
    with open(f"{REPO}/tpl/tplimpl/embedded/templates/_shortcodes/vimeo.html", "r") as f:
        content = f.read()

    # The BROKEN video ID should NOT be present in the template
    # ANY valid fix must change this broken ID
    assert "55073825" not in content, "Vimeo template should NOT use the broken video ID 55073825"


def test_vimeo_test_uses_correct_id():
    """Integration test file uses a different (non-broken) video ID (fail_to_pass)."""
    with open(f"{REPO}/tpl/tplimpl/shortcodes_integration_test.go", "r") as f:
        content = f.read()

    # The BROKEN video ID should NOT be present in the test file
    assert "55073825" not in content, "Test should NOT use the broken video ID 55073825"


def test_simple_mode_enabled():
    """Simple mode tests are re-enabled (not commented out) (fail_to_pass)."""
    with open(f"{REPO}/tpl/tplimpl/shortcodes_integration_test.go", "r") as f:
        content = f.read()

    # The comment referencing issue #14649 should NOT be present
    # This is a structural change, not a gold-specific value
    assert "// Commented out for now, see issue #14649" not in content, \
        "Simple mode tests should not be commented out"

    # Verify the simple mode privacy override is NOT commented out
    # Count how many times the ReplaceAll line appears - should be uncommented
    replaceall_count = content.count('files = strings.ReplaceAll(files, "privacy.vimeo.simple = false", "privacy.vimeo.simple = true")')
    assert replaceall_count >= 1, "Simple mode ReplaceAll should be present (uncommented)"


def test_vimeo_hashes_updated():
    """Integration test has hash assertions for Vimeo output (fail_to_pass)."""
    with open(f"{REPO}/tpl/tplimpl/shortcodes_integration_test.go", "r") as f:
        content = f.read()

    # The test should have file content assertions for the Vimeo pages
    # We check these exist (the specific hash values depend on the video ID used)
    # This verifies the test has been properly configured, not just stubbed out
    assert 'b.AssertFileContent("public/p1/index.html"' in content, \
        "Regular mode p1 test should have file content assertion"
    assert 'b.AssertFileContent("public/p3/index.html"' in content, \
        "Regular mode p3 test should have file content assertion"


def test_repo_tests_compile():
    """Repo tests compile without errors (pass_to_pass)."""
    result = subprocess.run(
        ["go", "build", "./..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert result.returncode == 0, f"Build failed:\n{result.stderr}"


def test_repo_vet_passes():
    """Repo passes go vet (pass_to_pass)."""
    result = subprocess.run(
        ["go", "vet", "./tpl/tplimpl/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"Go vet failed:\n{result.stderr}"


def test_repo_unit_tests():
    """Repo unit tests for modified package pass (pass_to_pass)."""
    result = subprocess.run(
        ["go", "test", "-count=1", "./tpl/tplimpl/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert result.returncode == 0, f"Unit tests failed:\n{result.stderr}"


def test_repo_gofmt():
    """Repo passes gofmt check (pass_to_pass)."""
    result = subprocess.run(
        ["gofmt", "-l", "./tpl/tplimpl/"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    # gofmt -l returns 0 but outputs file names if there are issues
    assert result.returncode == 0, f"gofmt check failed:\n{result.stderr}"
    assert result.stdout.strip() == "", f"gofmt found issues in:\n{result.stdout}"


def test_repo_go_mod_verify():
    """Repo Go modules verify (pass_to_pass)."""
    result = subprocess.run(
        ["go", "mod", "verify"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, f"Go mod verify failed:\n{result.stderr}"


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v", "--tb=short"]))
