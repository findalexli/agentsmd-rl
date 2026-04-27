"""Verifier for hugo-tpl-css-fix-external-source-maps (PR gohugoio/hugo#14622)."""
from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path(os.environ.get("REPO", "/workspace/hugo"))
FIXTURES = Path("/tests/fixtures")

BUILD_GO = REPO / "internal/js/esbuild/build.go"
SOURCEMAP_GO = REPO / "internal/js/esbuild/sourcemap.go"
ESBUILD_PKG = REPO / "internal/js/esbuild"
CSS_PKG = REPO / "tpl/css"


def _run_go_test(test_name: str, package: str, timeout: int = 600) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["go", "test", "-count=1", "-timeout", "300s",
         "-run", test_name, package],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=timeout,
    )


@pytest.fixture(scope="session", autouse=True)
def install_fixtures():
    """Stage gold-version test files and the unit-test alignment check.

    Tests under fixtures/ are owned by the task and not visible to the agent;
    they replace stale assertions in the repo with the post-fix expectations.
    """
    shutil.copy(FIXTURES / "sourcemap_align_test.go",
                ESBUILD_PKG / "sourcemap_align_test.go")
    shutil.copy(FIXTURES / "build_integration_test.go",
                CSS_PKG / "build_integration_test.go")
    yield


# ─── fail-to-pass ─────────────────────────────────────────────────────────────

def test_fix_sourcemap_alignment_unit():
    """fixSourceMap must keep Sources and SourcesContent index-aligned after
    the resolver drops some entries (sourcemap.go fix)."""
    r = _run_go_test("TestFixSourceMapKeepsSourcesContentAligned",
                     "./internal/js/esbuild")
    assert r.returncode == 0, (
        f"go test failed (returncode={r.returncode})\n"
        f"--- stdout ---\n{r.stdout}\n--- stderr ---\n{r.stderr}"
    )


def test_fix_sourcemap_no_sourcescontent_unit():
    """fixSourceMap must still filter Sources when SourcesContent is null."""
    r = _run_go_test("TestFixSourceMapNoSourcesContent",
                     "./internal/js/esbuild")
    assert r.returncode == 0, (
        f"go test failed (returncode={r.returncode})\n"
        f"--- stdout ---\n{r.stdout}\n--- stderr ---\n{r.stderr}"
    )


def test_css_build_sourcemaps_integration():
    """End-to-end CSS build must produce a source map whose `sources` array
    has exactly 4 entries (main.css + foo.css + bar.css + baz.css), for both
    minify=true and minify=false. This exercises both build.go and
    sourcemap.go fixes through a real Hugo build."""
    r = _run_go_test("TestCSSBuildSourceMaps", "./tpl/css")
    assert r.returncode == 0, (
        f"go test failed (returncode={r.returncode})\n"
        f"--- stdout ---\n{r.stdout[-3000:]}\n--- stderr ---\n{r.stderr[-2000:]}"
    )


# ─── pass-to-pass ─────────────────────────────────────────────────────────────

def test_repo_existing_esbuild_unit_tests():
    """Pre-existing tests in internal/js/esbuild keep passing
    (regression guard for refactoring of fixSourceMap).

    Excludes the gold-test alignment checks installed by this verifier;
    those are scored separately as fail-to-pass."""
    r = subprocess.run(
        ["go", "test", "-count=1", "-timeout", "300s",
         "-skip", "TestFixSourceMap",
         "./internal/js/esbuild"],
        cwd=str(REPO), capture_output=True, text=True, timeout=600,
    )
    assert r.returncode == 0, (
        f"go test failed (returncode={r.returncode})\n"
        f"--- stdout ---\n{r.stdout[-3000:]}\n--- stderr ---\n{r.stderr[-2000:]}"
    )


def test_gofmt_clean():
    """gofmt must report no formatting issues on the modified files."""
    r = subprocess.run(
        ["gofmt", "-l",
         "internal/js/esbuild/build.go",
         "internal/js/esbuild/sourcemap.go"],
        cwd=str(REPO), capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"gofmt errored: {r.stderr}"
    assert r.stdout.strip() == "", (
        f"gofmt found formatting issues in:\n{r.stdout}"
    )


def test_go_vet_passes():
    """`go vet` reports no problems in the modified package."""
    r = subprocess.run(
        ["go", "vet", "./internal/js/esbuild"],
        cwd=str(REPO), capture_output=True, text=True, timeout=300,
    )
    assert r.returncode == 0, f"go vet failed:\n{r.stderr}"


def test_no_debug_print_left_behind():
    """Per AGENTS.md, hdebug.Printf is the only sanctioned debug-print
    helper; ensure no stray fmt.Printf/Println debug statements were left
    behind in the modified files."""
    for fp in (BUILD_GO, SOURCEMAP_GO):
        text = fp.read_text()
        for needle in ("fmt.Println", "fmt.Printf"):
            assert needle not in text, (
                f"{fp.name} contains a stray `{needle}` — use hdebug.Printf "
                f"for temporary debug output (AGENTS.md)."
            )


def test_no_unused_helper_left_behind():
    """The sourcemap.go fix collapses fixSourceMapSources into fixSourceMap;
    a lingering unexported helper would either be unused (caught by
    staticcheck) or duplicate logic. Per AGENTS.md, do not export symbols
    that aren't needed outside the package — and do not leave dead code."""
    text = SOURCEMAP_GO.read_text()
    # If fixSourceMapSources still exists, it must be referenced somewhere.
    if "func fixSourceMapSources" in text:
        # Look for a call site beyond the definition.
        assert text.count("fixSourceMapSources(") >= 2, (
            "fixSourceMapSources is defined but never called — dead code."
        )
