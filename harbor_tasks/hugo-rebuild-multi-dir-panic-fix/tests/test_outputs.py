"""Verifier tests for hugo PR #14575 (issue 14573 panic fix)."""
from __future__ import annotations

import os
import subprocess
from pathlib import Path

REPO = Path("/workspace/hugo")
HUGOLIB = REPO / "hugolib"
SITE_GO = HUGOLIB / "site.go"


# Helper added by PR #14575 to integrationtest_builder.go. We inject this as
# its own file inside the hugolib package at test time so the regression
# tests below can compile.
ADDON_BUILDER_GO = r"""package hugolib

import (
	"path/filepath"

	qt "github.com/frankban/quicktest"
)

// CreateDirs creates empty directories under the test workspace so a rebuild
// observes them as directory pathChange events. Used by the issue-14573
// regression tests injected by the verifier.
func (s *IntegrationTestBuilder) CreateDirs(dirnames ...string) *IntegrationTestBuilder {
	for _, dirname := range dirnames {
		absDir := s.absFilename(filepath.FromSlash(dirname))
		s.Assert(s.fs.Source.MkdirAll(absDir, 0o777), qt.IsNil)
		s.createdFiles = append(s.createdFiles, absDir)
	}
	return s
}
"""

ADDON_TEST_GO = r"""package hugolib

import "testing"

// Issue 14573: panic when a rebuild's pathChanges include multiple new
// directories together with file changes nested under another directory.
func TestRebuildAddContentWithMultipleDirCreations_Issue14573(t *testing.T) {
	t.Parallel()
	files := `
-- hugo.toml --
baseURL = "https://example.com"
disableLiveReload = true
-- content/p1.md --
---
title: "P1"
---
-- layouts/page.html --
Single: {{ .Title }}|{{ .Content }}|
-- layouts/list.html --
Pages: {{ range .RegularPages }}{{ .RelPermalink }}|{{ end }}$`
	b := TestRunning(t, files)
	b.AssertFileContent("public/index.html", "Pages: /p1/|$")
	b.AddFiles(
		"content/nesteddir/dir1/post.md", "---\ntitle: Post\n---",
	).CreateDirs(
		"content/dir1",
		"content/dir2",
	).Build()
	b.AssertFileContent("public/nesteddir/dir1/post/index.html", "Single: Post|")
}

// Issue 14573 variant: more new directories so n grows even further beyond
// len(others) under the buggy logic — guards against any "off-by-one only"
// pseudo-fix.
func TestRebuildAddContentWithMultipleDirCreations_Issue14573_Wider(t *testing.T) {
	t.Parallel()
	files := `
-- hugo.toml --
baseURL = "https://example.com"
disableLiveReload = true
-- content/p1.md --
---
title: "P1"
---
-- layouts/page.html --
Single: {{ .Title }}|{{ .Content }}|
-- layouts/list.html --
Pages: {{ range .RegularPages }}{{ .RelPermalink }}|{{ end }}$`
	b := TestRunning(t, files)
	b.AssertFileContent("public/index.html", "Pages: /p1/|$")
	b.AddFiles(
		"content/nesteddir/dir1/post.md", "---\ntitle: Post\n---",
	).CreateDirs(
		"content/dirA",
		"content/dirB",
		"content/dirC",
		"content/dirD",
	).Build()
	b.AssertFileContent("public/nesteddir/dir1/post/index.html", "Single: Post|")
}
"""


def _stage_test_addons() -> None:
    """Drop the regression-test helper + tests into hugolib/ once per run."""
    builder_dst = HUGOLIB / "z_issue14573_addon_builder.go"
    test_dst = HUGOLIB / "z_issue14573_addon_test.go"
    if not builder_dst.exists():
        builder_dst.write_text(ADDON_BUILDER_GO)
    if not test_dst.exists():
        test_dst.write_text(ADDON_TEST_GO)


