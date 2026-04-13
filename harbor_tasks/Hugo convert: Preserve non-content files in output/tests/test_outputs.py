#!/usr/bin/env python3
"""
Tests for hugo convert command preservation of non-content files.

These tests verify that the convert command properly preserves non-content
files (bundle resources) when copying content directories to output.

Fail-to-pass tests (behavioral):
- test_bundle_resource_preserved: Bundle resources (data.txt) must be copied to output
- test_nested_resource_preserved: Nested resources (nested/asset.dat) must be copied

Pass-to-pass tests (regression):
- test_convert_compiles: Code must compile after changes
- test_convert_command_help: Help output must be valid
- test_repo_go_vet: Go vet must pass (repo CI/CD)
- test_repo_build: Repo must build successfully (repo CI/CD)
- test_repo_gofmt: Go code is properly formatted (repo CI/CD)
- test_repo_go_mod_verify: Go modules verified (repo CI/CD)
- test_repo_command_convert: Repo's convert test passes (repo CI/CD)
"""

import subprocess
import tempfile
import os
import shutil
import sys

REPO = "/workspace/hugo"
HUGO_BIN = "/usr/local/bin/hugo"


def test_convert_compiles():
    """Verify Hugo compiles successfully with the fix applied."""
    result = subprocess.run(
        ["go", "build", "-o", "/tmp/hugo_test", "."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )
    assert result.returncode == 0, f"Failed to compile Hugo:\n{result.stderr}"


def test_convert_command_help():
    """Verify convert command help works."""
    result = subprocess.run(
        [HUGO_BIN, "convert", "--help"],
        capture_output=True,
        text=True,
        timeout=30
    )
    assert result.returncode == 0, f"convert --help failed:\n{result.stderr}"
    assert "Convert front matter to another format" in result.stdout


def test_repo_go_vet():
    """Repo's Go vet passes (pass_to_pass). Verifies go vet on commands package."""
    # Run go vet on commands package only (where the changes are)
    # Full repo vet runs out of disk space in Docker
    r = subprocess.run(
        ["go", "vet", "./commands/..."],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"go vet failed:\n{r.stderr[-500:]}"


def test_repo_build():
    """Repo builds successfully (pass_to_pass). Verifies go build works."""
    r = subprocess.run(
        ["go", "build", "."],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"go build failed:\n{r.stderr[-500:]}"


def test_repo_gofmt():
    """Repo code is properly formatted (pass_to_pass). Verifies gofmt passes."""
    r = subprocess.run(
        ["gofmt", "-l", "."],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    # gofmt -l outputs file names that need formatting; empty output means pass
    assert r.returncode == 0, f"gofmt check failed:\n{r.stderr[-500:]}"
    assert r.stdout.strip() == "", f"gofmt found formatting issues in files:\n{r.stdout}"


def test_repo_go_mod_verify():
    """Go modules are verified (pass_to_pass). Verifies go mod verify passes."""
    r = subprocess.run(
        ["go", "mod", "verify"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"go mod verify failed:\n{r.stderr[-500:]}"


def test_repo_command_convert():
    """Repo's convert command test passes (pass_to_pass). Tests the actual convert functionality."""
    r = subprocess.run(
        ["go", "test", "-v", "-run", "TestCommands/convert", "-count=1", ".", "-tags", "none"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"TestCommands/convert failed:\n{r.stderr[-1000:]}"


def test_bundle_resource_preserved():
    """
    Fail-to-pass: Non-content files in page bundles must be preserved in output.

    This tests the core fix from PR #14657 - when running hugo convert with -o,
    non-content files like bundle resources should be copied to the output dir.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test site structure with a page bundle
        content_dir = os.path.join(tmpdir, "content")
        bundle_dir = os.path.join(content_dir, "bundle")
        os.makedirs(bundle_dir)

        # Create bundle content file
        with open(os.path.join(bundle_dir, "index.md"), "w") as f:
            f.write("---\ntitle: Bundle\n---\nBundle content\n")

        # Create bundle resource file (non-content)
        with open(os.path.join(bundle_dir, "data.txt"), "w") as f:
            f.write("bundle resource data\n")

        # Create config
        with open(os.path.join(tmpdir, "hugo.toml"), "w") as f:
            f.write('baseURL = "http://example.org/"\n')

        output_dir = os.path.join(tmpdir, "output")

        # Run hugo convert toJSON with output
        result = subprocess.run(
            [HUGO_BIN, "convert", "toJSON", "-o", output_dir],
            cwd=tmpdir,
            capture_output=True,
            text=True,
            timeout=60
        )

        # Check command succeeded
        assert result.returncode == 0, f"convert command failed:\n{result.stderr}\nstdout:\n{result.stdout}"

        # Verify the content file was converted
        output_content_dir = os.path.join(output_dir, "content")
        output_bundle_dir = os.path.join(output_content_dir, "bundle")
        output_index = os.path.join(output_bundle_dir, "index.md")
        assert os.path.exists(output_index), f"Converted index.md not found in {output_bundle_dir}"

        # Verify the bundle resource was preserved (THIS IS THE BUG FIX)
        output_resource = os.path.join(output_bundle_dir, "data.txt")
        assert os.path.exists(output_resource), (
            f"Bundle resource data.txt was not preserved in output. "
            f"This is the bug from issue #4621 - non-content files in bundles "
            f"should be copied when using hugo convert with -o flag."
        )

        # Verify content is correct
        with open(output_resource, "r") as f:
            content = f.read()
        assert content == "bundle resource data\n", "Resource content was corrupted"


def test_nested_resource_preserved():
    """
    Fail-to-pass: Nested non-content files must be preserved.

    Tests that resources in subdirectories of bundles are also copied.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test site structure with nested resources
        content_dir = os.path.join(tmpdir, "content")
        bundle_dir = os.path.join(content_dir, "bundle")
        nested_dir = os.path.join(bundle_dir, "nested")
        os.makedirs(nested_dir)

        # Create bundle content
        with open(os.path.join(bundle_dir, "index.md"), "w") as f:
            f.write("---\ntitle: Bundle\n---\nBundle content\n")

        # Create nested resource file
        with open(os.path.join(nested_dir, "asset.dat"), "w") as f:
            f.write("nested resource data\n")

        # Create config
        with open(os.path.join(tmpdir, "hugo.toml"), "w") as f:
            f.write('baseURL = "http://example.org/"\n')

        output_dir = os.path.join(tmpdir, "output")

        # Run hugo convert
        result = subprocess.run(
            [HUGO_BIN, "convert", "toYAML", "-o", output_dir],
            cwd=tmpdir,
            capture_output=True,
            text=True,
            timeout=60
        )

        assert result.returncode == 0, f"convert command failed:\n{result.stderr}"

        # Verify nested resource was preserved
        output_nested = os.path.join(output_dir, "content", "bundle", "nested", "asset.dat")
        assert os.path.exists(output_nested), (
            f"Nested resource asset.dat was not preserved. "
            f"Resources in subdirectories of page bundles should be copied."
        )

        with open(output_nested, "r") as f:
            content = f.read()
        assert content == "nested resource data\n"


def test_multiple_content_files_converted():
    """
    Fail-to-pass: Multiple content files should be converted and resources preserved.

    Tests the scenario from the original issue with multiple content files
    in different formats, plus bundle resources.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        content_dir = os.path.join(tmpdir, "content")
        os.makedirs(content_dir)
        bundle_dir = os.path.join(content_dir, "bundle")
        os.makedirs(bundle_dir)

        # Create multiple content files in different formats
        # TOML front matter
        with open(os.path.join(content_dir, "mytoml.md"), "w") as f:
            f.write("+++\ntitle = \"TOML\"\n+++\nTOML content\n")

        # JSON front matter
        with open(os.path.join(content_dir, "myjson.md"), "w") as f:
            f.write('{\n  "title": "JSON"\n}\nJSON content\n')

        # YAML front matter
        with open(os.path.join(content_dir, "myyaml.md"), "w") as f:
            f.write("---\ntitle: YAML\n---\nYAML content\n")

        # Bundle with resource
        with open(os.path.join(bundle_dir, "index.md"), "w") as f:
            f.write("---\ntitle: Bundle\n---\nBundle content\n")
        with open(os.path.join(bundle_dir, "data.txt"), "w") as f:
            f.write("bundle resource\n")

        # Config
        with open(os.path.join(tmpdir, "hugo.toml"), "w") as f:
            f.write('baseURL = "http://example.org/"\n')

        output_dir = os.path.join(tmpdir, "myoutput")

        # Run convert
        result = subprocess.run(
            [HUGO_BIN, "convert", "toJSON", "-o", output_dir],
            cwd=tmpdir,
            capture_output=True,
            text=True,
            timeout=60
        )

        assert result.returncode == 0, f"convert failed:\n{result.stderr}"

        # All content files should be converted
        assert os.path.exists(os.path.join(output_dir, "content", "mytoml.md"))
        assert os.path.exists(os.path.join(output_dir, "content", "myjson.md"))
        assert os.path.exists(os.path.join(output_dir, "content", "myyaml.md"))
        assert os.path.exists(os.path.join(output_dir, "content", "bundle", "index.md"))

        # Bundle resource should exist
        assert os.path.exists(os.path.join(output_dir, "content", "bundle", "data.txt")), (
            "Bundle resource not preserved with multiple content files"
        )


def test_convert_output_format_variations():
    """
    Pass-to-pass: Verify convert works with all format options.

    Tests toJSON, toTOML, and toYAML all work correctly.
    """
    formats = ["toJSON", "toTOML", "toYAML"]

    for fmt in formats:
        with tempfile.TemporaryDirectory() as tmpdir:
            content_dir = os.path.join(tmpdir, "content")
            os.makedirs(content_dir)
            bundle_dir = os.path.join(content_dir, "bundle")
            os.makedirs(bundle_dir)

            # Create content
            with open(os.path.join(content_dir, "test.md"), "w") as f:
                f.write("---\ntitle: Test\n---\nTest content\n")
            with open(os.path.join(bundle_dir, "index.md"), "w") as f:
                f.write("---\ntitle: Bundle\n---\nBundle content\n")
            with open(os.path.join(bundle_dir, "resource.txt"), "w") as f:
                f.write("resource data\n")

            with open(os.path.join(tmpdir, "hugo.toml"), "w") as f:
                f.write('baseURL = "http://example.org/"\n')

            output_dir = os.path.join(tmpdir, "out")

            result = subprocess.run(
                [HUGO_BIN, "convert", fmt, "-o", output_dir],
                cwd=tmpdir,
                capture_output=True,
                text=True,
                timeout=60
            )

            assert result.returncode == 0, f"{fmt} failed:\n{result.stderr}"



if __name__ == "__main__":
    # Run with pytest if available
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
