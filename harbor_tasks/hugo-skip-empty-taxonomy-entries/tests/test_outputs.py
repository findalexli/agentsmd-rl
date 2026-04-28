"""Tests for hugo PR #14551: skip taxonomy entries with empty keys/values.

The bug: when `disableKinds = []` is placed in TOML AFTER a `[taxonomies]`
section, TOML parses it inside the taxonomies table.  An empty-keyed
taxonomy with empty pluralTreeKey makes `.Ancestors` loop indefinitely.

These tests run inside the Docker image, where the repository lives at
/workspace/hugo and Go modules have already been downloaded.
"""

import os
import shutil
import subprocess
from pathlib import Path

REPO = Path("/workspace/hugo")

# A self-contained Go test that drives the bug by building a real Hugo site.
# We give the test a unique name so it never collides with the upstream test
# the gold patch may add.
SCAFFOLD_TEST_FILENAME = "scaffold_taxonomy_bug_test.go"
SCAFFOLD_TEST_PATH = REPO / "hugolib" / SCAFFOLD_TEST_FILENAME
SCAFFOLD_TEST_GO = '''package hugolib

import (
	"testing"
)

// Reproducer for the empty-taxonomy-entry bug.  When disableKinds = []
// is placed after [taxonomies] in TOML, it's parsed as part of the
// taxonomies table.  An empty-valued entry creates a phantom taxonomy
// whose pluralTreeKey is empty, causing .Ancestors to loop forever.
func TestScaffoldEmptyTaxonomyAncestors(t *testing.T) {
	files := `
-- hugo.toml --
baseURL = "http://example.com/"
title = "Bug repro"
[taxonomies]
  tag = "tags"
disableKinds = []
-- content/posts/hello.md --
---
title: Hello
tags: [demo]
---
Hello.
-- layouts/page.html --
Ancestors: {{ len .Ancestors }}|{{ range .Ancestors }}{{ .Kind }}|{{ end }}
-- layouts/list.html --
{{ .Title }}
`
	b := Test(t, files)
	b.AssertFileContent("public/posts/hello/index.html", "Ancestors: 2|section|home|")
}
'''


def _write_scaffold_test():
    SCAFFOLD_TEST_PATH.write_text(SCAFFOLD_TEST_GO)


def _remove_scaffold_test():
    if SCAFFOLD_TEST_PATH.exists():
        SCAFFOLD_TEST_PATH.unlink()


def setup_module(module):
    _write_scaffold_test()


def teardown_module(module):
    _remove_scaffold_test()


# --------------------------------------------------------------------------
# fail-to-pass: the actual bug fix
# --------------------------------------------------------------------------

def test_empty_taxonomy_entry_does_not_break_ancestors():
    """When disableKinds=[] follows [taxonomies] in TOML, .Ancestors must
    return the regular section/home chain instead of looping forever or
    producing a phantom ancestor."""
    r = subprocess.run(
        ["go", "test",
         "-run", "^TestScaffoldEmptyTaxonomyAncestors$",
         "-count=1",
         "-timeout", "60s",
         "./hugolib/"],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, (
        "Bug-repro Go test failed.\n"
        f"STDOUT (tail):\n{r.stdout[-3000:]}\n"
        f"STDERR (tail):\n{r.stderr[-2000:]}"
    )


# --------------------------------------------------------------------------
# pass-to-pass: repo invariants that must keep holding after the fix
# --------------------------------------------------------------------------

def test_alldecoders_is_gofmt_clean():
    """The agent's edit to config/allconfig/alldecoders.go must remain
    gofmt-clean (per AGENTS.md `./check.sh`)."""
    r = subprocess.run(
        ["gofmt", "-l", "config/allconfig/alldecoders.go"],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"gofmt errored: {r.stderr}"
    assert r.stdout.strip() == "", (
        f"gofmt found formatting issues:\n{r.stdout}"
    )


def test_config_allconfig_vet_clean():
    """`go vet ./config/allconfig/...` must pass."""
    r = subprocess.run(
        ["go", "vet", "./config/allconfig/..."],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, (
        f"go vet failed.\nSTDOUT:\n{r.stdout[-2000:]}\nSTDERR:\n{r.stderr[-2000:]}"
    )


def test_config_allconfig_compiles_and_tests_pass():
    """The repo's existing config/allconfig tests must keep passing."""
    r = subprocess.run(
        ["go", "test", "-count=1", "-timeout", "180s", "./config/allconfig/..."],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=240,
    )
    assert r.returncode == 0, (
        f"./config/allconfig tests failed.\n"
        f"STDOUT:\n{r.stdout[-3000:]}\nSTDERR:\n{r.stderr[-1500:]}"
    )

# === PR-added f2p tests (taskforge.test_patch_miner) ===
def test_pr_added_TestDisableKindsEmptySliceAncestors():
    """fail_to_pass | PR added test 'TestDisableKindsEmptySliceAncestors' in 'hugolib/disableKinds_test.go' (go_test)"""
    r = subprocess.run(
        ["go", "test",
         "-run", "^TestDisableKindsEmptySliceAncestors$",
         "-count=1",
         "-v",
         "-timeout", "120s",
         "./hugolib/"],
        cwd=str(REPO),
        capture_output=True, text=True, timeout=300,
    )
    assert r.returncode == 0, (
        f"PR-added test 'TestDisableKindsEmptySliceAncestors' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")
    assert "no tests to run" not in r.stdout, (
        "PR-added test TestDisableKindsEmptySliceAncestors was not found in the package.\n"
        f"stdout: {r.stdout[-1500:]}")
    assert "--- PASS:" in r.stdout, (
        f"PR-added test did not pass.\nstdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_test_check():
    """pass_to_pass | CI job 'test' → step 'Check'"""
    r = subprocess.run(
        ["bash", "-lc", 'mage -v check'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Check' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_test():
    """pass_to_pass | CI job 'test' → step 'Test'"""
    r = subprocess.run(
        ["bash", "-lc", 'mage -v test'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Test' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_build_for_dragonfly():
    """pass_to_pass | CI job 'test' → step 'Build for dragonfly'"""
    r = subprocess.run(
        ["bash", "-lc", 'go install\ngo clean -i -cache'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build for dragonfly' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")