def _go_env() -> dict[str, str]:
    env = os.environ.copy()
    env.setdefault("GOFLAGS", "-mod=mod")
    env.setdefault("CGO_ENABLED", "0")
    return env


# ---------------------------------------------------------------------------
# Fail-to-pass: the actual bug fix
# ---------------------------------------------------------------------------

def test_rebuild_no_panic_two_dirs():
    """Regression: rebuild must not panic when pathChanges include two new
    dirs alongside a file change nested under another dir (issue 14573)."""
    _stage_test_addons()
    r = subprocess.run(
        ["go", "test", "-count=1", "-timeout=180s",
         "-run", "TestRebuildAddContentWithMultipleDirCreations_Issue14573$",
         "./hugolib/"],
        cwd=REPO, capture_output=True, text=True, env=_go_env(), timeout=600,
    )
    out = (r.stdout or "") + (r.stderr or "")
    assert "index out of range" not in out, (
        "rebuild still panics with index-out-of-range:\n" + out[-2000:]
    )
    assert r.returncode == 0, f"go test failed:\n{out[-2000:]}"


def test_rebuild_no_panic_four_dirs():
    """Regression variant: same scenario but with four new dirs — guards
    against a fix that only handles the n=2 case (issue 14573)."""
    _stage_test_addons()
    r = subprocess.run(
        ["go", "test", "-count=1", "-timeout=180s",
         "-run", "TestRebuildAddContentWithMultipleDirCreations_Issue14573_Wider$",
         "./hugolib/"],
        cwd=REPO, capture_output=True, text=True, env=_go_env(), timeout=600,
    )
    out = (r.stdout or "") + (r.stderr or "")
    assert "index out of range" not in out, (
        "rebuild still panics with index-out-of-range:\n" + out[-2000:]
    )
    assert r.returncode == 0, f"go test failed:\n{out[-2000:]}"


# ---------------------------------------------------------------------------
# Pass-to-pass: repo-level CI invariants (must hold before AND after fix)
# ---------------------------------------------------------------------------

def test_repo_compiles_go_build():
    """`go build ./...` must succeed."""
    r = subprocess.run(
        ["go", "build", "./..."],
        cwd=REPO, capture_output=True, text=True, env=_go_env(), timeout=600,
    )
    assert r.returncode == 0, (r.stderr or r.stdout)[-2000:]


def test_repo_go_vet_hugolib():
    """`go vet ./hugolib/` must be clean (with the regression test addon
    staged in)."""
    _stage_test_addons()
    r = subprocess.run(
        ["go", "vet", "./hugolib/"],
        cwd=REPO, capture_output=True, text=True, env=_go_env(), timeout=600,
    )
    assert r.returncode == 0, (r.stderr or r.stdout)[-2000:]


def test_gofmt_clean_site_go():
    """site.go must be gofmt-clean (root agent rule: ./check.sh runs gofmt)."""
    r = subprocess.run(
        ["gofmt", "-l", "hugolib/site.go"],
        cwd=REPO, capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0
    assert r.stdout.strip() == "", f"gofmt would reformat: {r.stdout!r}"


# ---------------------------------------------------------------------------
# Agent-config rules (root AGENTS.md)
# ---------------------------------------------------------------------------

def test_no_hdebug_printf_in_site_go():
    """AGENTS.md: temporary debug prints (hdebug.Printf) must NOT remain in
    committed code; CI fails if forgotten. Source: AGENTS.md L6 + footnote."""
    src = SITE_GO.read_text()
    assert "hdebug.Printf" not in src, (
        "site.go contains hdebug.Printf — debug prints must be removed"
    )


def test_fileEventsContentPaths_signature_unchanged():
    """The fix is a logic change inside the function — its signature must
    stay the same so call sites don't break (AGENTS.md: don't export new
    symbols not needed outside the package)."""
    src = SITE_GO.read_text()
    assert "func (h *HugoSites) fileEventsContentPaths(p []pathChange) []pathChange" in src, (
        "fileEventsContentPaths signature must remain unchanged"
    )

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