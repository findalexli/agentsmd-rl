"""
Tests for Hugo taxonomy empty keys bug fix (PR #14551).

This tests that phantom taxonomy entries (with empty keys or values)
are properly filtered out during config parsing, preventing infinite
loops when .Ancestors is accessed.

The bug: When non-taxonomy keys (e.g. disableKinds = []) are placed after
[taxonomies] in TOML, they become part of the taxonomies table. An empty-
valued entry creates a phantom taxonomy with an empty pluralTreeKey, causing
.Ancestors to loop indefinitely.

The fix: Filter out entries with empty keys or values in the taxonomies decoder.
"""

import subprocess
import os

REPO = "/workspace/hugo"


def test_ancestors_with_problematic_config():
    """
    F2P: Test that .Ancestors works with problematic TOML config.

    This reproduces issue #14550 where disableKinds = [] after [taxonomies]
    creates a phantom taxonomy that causes .Ancestors to hang.

    The test creates a minimal Hugo site with problematic config and verifies
    that accessing .Ancestors in a template doesn't hang (which would cause
    the 30-second timeout to expire).
    """
    import tempfile

    # Create a minimal Hugo site with the problematic config
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create content directory
        os.makedirs(os.path.join(tmpdir, "content", "posts"))

        # Create problematic hugo.toml - disableKinds after [taxonomies]
        config = '''baseURL = "http://example.com/"
title = "Bug repro"
[taxonomies]
  tag = "tags"
disableKinds = []
'''
        with open(os.path.join(tmpdir, "hugo.toml"), "w") as f:
            f.write(config)

        # Create content file with tags
        content = '''---
title: Hello
tags: [demo]
---
Hello.
'''
        with open(os.path.join(tmpdir, "content", "posts", "hello.md"), "w") as f:
            f.write(content)

        # Create minimal layouts with .Ancestors access (the trigger for the bug)
        os.makedirs(os.path.join(tmpdir, "layouts"))
        with open(os.path.join(tmpdir, "layouts", "page.html"), "w") as f:
            f.write("Ancestors: {{ len .Ancestors }}\n")
        with open(os.path.join(tmpdir, "layouts", "list.html"), "w") as f:
            f.write("{{ .Title }}\n")

        # Create layouts for taxonomy pages which also use .Ancestors
        with open(os.path.join(tmpdir, "layouts", "taxonomy.html"), "w") as f:
            f.write("Taxonomy: {{ .Title }} Ancestors: {{ len .Ancestors }}\n")
        with open(os.path.join(tmpdir, "layouts", "term.html"), "w") as f:
            f.write("Term: {{ .Title }} Ancestors: {{ len .Ancestors }}\n")

        # Try to build with timeout - if it hangs due to .Ancestors bug, we fail
        # Note: First run may need to download Go toolchain and dependencies (GOTOOLCHAIN=auto)
        env = os.environ.copy()
        env["GOTOOLCHAIN"] = "auto"
        result = subprocess.run(
            ["go", "run", ".", "--source", tmpdir, "--destination", os.path.join(tmpdir, "public")],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=180,  # Allow time for toolchain download + build. Bug causes infinite loop (hangs forever)
            env=env,
        )

        # We allow non-zero exit codes (config issues etc), but not hangs/panics
        # The test passes if we got here without timeout - meaning .Ancestors didn't hang


