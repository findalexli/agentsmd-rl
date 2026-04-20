"""
Test suite for Hugo taxonomy empty key fix.
Tests that taxonomy entries with empty keys or values are filtered out.
"""

import os
import subprocess
import tempfile
import pytest
import time
import shutil

REPO = "/workspace/hugo_repo"


def test_taxonomy_empty_key_filtering():
    """
    Fail-to-pass: Verify that empty-key taxonomy entries are filtered out.

    When [taxonomies] section contains entries with empty keys or values,
    they must be removed from the taxonomies map to prevent phantom taxonomies
    that cause .Ancestors to loop indefinitely.

    This test builds Hugo, creates a site with the problematic TOML config
    (disableKinds = [] after [taxonomies]), and verifies the page renders
    correctly with exactly 2 ancestors (section|home) without hanging.
    """
    # Build Hugo first
    build_result = subprocess.run(
        ["go", "build", "-o", "/tmp/hugo-test-bin"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert build_result.returncode == 0, f"Build failed:\n{build_result.stderr}"

    # Create a temporary test site
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create the problematic TOML config
        # In TOML, [taxonomies] followed by disableKinds = [] makes disableKinds
        # an entry in the taxonomies map with an empty key (since the value "[]"
        # gets parsed as empty string)
        hugo_toml = os.path.join(tmpdir, "hugo.toml")
        with open(hugo_toml, "w") as f:
            f.write("""baseURL = "http://example.com/"
title = "Bug repro"
[taxonomies]
  tag = "tags"
disableKinds = []
""")

        # Create content directory with a post that has taxonomy terms
        content_dir = os.path.join(tmpdir, "content", "posts")
        os.makedirs(content_dir)
        with open(os.path.join(content_dir, "hello.md"), "w") as f:
            f.write("""---
title: Hello
tags: [demo]
---
Hello.
""")

        # Create layouts directory with page template that outputs ancestors
        layouts_dir = os.path.join(tmpdir, "layouts")
        os.makedirs(layouts_dir)
        with open(os.path.join(layouts_dir, "page.html"), "w") as f:
            f.write("""Ancestors: {{ len .Ancestors }}|{{ range .Ancestors }}{{ .Kind }}|{{ end }}
""")

        # Run Hugo with a timeout (if bug exists, it hangs)
        try:
            result = subprocess.run(
                ["/tmp/hugo-test-bin", "--source", tmpdir],
                capture_output=True,
                text=True,
                timeout=30,
            )
        except subprocess.TimeoutExpired:
            pytest.fail("Hugo hung (bug exists): .Ancestors caused an infinite loop")

        # Check that Hugo didn't fail to build
        assert result.returncode == 0, f"Hugo failed:\n{result.stderr}"

        # Read the rendered page and verify correct ancestor count
        output_file = os.path.join(tmpdir, "public", "posts", "hello", "index.html")
        assert os.path.exists(output_file), f"Output file not found at {output_file}"

        with open(output_file, "r") as f:
            content = f.read()

        # The bug causes ancestors to be wrong or hang; fix should give exactly 2
        assert "Ancestors: 2|section|home|" in content, \
            f"Expected 'Ancestors: 2|section|home|' but got:\n{content[:500]}"


def test_hugo_builds():
    """Pass-to-pass: Hugo builds without error."""
    r = subprocess.run(
        ["go", "build", "-o", "/dev/null"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, f"Build failed:\n{r.stderr}"


def test_config_tests_pass():
    """Pass-to-pass: Config package tests pass."""
    r = subprocess.run(
        ["go", "test", "-v", "-timeout", "60s", "./config/allconfig/"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, f"Config tests failed:\n{r.stdout}\n{r.stderr}"


def test_go_vet_allconfig():
    """Pass-to-pass: go vet passes on config/allconfig package."""
    r = subprocess.run(
        ["go", "vet", "./config/allconfig/"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"go vet failed:\n{r.stderr}"


def test_go_vet_hugolib():
    """Pass-to-pass: go vet passes on hugolib package."""
    r = subprocess.run(
        ["go", "vet", "./hugolib/"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"go vet failed:\n{r.stderr}"


def test_taxonomies_tests():
    """Pass-to-pass: Taxonomy-related tests pass."""
    r = subprocess.run(
        ["go", "test", "-v", "-timeout", "60s", "./hugolib/", "-run", "TestTaxonomies"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"Taxonomy tests failed:\n{r.stderr}"


def test_disablekinds_tests():
    """Pass-to-pass: DisableKinds tests pass."""
    r = subprocess.run(
        ["go", "test", "-v", "-timeout", "60s", "./hugolib/", "-run", "TestDisableKinds"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"DisableKinds tests failed:\n{r.stderr}"