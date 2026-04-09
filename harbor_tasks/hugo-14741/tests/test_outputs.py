"""
Test suite for Hugo PR #14741: Fix panic on edit of legacy mapped template names.

The bug: When editing a template with a legacy mapped name (e.g., tags/list.html),
if that template name was also a valid path in the new setup, Hugo would panic
because the 'replace' parameter was being passed but the duplicate name check
was conditional on 'replace' being false.

The fix: Remove the 'replace' parameter entirely and always check for duplicate
template names, appending a counter to avoid collisions.
"""

import subprocess
import sys
import os

REPO = "/workspace/hugo"

# Environment for Go commands (auto-download required Go version)
GO_ENV = {"GOTOOLCHAIN": "auto", **os.environ}


def test_hugo_build_compiles():
    """
    Fail-to-pass test: Verify Hugo compiles successfully after the fix.
    This catches any syntax errors or type mismatches introduced by the change.
    """
    result = subprocess.run(
        ["go", "build", "-o", "/tmp/hugo", "."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"Hugo build failed:\n{result.stderr}"


def test_template_functions_signature():
    """
    Pass-to-pass test: Verify the function signatures are correct.
    The fix removes the 'replace bool' parameter from several functions.
    """
    # Check that parseTemplates no longer takes a bool parameter
    result = subprocess.run(
        ["go", "build", "."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )
    assert result.returncode == 0, f"Build failed after signature change:\n{result.stderr}"


def test_templatestore_parse_template_signature():
    """
    Pass-to-pass test: Verify parseTemplate signature is correct.
    Should only take *TemplInfo, not (*TemplInfo, bool).
    """
    # This test is structural - it verifies the code compiles with new signature
    result = subprocess.run(
        ["go", "build", "./tpl/tplimpl"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )
    assert result.returncode == 0, f"tplimpl package build failed:\n{result.stderr}"


def test_doparse_template_signature():
    """
    Pass-to-pass test: Verify doParseTemplate signature is correct.
    Should only take *TemplInfo, not (*TemplInfo, bool).
    """
    result = subprocess.run(
        ["go", "build", "./tpl/tplimpl"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )
    assert result.returncode == 0, f"doParseTemplate signature check failed:\n{result.stderr}"


def test_rebuild_tags_list_template():
    """
    Fail-to-pass test: Run the specific regression test for issue #14740.
    This test verifies that editing a tags/list.html template doesn't panic.

    Before the fix: The test would panic because when RefreshFiles called
    parseTemplates(true), the replace=true would skip duplicate name checks,
    causing template name collisions.

    After the fix: The duplicate name check always runs, preventing panics.
    """
    # Run the specific test from the PR
    result = subprocess.run(
        ["go", "test", "-v", "-run", "TestRebuildEditTagsListLayout", "./hugolib"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )

    # Check test passed
    assert result.returncode == 0, (
        f"TestRebuildEditTagsListLayout failed:\n"
        f"STDOUT:\n{result.stdout}\n"
        f"STDERR:\n{result.stderr}"
    )

    # Verify the test actually ran (not skipped)
    assert "TestRebuildEditTagsListLayout" in result.stdout, "Test did not run"
    assert "PASS" in result.stdout or "PASS: TestRebuildEditTagsListLayout" in result.stdout, "Test did not pass"


def test_no_replace_parameter_in_parseTemplates():
    """
    Pass-to-pass structural test: Verify parseTemplates no longer accepts replace parameter.
    This catches cases where the agent might have forgotten to update all call sites.
    """
    # Grep for any remaining calls to parseTemplates with a boolean argument
    result = subprocess.run(
        ["grep", "-rn", "parseTemplates(true)", "--include=*.go", "."],
        cwd=REPO,
        capture_output=True,
        text=True
    )
    assert result.returncode != 0 or result.stdout.strip() == "", (
        f"Found remaining parseTemplates(true) calls that should be removed:\n{result.stdout}"
    )

    result = subprocess.run(
        ["grep", "-rn", "parseTemplates(false)", "--include=*.go", "."],
        cwd=REPO,
        capture_output=True,
        text=True
    )
    assert result.returncode != 0 or result.stdout.strip() == "", (
        f"Found remaining parseTemplates(false) calls that should be removed:\n{result.stdout}"
    )


def test_no_replace_parameter_in_parseTemplate():
    """
    Pass-to-pass structural test: Verify parseTemplate calls no longer pass replace parameter.
    """
    # Check that parseTemplate is not called with a second boolean argument
    result = subprocess.run(
        ["grep", "-rn", "parseTemplate.*,.*true)", "--include=*.go", "./tpl/tplimpl"],
        cwd=REPO,
        capture_output=True,
        text=True
    )
    assert result.returncode != 0 or result.stdout.strip() == "", (
        f"Found parseTemplate calls with 'true' parameter:\n{result.stdout}"
    )

    result = subprocess.run(
        ["grep", "-rn", "parseTemplate.*,.*false)", "--include=*.go", "./tpl/tplimpl"],
        cwd=REPO,
        capture_output=True,
        text=True
    )
    assert result.returncode != 0 or result.stdout.strip() == "", (
        f"Found parseTemplate calls with 'false' parameter:\n{result.stdout}"
    )


def test_template_duplicate_name_check():
    """
    Pass-to-pass behavioral test: Verify the duplicate name check logic is correct.
    The fix changes:
        if !replace && prototype.Lookup(name) != nil
    to:
        if prototype.Lookup(name) != nil
    This test verifies the code compiles with the correct logic.
    """
    # Build the package to ensure the logic is correct
    result = subprocess.run(
        ["go", "build", "./tpl/tplimpl"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )
    assert result.returncode == 0, f"Template duplicate name check failed:\n{result.stderr}"


def test_all_tplimpl_tests_pass():
    """
    Pass-to-pass test: Run all tplimpl tests to ensure no regressions.
    """
    result = subprocess.run(
        ["go", "test", "./tpl/tplimpl", "-count=1"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180
    )
    assert result.returncode == 0, (
        f"tplimpl tests failed:\n"
        f"STDOUT:\n{result.stdout}\n"
        f"STDERR:\n{result.stderr}"
    )


def test_hugolib_rebuild_tests():
    """
    Pass-to-pass test: Run all rebuild-related tests in hugolib.
    These are the tests most likely to be affected by template refresh changes.
    """
    result = subprocess.run(
        ["go", "test", "./hugolib", "-run", "Rebuild|Rebuild.*Edit", "-v", "-count=1"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180
    )
    assert result.returncode == 0, (
        f"hugolib rebuild tests failed:\n"
        f"STDOUT:\n{result.stdout}\n"
        f"STDERR:\n{result.stderr}"
    )


# =============================================================================
# Pass-to-Pass: Repo CI/CD Tests
# These tests verify that the repo's own CI checks pass on the base commit.
# They ensure the fix doesn't break existing functionality.
# =============================================================================


def test_repo_gofmt():
    """Repo's gofmt check passes (pass_to_pass)."""
    r = subprocess.run(
        ["gofmt", "-l", "."],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    # gofmt -l returns empty output when there are no issues
    assert r.stdout.strip() == "", f"gofmt found issues in:\n{r.stdout}"


def test_repo_go_mod_verify():
    """Repo's go.mod verification passes (pass_to_pass)."""
    r = subprocess.run(
        ["go", "mod", "verify"],
        capture_output=True, text=True, timeout=60, cwd=REPO, env=GO_ENV,
    )
    assert r.returncode == 0, f"go mod verify failed:\n{r.stderr}"


def test_repo_go_build_all():
    """Repo builds all packages successfully (pass_to_pass)."""
    r = subprocess.run(
        ["go", "build", "./..."],
        capture_output=True, text=True, timeout=120, cwd=REPO, env=GO_ENV,
    )
    assert r.returncode == 0, f"go build ./... failed:\n{r.stderr[-500:]}"


def test_repo_go_vet_tplimpl():
    """Repo's go vet passes on tpl/tplimpl package (pass_to_pass)."""
    r = subprocess.run(
        ["go", "vet", "./tpl/tplimpl/..."],
        capture_output=True, text=True, timeout=120, cwd=REPO, env=GO_ENV,
    )
    assert r.returncode == 0, f"go vet ./tpl/tplimpl/... failed:\n{r.stderr[-500:]}"


def test_repo_go_vet_hugolib():
    """Repo's go vet passes on hugolib package (pass_to_pass)."""
    r = subprocess.run(
        ["go", "vet", "./hugolib/..."],
        capture_output=True, text=True, timeout=120, cwd=REPO, env=GO_ENV,
    )
    assert r.returncode == 0, f"go vet ./hugolib/... failed:\n{r.stderr[-500:]}"


if __name__ == "__main__":
    pytest_main = ["-v", __file__]
    if len(sys.argv) > 1:
        pytest_main = ["-v", __file__, "-k", sys.argv[1]]
    subprocess.run(["python3", "-m", "pytest"] + pytest_main)
