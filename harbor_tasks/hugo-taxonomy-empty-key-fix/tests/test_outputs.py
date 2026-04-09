"""
Tests for Hugo taxonomy configuration fix.

This test verifies that the fix for issue #14550 correctly handles
taxonomy entries with empty keys or values, which could be created
when non-taxonomy keys are placed after [taxonomies] in TOML config.
"""

import subprocess
import os
import tempfile
import shutil
import pytest

REPO_PATH = "/workspace/hugo"


def run_go_test(test_pattern, timeout=60):
    """Run a specific Go test and return the result."""
    result = subprocess.run(
        ["go", "test", "-v", "-run", test_pattern, "-timeout", f"{timeout}s"],
        cwd=REPO_PATH,
        capture_output=True,
        text=True
    )
    return result


def test_taxonomy_empty_key_value_fix():
    """
    Test that taxonomy entries with empty keys or values are filtered out.
    This is a fail-to-pass test that verifies the fix for issue #14550.

    This test directly checks the alldecoders.go code contains the fix
    that filters out invalid taxonomy entries with empty keys or values.
    """
    # Read the alldecoders.go file and verify the fix is present
    decoder_file = os.path.join(REPO_PATH, "config/allconfig/alldecoders.go")

    with open(decoder_file, "r") as f:
        content = f.read()

    # Check that the fix is present: filtering out entries with empty keys or values
    # The fix should have a loop that deletes entries where k == "" or v == ""
    assert "for k, v := range m" in content, (
        "Missing taxonomy filtering loop - fix not applied"
    )
    assert 'if k == "" || v == ""' in content or "if k == \"\" || v == \"\"" in content, (
        "Missing empty key/value check - fix not applied"
    )
    assert "delete(m, k)" in content, (
        "Missing delete statement for invalid entries - fix not applied"
    )


def test_ancestors_does_not_hang():
    """
    Test that .Ancestors does not loop indefinitely when phantom taxonomies exist.
    This is a regression test for the hanging behavior described in issue #14550.

    We test this by creating a Hugo site with a config that would create phantom
    taxonomies (disableKinds=[] inside [taxonomies]), then verify Hugo builds
    without hanging.
    """
    import tempfile
    import subprocess

    # Create a minimal Hugo site with problematic config
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create config with issue #14550 pattern
        config_content = """baseURL = "http://example.com/"
title = "Bug repro"
[taxonomies]
  tag = "tags"
disableKinds = []
"""
        # Write config
        config_path = os.path.join(tmpdir, "hugo.toml")
        with open(config_path, "w") as f:
            f.write(config_content)

        # Create minimal content
        content_dir = os.path.join(tmpdir, "content")
        os.makedirs(content_dir, exist_ok=True)

        post_content = """---
title: Hello
tags: [demo]
---
Hello.
"""
        post_path = os.path.join(content_dir, "hello.md")
        with open(post_path, "w") as f:
            f.write(post_content)

        # Create minimal layouts
        layouts_dir = os.path.join(tmpdir, "layouts")
        os.makedirs(layouts_dir, exist_ok=True)

        page_layout = "Page: {{ .Title }}\n"
        with open(os.path.join(layouts_dir, "page.html"), "w") as f:
            f.write(page_layout)

        list_layout = "List: {{ .Title }}\n"
        with open(os.path.join(layouts_dir, "list.html"), "w") as f:
            f.write(list_layout)

        # Try to build the site with timeout to detect hangs
        # First ensure Hugo is built
        build_result = subprocess.run(
            ["go", "build", "-o", "/tmp/hugo_test", "."],
            capture_output=True, text=True, timeout=120, cwd=REPO_PATH,
            env={**os.environ, "GOTOOLCHAIN": "auto"}
        )
        if build_result.returncode != 0:
            pytest.fail(f"Failed to build Hugo: {build_result.stderr}")

        try:
            result = subprocess.run(
                ["/tmp/hugo_test", "--source", tmpdir, "--destination", os.path.join(tmpdir, "public")],
                capture_output=True,
                text=True,
                timeout=30,  # If it hangs, this will timeout
                cwd=tmpdir
            )
            # Build should succeed without hanging
            # Note: We allow failure as long as it doesn't hang
            # The key is that we got here without a timeout
        except subprocess.TimeoutExpired:
            pytest.fail("Hugo build timed out - likely hanging due to phantom taxonomy bug")


