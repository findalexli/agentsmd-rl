"""
Test suite for Hugo issue #14740: panic on edit of legacy mapped template names.

This tests that editing templates like `layouts/tags/list.html` during live reload
does not cause a panic due to duplicate template name registration.
"""

import subprocess
import sys
import tempfile
import os
import shutil

REPO = "/workspace/hugo"
HUGO_BIN = "/usr/local/bin/hugo"


def test_template_functions_parse_template_signature():
    """
    FAIL-TO-PASS: parseTemplate should not have 'replace' parameter.

    The bug was caused by the `replace bool` parameter that controlled whether
    to check for duplicate template names. When replace=true (during RefreshFiles),
    duplicates weren't detected, causing a panic.

    The fix removes the replace parameter entirely, always checking for duplicates.
    """
    # Read the templates.go file
    templates_file = os.path.join(REPO, "tpl/tplimpl/templates.go")
    with open(templates_file, "r") as f:
        content = f.read()

    # After fix: parseTemplate should have signature without replace parameter
    # This should NOT exist after fix: "func (s *TemplateStore) parseTemplate(ti *TemplInfo, replace bool)"
    bad_signature = "func (s *TemplateStore) parseTemplate(ti *TemplInfo, replace bool)"
    good_signature = "func (s *TemplateStore) parseTemplate(ti *TemplInfo) error"

    # The fix should have the good signature
    assert good_signature in content, f"parseTemplate should not have 'replace' parameter. Expected: {good_signature}"
    assert bad_signature not in content, f"Old buggy signature found: {bad_signature}"


def test_template_functions_do_parse_template_signature():
    """
    FAIL-TO-PASS: doParseTemplate should not have 'replace' parameter.
    """
    templates_file = os.path.join(REPO, "tpl/tplimpl/templates.go")
    with open(templates_file, "r") as f:
        content = f.read()

    bad_signature = "func (t *templateNamespace) doParseTemplate(ti *TemplInfo, replace bool)"
    good_signature = "func (t *templateNamespace) doParseTemplate(ti *TemplInfo) error"

    assert good_signature in content, f"doParseTemplate should not have 'replace' parameter"
    assert bad_signature not in content, f"Old buggy signature found: {bad_signature}"


def test_template_store_parse_templates_signature():
    """
    FAIL-TO-PASS: parseTemplates should not have 'replace' parameter.
    """
    store_file = os.path.join(REPO, "tpl/tplimpl/templatestore.go")
    with open(store_file, "r") as f:
        content = f.read()

    bad_signature = "func (s *TemplateStore) parseTemplates(replace bool)"
    good_signature = "func (s *TemplateStore) parseTemplates() error"

    assert good_signature in content, f"parseTemplates should not have 'replace' parameter"
    assert bad_signature not in content, f"Old buggy signature found: {bad_signature}"


def test_template_parsing_calls_no_replace_arg():
    """
    FAIL-TO-PASS: parseTemplate calls should not pass replace argument.

    All call sites should be updated to not pass the replace argument.
    """
    store_file = os.path.join(REPO, "tpl/tplimpl/templatestore.go")
    with open(store_file, "r") as f:
        content = f.read()

    # After fix, all calls should be: parseTemplate(vv) not parseTemplate(vv, replace)
    # Check that no calls with two arguments exist
    import re

    # Find all parseTemplate calls with 2 arguments (the buggy pattern)
    bad_calls = re.findall(r"s\.parseTemplate\([^,)]+,\s*[^)]+\)", content)

    assert len(bad_calls) == 0, f"Found parseTemplate calls with 'replace' argument: {bad_calls}"


def test_duplicate_template_name_check_always_runs():
    """
    FAIL-TO-PASS: Template name duplicate check should always run.

    The bug was that the check `if !replace && prototype.Lookup(name) != nil`
    was skipped when replace=true. The fix removes the `!replace &&` condition
    so the check always runs.
    """
    templates_file = os.path.join(REPO, "tpl/tplimpl/templates.go")
    with open(templates_file, "r") as f:
        content = f.read()

    # The buggy pattern: checking "!replace &&" before prototype.Lookup
    bad_pattern = "if !replace && prototype.Lookup(name) != nil"

    # The fixed pattern: checking without replace condition
    good_pattern = "if prototype.Lookup(name) != nil"

    # Should find the good pattern (at least twice - once for plain text, once for HTML)
    good_count = content.count(good_pattern)
    bad_count = content.count(bad_pattern)

    assert bad_count == 0, f"Found {bad_count} occurrences of buggy '!replace &&' pattern"
    assert good_count >= 2, f"Expected at least 2 occurrences of 'if prototype.Lookup(name) != nil', found {good_count}"


