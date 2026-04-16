"""Test outputs for Hugo Goldmark link ampersand escaping fix."""

import subprocess
import sys
import os
import tempfile

REPO = "/workspace/hugo"
TEST_TIMEOUT = 120


def test_link_ampersand_escaping():
    """Test that ampersands in link URLs are correctly escaped (not double-escaped).

    This is a fail_to_pass test: on the buggy base commit, ampersands are
    double-escaped to &amp;amp; instead of &amp;. After the fix, they should
    be correctly escaped to &amp;.
    """
    # First check if the upstream test exists in the codebase
    test_file_path = os.path.join(REPO, "markup/goldmark/goldmark_integration_test.go")
    with open(test_file_path, "r") as f:
        content = f.read()

    # If the test doesn't exist, we need to add it temporarily to test
    if "TestRenderLinkDefaultAmpersand" not in content:
        # Add the test temporarily
        test_code = '''

// Issue 14715
func TestRenderLinkDefaultAmpersand(t *testing.T) {
	t.Parallel()

	files := `
-- content/_index.md --
---
title: "Home"
---
[foo](https://a.com/?a=1&b=2)
-- layouts/home.html --
{{ .Content }}
`

	b := hugolib.Test(t, files)

	b.AssertFileContent("public/index.html",
		`<a href="https://a.com/?a=1&amp;b=2">foo</a>`,
	)
}
'''
        # Append the test to the file
        with open(test_file_path, "a") as f:
            f.write(test_code)

    # Now run the specific integration test for this issue
    result = subprocess.run(
        ["go", "test", "-v", "-run", "TestRenderLinkDefaultAmpersand", "./markup/goldmark/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=TEST_TIMEOUT,
    )

    if result.returncode != 0:
        print(f"Test stdout:\n{result.stdout}")
        print(f"Test stderr:\n{result.stderr}")

    assert result.returncode == 0, f"Test failed - ampersand escaping issue present (double-escaped to &amp;amp; instead of &amp;):\n{result.stderr}"


def test_goldmark_render_hooks_compile():
    """Test that goldmark render_hooks.go compiles successfully.

    This is a basic sanity check that the code is syntactically correct.
    """
    result = subprocess.run(
        ["go", "build", "./markup/goldmark/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=TEST_TIMEOUT,
    )

    if result.returncode != 0:
        print(f"Build stdout:\n{result.stdout}")
        print(f"Build stderr:\n{result.stderr}")

    assert result.returncode == 0, f"Build failed:\n{result.stderr}"


def test_goldmark_package_subtests():
    """Run goldmark subpackage tests to ensure no regressions.

    This is a pass_to_pass test - the tests should pass both before and after.
    Excludes the main goldmark package which may be modified by fail_to_pass tests.
    """
    subpackages = [
        "./markup/goldmark/blockquotes/...",
        "./markup/goldmark/codeblocks/...",
        "./markup/goldmark/hugocontext/...",
        "./markup/goldmark/images/...",
        "./markup/goldmark/internal/...",
        "./markup/goldmark/passthrough/...",
        "./markup/goldmark/tables/...",
    ]

    for pkg in subpackages:
        result = subprocess.run(
            ["go", "test", "-v", "-count=1", pkg],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode != 0:
            print(f"Test stdout:\n{result.stdout[-1500:]}")
            print(f"Test stderr:\n{result.stderr[-500:]}")
        assert result.returncode == 0, f"Package tests failed for {pkg}:\n{result.stderr[-500:]}"


# =============================================================================
# Pass-to-Pass Tests (repo CI commands) - These should pass both before and after
# =============================================================================

def test_repo_go_mod_verify():
    """Go modules are verified (pass_to_pass)."""
    result = subprocess.run(
        ["go", "mod", "verify"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=TEST_TIMEOUT,
    )
    assert result.returncode == 0, f"Go mod verify failed:\n{result.stderr}"


def test_repo_go_vet_goldmark():
    """Go vet passes on goldmark package (pass_to_pass)."""
    result = subprocess.run(
        ["go", "vet", "./markup/goldmark/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=TEST_TIMEOUT,
    )
    assert result.returncode == 0, f"Go vet failed:\n{result.stderr}"


def test_repo_gofmt_check():
    """Go code is properly formatted (pass_to_pass).

    Note: This checks all directories except markup/goldmark which may be
    modified by the fail_to_pass test that adds a temporary test case.
    """
    # Check specific directories that don't get modified
    dirs_to_check = [
        "bufferpool", "cache", "codegen", "commands", "common", "compare",
        "config", "create", "deploy", "deps", "docshelper", "helpers",
        "htesting", "hugofs", "hugolib", "identity", "internal", "langs",
        "livereload", "main.go", "markup/asciidocext", "markup/converter",
        "markup/goldmark/blockquotes", "markup/goldmark/codeblocks",
        "markup/goldmark/hugocontext", "markup/goldmark/images",
        "markup/goldmark/internal", "markup/goldmark/passthrough",
        "markup/goldmark/tables", "markup/highlight", "markup/markdownlex",
        "markup/mdconv", "markup/org", "markup/pandoc", "markup/rst",
        "markup/tableofcontents", "media", "metrics", "minifiers",
        "modules", "navigation", "output", "parser", "publisher",
        "related", "releaser", "resources", "scripts", "source",
        "testscripts", "tpl", "transform", "watcher"
    ]

    for dir_path in dirs_to_check:
        full_path = os.path.join(REPO, dir_path)
        if os.path.exists(full_path):
            result = subprocess.run(
                ["gofmt", "-l", dir_path],
                cwd=REPO,
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.stdout.strip():
                assert False, f"gofmt found unformatted files in {dir_path}:\n{result.stdout}"


def test_repo_convert_tests():
    """Goldmark convert tests pass (pass_to_pass)."""
    result = subprocess.run(
        ["go", "test", "-run", "TestConvert", "-count=1", "-v", "./markup/goldmark/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    if result.returncode != 0:
        print(f"Test stdout:\n{result.stdout[-1500:]}")
        print(f"Test stderr:\n{result.stderr[-500:]}")
    assert result.returncode == 0, f"Convert tests failed:\n{result.stderr[-500:]}"


def test_repo_link_tests():
    """Goldmark link-related tests pass (pass_to_pass)."""
    result = subprocess.run(
        ["go", "test", "-run", "TestLink", "-count=1", "-v", "./markup/goldmark/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    if result.returncode != 0:
        print(f"Test stdout:\n{result.stdout[-1500:]}")
        print(f"Test stderr:\n{result.stderr[-500:]}")
    assert result.returncode == 0, f"Link tests failed:\n{result.stderr[-500:]}"


def test_repo_render_hooks_tests():
    """Hugolib content render hooks tests pass (pass_to_pass)."""
    result = subprocess.run(
        ["go", "test", "-run", "TestContentRenderHooks", "-count=1", "-v", "./hugolib/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    if result.returncode != 0:
        print(f"Test stdout:\n{result.stdout[-1500:]}")
        print(f"Test stderr:\n{result.stderr[-500:]}")
    assert result.returncode == 0, f"Render hooks tests failed:\n{result.stderr[-500:]}"