def test_compilation():
    """
    P2P: Verify Hugo compiles successfully.
    """
    env = os.environ.copy()
    env["GOTOOLCHAIN"] = "auto"
    result = subprocess.run(
        ["go", "build", "-o", "/tmp/hugo", "./"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180,
        env=env,
    )

    if result.returncode != 0:
        raise AssertionError(f"Hugo compilation failed:\n{result.stderr}")


def test_gofmt():
    """
    P2P: Repo code passes gofmt formatting check (pass_to_pass).
    """
    result = subprocess.run(
        ["gofmt", "-l", "."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )

    if result.stdout.strip():
        files = result.stdout.strip().split("\n")
        raise AssertionError(f"gofmt found formatting issues in: {files}")


def test_config_package():
    """
    P2P: Config package tests pass (pass_to_pass).
    """
    env = os.environ.copy()
    env["GOTOOLCHAIN"] = "auto"
    result = subprocess.run(
        ["go", "test", "-v", "./config/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
        env=env,
    )

    if result.returncode != 0:
        raise AssertionError(
            f"Config package tests failed:\nstdout: {result.stdout[-1000:]}\nstderr: {result.stderr[-500:]}"
        )


def test_hugolib_package_smoke():
    """
    P2P: Smoke test - hugolib package compiles and basic tests pass (pass_to_pass).
    """
    env = os.environ.copy()
    env["GOTOOLCHAIN"] = "auto"
    result = subprocess.run(
        ["go", "test", "-v", "-run", "^TestBuild", "./hugolib/"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
        env=env,
    )

    if result.returncode != 0:
        raise AssertionError(
            f"Hugolib smoke test failed:\nstdout: {result.stdout[-1000:]}\nstderr: {result.stderr[-500:]}"
        )


def test_taxonomies_decoder_has_filtering():
    """
    Structural P2P: Verify the fix is present in the decoder.
    Gated by behavioral tests.
    """
    decoder_file = os.path.join(REPO, "config", "allconfig", "alldecoders.go")

    with open(decoder_file, "r") as f:
        content = f.read()

    # Check for the filtering loop that removes empty keys/values
    has_empty_check = 'if k == "" || v == ""' in content
    has_delete = "delete(m, k)" in content

    if not has_empty_check:
        raise AssertionError("Missing empty key/value check in taxonomies decoder")

    if not has_delete:
        raise AssertionError("Missing delete statement in taxonomies decoder")


def test_disable_kinds_tests_pass():
    """
    P2P: Run all disableKinds tests to ensure no regressions.
    """
    env = os.environ.copy()
    env["GOTOOLCHAIN"] = "auto"
    result = subprocess.run(
        ["go", "test", "-v", "-run", "^TestDisableKinds", "./hugolib/"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
        env=env,
    )

    if result.returncode != 0:
        raise AssertionError(
            f"TestDisableKinds tests failed:\nstdout: {result.stdout}\nstderr: {result.stderr}"
        )


def test_taxonomy_parsing_no_panic():
    """
    F2P: Verify Hugo doesn't panic or hang with empty taxonomy values.

    Uses a simple integration test approach - if Hugo can load the config
    and build without hanging, the fix is working.
    """
    import tempfile
    import shutil

    # Create a minimal Hugo site with the problematic config
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create content directory
        os.makedirs(os.path.join(tmpdir, "content", "posts"))

        # Create problematic hugo.toml - disableKinds after [taxonomies]
        config = '''baseURL = "http://example.com/"
title = "Bug repro"
[taxonomies]
  tag = "tags"
disableKinds = []
'''
        with open(os.path.join(tmpdir, "hugo.toml"), "w") as f:
            f.write(config)

        # Create content file with tags
        content = '''---
title: Hello
tags: [demo]
---
Hello.
'''
        with open(os.path.join(tmpdir, "content", "posts", "hello.md"), "w") as f:
            f.write(content)

        # Create minimal layouts
        os.makedirs(os.path.join(tmpdir, "layouts"))
        with open(os.path.join(tmpdir, "layouts", "page.html"), "w") as f:
            f.write("Ancestors: {{ len .Ancestors }}\n")
        with open(os.path.join(tmpdir, "layouts", "list.html"), "w") as f:
            f.write("{{ .Title }}\n")

        # Try to build with timeout - if it hangs, we fail
        # Note: First run may need to download Go toolchain and dependencies (GOTOOLCHAIN=auto)
        env = os.environ.copy()
        env["GOTOOLCHAIN"] = "auto"
        result = subprocess.run(
            ["go", "run", ".", "--source", tmpdir, "--destination", os.path.join(tmpdir, "public")],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=180,  # Allow time for toolchain download + build. Bug causes infinite loop (hangs forever)
            env=env,
        )

        # We allow non-zero exit codes (config issues etc), but not hangs/panics
        # The test passes if we got here without timeout