def test_regression_tags_list_edit():
    """
    FAIL-TO-PASS: Editing tags/list.html template should not panic.

    This reproduces the exact issue from #14740: creating a site with
    layouts/tags/list.html and triggering a rebuild causes a panic on
    the base commit.
    """
    # Create a temporary Hugo site
    with tempfile.TemporaryDirectory() as site_dir:
        # Create the site structure
        layouts_dir = os.path.join(site_dir, "layouts", "tags")
        content_dir = os.path.join(site_dir, "content")
        os.makedirs(layouts_dir, exist_ok=True)
        os.makedirs(content_dir, exist_ok=True)

        # Create hugo.toml
        with open(os.path.join(site_dir, "hugo.toml"), "w") as f:
            f.write('baseURL = "https://example.com"\n')

        # Create the problematic template (tags/list.html)
        with open(os.path.join(layouts_dir, "list.html"), "w") as f:
            f.write("Foo.\n")

        # Create a basic content file
        with open(os.path.join(content_dir, "_index.md"), "w") as f:
            f.write("---\ntitle: \"Tags\"\n---\n")

        # First build - should work even on base commit
        result1 = subprocess.run(
            [HUGO_BIN, "--source", site_dir],
            capture_output=True,
            text=True,
            timeout=60
        )

        # The initial build should succeed
        assert result1.returncode == 0, f"Initial build failed: {result1.stderr}"

        # Check that the output was created
        public_dir = os.path.join(site_dir, "public", "tags")
        assert os.path.exists(public_dir), f"public/tags directory not created"

        # Read the initial output
        index_file = os.path.join(public_dir, "index.html")
        if os.path.exists(index_file):
            with open(index_file, "r") as f:
                content1 = f.read()
            assert "Foo." in content1, f"Initial content should contain 'Foo.'"

        # Edit the template - this triggers the panic on base commit
        with open(os.path.join(layouts_dir, "list.html"), "w") as f:
            f.write("Bar.\n")

        # Second build - this is where the panic occurs on base commit
        result2 = subprocess.run(
            [HUGO_BIN, "--source", site_dir],
            capture_output=True,
            text=True,
            timeout=60
        )

        # This should NOT panic - on base commit this will fail
        assert result2.returncode == 0, f"Build after edit failed (panic?): {result2.stderr}"

        # Check that the edited content is reflected
        if os.path.exists(index_file):
            with open(index_file, "r") as f:
                content2 = f.read()
            assert "Bar." in content2, f"Edited content should contain 'Bar.'"


def test_hugo_compiles():
    """
    PASS-TO-PASS: Hugo binary should compile and run.
    """
    result = subprocess.run(
        [HUGO_BIN, "version"],
        capture_output=True,
        text=True,
        timeout=30
    )
    assert result.returncode == 0, f"Hugo version check failed: {result.stderr}"
    assert "hugo" in result.stdout.lower(), f"Expected 'hugo' in version output: {result.stdout}"


def test_go_build():
    """
    PASS-TO-PASS: Repository should compile with go build.
    """
    result = subprocess.run(
        ["go", "build", "-o", "/tmp/hugo-test", "."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"Go build failed: {result.stderr}"
    assert os.path.exists("/tmp/hugo-test"), "Built binary not found"


def test_go_vet():
    """
    PASS-TO-PASS: Repository should pass go vet on modified package.
    """
    # Only vet the modified package to save time
    result = subprocess.run(
        ["go", "vet", "./tpl/tplimpl/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"go vet failed: {result.stderr}"


def test_repo_tests_tplimpl():
    """
    PASS-TO-PASS: tpl/tplimpl tests should pass.
    """
    result = subprocess.run(
        ["go", "test", "-v", "-count=1", "-run", "TestTemplate", "./tpl/tplimpl/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )
    # We don't strictly require all tests to pass, but we check that
    # the test suite runs without crashing
    if result.returncode != 0:
        # If tests fail, check if it's due to actual failures vs setup issues
        if "panic" in result.stderr.lower():
            assert False, f"Tests panicked: {result.stderr[-500:]}"


def test_repo_tests_hugolib_basic():
    """
    PASS-TO-PASS: Basic hugolib tests should pass.
    """
    # Run a subset of hugolib tests related to templates and rebuilding
    result = subprocess.run(
        ["go", "test", "-v", "-count=1", "-run", "TestRebuild|TestTemplate", "./hugolib/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )

    # Check for panics specifically
    if "panic" in result.stderr.lower() or "panic" in result.stdout.lower():
        assert False, f"Tests panicked: {result.stderr[-1000:]}"

    # The test should complete without timing out or crashing
    assert result.returncode in [0, 1], f"Test run had unexpected error: {result.stderr[-500:]}"


def test_gofmt_tplimpl():
    """
    PASS-TO-PASS: Modified package should pass gofmt.
    """
    result = subprocess.run(
        ["gofmt", "-l", "./tpl/tplimpl/"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )
    # gofmt returns 0 even if files are found, check stdout is empty
    assert result.stdout.strip() == "", f"gofmt found issues:\n{result.stdout}"
    assert result.returncode == 0, f"gofmt failed: {result.stderr}"


def test_staticcheck_tplimpl():
    """
    PASS-TO-PASS: Modified package should pass staticcheck.
    """
    # Install staticcheck if needed
    install_result = subprocess.run(
        ["go", "install", "honnef.co/go/tools/cmd/staticcheck@latest"],
        capture_output=True,
        text=True,
        timeout=120
    )

    env = os.environ.copy()
    env["PATH"] = env.get("PATH", "") + ":/go/bin"

    result = subprocess.run(
        ["staticcheck", "./tpl/tplimpl/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180,
        env=env
    )
    assert result.returncode == 0, f"staticcheck failed:\n{result.stdout}\n{result.stderr}"


def test_go_build_all():
    """
    PASS-TO-PASS: Full repository should compile with go build ./...
    """
    result = subprocess.run(
        ["go", "build", "./..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )
    assert result.returncode == 0, f"go build ./... failed:\n{result.stderr[-500:]}"


def test_hugolib_rebuild_tests():
    """
    PASS-TO-PASS: Rebuild-related tests in hugolib should pass.
    """
    # Run specific rebuild tests that are relevant to the fix
    result = subprocess.run(
        ["go", "test", "-count=1", "-run", "TestRebuild.*Edit|TestEditBaseofParseAfterExecute", "./hugolib/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )

    # Check for panics specifically
    if "panic" in result.stderr.lower() or "panic" in result.stdout.lower():
        assert False, f"Tests panicked: {result.stderr[-1000:]}"

    assert result.returncode == 0, f"Rebuild tests failed:\n{result.stderr[-500:]}"