def test_taxonomy_config_filtering():
    """
    Test that the taxonomy decoder correctly filters invalid entries.
    This tests the actual fix in config/allconfig/alldecoders.go.
    """
    # This is a duplicate of test_taxonomy_empty_key_value_fix - it tests the same fix
    # Both tests verify the fix in alldecoders.go that filters out invalid taxonomy entries
    decoder_file = os.path.join(REPO_PATH, "config/allconfig/alldecoders.go")

    with open(decoder_file, "r") as f:
        content = f.read()

    # Check that the fix is present: filtering out entries with empty keys or values
    assert "for k, v := range m" in content, (
        "Missing taxonomy filtering loop - fix not applied"
    )
    assert 'if k == "" || v == ""' in content or "if k == \"\" || v == \"\"" in content, (
        "Missing empty key/value check - fix not applied"
    )
    assert "delete(m, k)" in content, (
        "Missing delete statement for invalid entries - fix not applied"
    )


def test_new_test_uses_correct_layout_paths():
    """
    Verify that tests use the latest Hugo layout specification.
    This is a pass-to-pass test from AGENTS.md agent config.

    This test validates the AGENTS.md guideline:
    "In tests, always use the latest Hugo specification, e.g. for layouts,
    it's layouts/page.html and not layouts/_default/single.html"
    """
    # Check that the codebase follows the AGENTS.md guideline for layout paths
    # We verify that any test using the modern layout pattern exists
    test_file = os.path.join(REPO_PATH, "hugolib", "disableKinds_test.go")

    with open(test_file, "r") as f:
        content = f.read()

    # Check for modern layout patterns per AGENTS.md:
    # layouts/page.html (not layouts/_default/single.html)
    # layouts/list.html (not layouts/_default/list.html)
    has_modern_single = "layouts/page.html" in content
    has_modern_list = "layouts/list.html" in content
    has_legacy_single = "layouts/_default/single.html" in content
    has_legacy_list = "layouts/_default/list.html" in content

    # The codebase should either use modern paths or not use the old ones
    # If the new test TestDisableKindsEmptySliceAncestors exists, it must use modern paths
    if "TestDisableKindsEmptySliceAncestors" in content:
        # The new test must use modern layout paths
        assert has_modern_single or has_modern_list, (
            "TestDisableKindsEmptySliceAncestors should use modern layout paths "
            "(layouts/page.html, layouts/list.html) per AGENTS.md guidelines"
        )
        assert not has_legacy_single and not has_legacy_list, (
            "TestDisableKindsEmptySliceAncestors should not use legacy layout paths "
            "(layouts/_default/single.html, layouts/_default/list.html)"
        )


def test_repo_go_vet():
    """Repo's Go vet passes (pass_to_pass)."""
    r = subprocess.run(
        ["go", "vet", "./config/..."],
        capture_output=True, text=True, timeout=120, cwd=REPO_PATH,
        env={**os.environ, "GOTOOLCHAIN": "auto"}
    )
    assert r.returncode == 0, f"Go vet failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


def test_repo_gofmt():
    """Repo's Go code is properly formatted (pass_to_pass)."""
    r = subprocess.run(
        ["gofmt", "-l", "./config/allconfig"],
        capture_output=True, text=True, timeout=60, cwd=REPO_PATH,
    )
    # gofmt -l returns empty output if all files are properly formatted
    assert r.returncode == 0, f"gofmt check failed:\n{r.stderr}"
    assert r.stdout.strip() == "", f"Files need formatting:\n{r.stdout}"


def test_repo_build():
    """Repo builds successfully (pass_to_pass)."""
    r = subprocess.run(
        ["go", "build", "./..."],
        capture_output=True, text=True, timeout=120, cwd=REPO_PATH,
        env={**os.environ, "GOTOOLCHAIN": "auto"}
    )
    assert r.returncode == 0, f"Build failed:\n{r.stderr[-500:]}"


def test_repo_config_tests():
    """Existing config package tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["go", "test", "-v", "./config/allconfig", "-run", "TestConfigAliases"],
        capture_output=True, text=True, timeout=120, cwd=REPO_PATH,
        env={**os.environ, "GOTOOLCHAIN": "auto"}
    )
    assert r.returncode == 0, f"Config tests failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"
    assert "PASS: TestConfigAliases" in r.stdout or "PASS\n" in r.stdout, (
        f"Test did not pass. Output:\n{r.stdout}"
    )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
