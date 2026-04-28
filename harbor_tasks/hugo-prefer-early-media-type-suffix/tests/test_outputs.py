"""Behavioral tests for hugo PR #14602.

Verifies that when multiple templates share the same base name but differ only
in file extension, and both extensions are valid suffixes for the same media
type, the template store prefers the one whose extension appears earliest in
the media type's `suffixes` list.
"""

import os
import shutil
import subprocess
import textwrap
from pathlib import Path

REPO = "/workspace/hugo"
INJECTED = Path(REPO) / "hugolib" / "task_extra_pr14602_test.go"


def _run_go_test(test_name: str, timeout: int = 600) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["go", "test", "-count=1", "-timeout", f"{timeout - 60}s",
         "-run", f"^{test_name}$", "./hugolib/"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def _write_injected_tests() -> None:
    INJECTED.write_text(textwrap.dedent('''\
        package hugolib

        import "testing"

        // Verifies suffix-priority resolution with declared order ["b","a","d","c"]:
        // page.html.b should win because "b" is the first declared suffix.
        func TestPR14602FirstSuffixB(t *testing.T) {
            t.Parallel()

            files := `
        -- hugo.toml --
        disableKinds = ['home','rss','section','sitemap','taxonomy','term']

        [mediaTypes.'text/html']
        suffixes = ['b','a','d','c']

        [outputFormats.html]
        mediaType = 'text/html'
        -- content/p1.md --
        ---
        title: p1
        ---
        -- layouts/page.html.a --
        page.html.a
        -- layouts/page.html.b --
        page.html.b
        -- layouts/page.html.c --
        page.html.c
        -- layouts/page.html.d --
        page.html.d
        `

            b := Test(t, files)
            b.AssertFileContent("public/p1/index.b", "page.html.b")
        }

        // Different suffix list, again with the winning suffix in the middle
        // of the alphabetical ordering of available layouts — guards against
        // agents hardcoding the letter "b" or any single-input shortcut.
        func TestPR14602FirstSuffixCAmongFour(t *testing.T) {
            t.Parallel()

            files := `
        -- hugo.toml --
        disableKinds = ['home','rss','section','sitemap','taxonomy','term']

        [mediaTypes.'text/html']
        suffixes = ['c','d','a','b']

        [outputFormats.html]
        mediaType = 'text/html'
        -- content/p2.md --
        ---
        title: p2
        ---
        -- layouts/page.html.a --
        page.html.a
        -- layouts/page.html.b --
        page.html.b
        -- layouts/page.html.c --
        page.html.c
        -- layouts/page.html.d --
        page.html.d
        `

            b := Test(t, files)
            b.AssertFileContent("public/p2/index.c", "page.html.c")
        }

        // Same scenario but the winning suffix is in the middle of the list,
        // not the first letter alphabetically — guards against any
        // implementation that just picks lexicographically smallest.
        func TestPR14602MiddleWinsByDeclaredOrder(t *testing.T) {
            t.Parallel()

            files := `
        -- hugo.toml --
        disableKinds = ['home','rss','section','sitemap','taxonomy','term']

        [mediaTypes.'text/html']
        suffixes = ['m','a','z']

        [outputFormats.html]
        mediaType = 'text/html'
        -- content/p3.md --
        ---
        title: p3
        ---
        -- layouts/page.html.a --
        page.html.a
        -- layouts/page.html.m --
        page.html.m
        -- layouts/page.html.z --
        page.html.z
        `

            b := Test(t, files)
            b.AssertFileContent("public/p3/index.m", "page.html.m")
        }
    '''))


def setup_module(module):
    _write_injected_tests()


def teardown_module(module):
    try:
        INJECTED.unlink()
    except FileNotFoundError:
        pass


# ---------------------------------------------------------------------------
# fail_to_pass: behavioral checks (require the fix)
# ---------------------------------------------------------------------------

def test_first_suffix_b_wins():
    """Template whose extension matches the first declared suffix wins."""
    r = _run_go_test("TestPR14602FirstSuffixB", timeout=600)
    assert r.returncode == 0, (
        "First-suffix selection failed.\n"
        f"STDOUT:\n{r.stdout[-2000:]}\n\n"
        f"STDERR:\n{r.stderr[-2000:]}"
    )


def test_first_suffix_c_among_four():
    """Same priority logic with a different first suffix ('c'). Verifies the
    winner is determined by declaration order, not alphabet or input length."""
    r = _run_go_test("TestPR14602FirstSuffixCAmongFour", timeout=600)
    assert r.returncode == 0, (
        "Suffix priority should not depend on alphabet.\n"
        f"STDOUT:\n{r.stdout[-2000:]}\n\n"
        f"STDERR:\n{r.stderr[-2000:]}"
    )


def test_middle_declared_suffix_wins():
    """Suffix priority is by declared order, not lexicographic."""
    r = _run_go_test("TestPR14602MiddleWinsByDeclaredOrder", timeout=600)
    assert r.returncode == 0, (
        "Suffix priority must follow declaration order.\n"
        f"STDOUT:\n{r.stdout[-2000:]}\n\n"
        f"STDERR:\n{r.stderr[-2000:]}"
    )


# ---------------------------------------------------------------------------
# pass_to_pass: regression / repo CI checks (must already pass at base)
# ---------------------------------------------------------------------------

def test_tplimpl_compiles():
    """`go build ./tpl/tplimpl/...` succeeds."""
    r = subprocess.run(
        ["go", "build", "./tpl/tplimpl/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert r.returncode == 0, f"Compilation failed:\n{r.stderr[-2000:]}"


def test_hugolib_compiles():
    """`go build ./hugolib/...` succeeds."""
    r = subprocess.run(
        ["go", "build", "./hugolib/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=900,
    )
    assert r.returncode == 0, f"Compilation failed:\n{r.stderr[-2000:]}"


def test_go_vet_tplimpl():
    """`go vet ./tpl/tplimpl/...` reports no issues."""
    r = subprocess.run(
        ["go", "vet", "./tpl/tplimpl/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert r.returncode == 0, f"go vet failed:\n{r.stderr[-2000:]}"


def test_gofmt_clean_on_touched_file():
    """`gofmt -l tpl/tplimpl/templatestore.go` reports no formatting drift."""
    r = subprocess.run(
        ["gofmt", "-l", "tpl/tplimpl/templatestore.go"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"gofmt errored:\n{r.stderr[-500:]}"
    assert r.stdout.strip() == "", (
        f"gofmt found unformatted files:\n{r.stdout}"
    )


def test_unrelated_template_test_still_passes():
    """A pre-existing template test must still pass — no regression."""
    r = _run_go_test("TestOverrideInternalTemplate", timeout=600)
    assert r.returncode == 0, (
        f"Pre-existing test regressed:\n"
        f"STDOUT:\n{r.stdout[-2000:]}\n\nSTDERR:\n{r.stderr[-2000:]}"
    )

# === PR-added f2p tests (taskforge.test_patch_miner) ===
def test_pr_added_TestTemplateSelectionFirstMediaTypeSuffix():
    """fail_to_pass | PR added test 'TestTemplateSelectionFirstMediaTypeSuffix' in 'hugolib/template_test.go' (go_test)"""
    r = _run_go_test("TestTemplateSelectionFirstMediaTypeSuffix", timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'TestTemplateSelectionFirstMediaTypeSuffix' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")
    assert "no tests to run" not in r.stdout, (
        "TestTemplateSelectionFirstMediaTypeSuffix was not found — the fix must add this test.\n"
        f"stdout: {r.stdout[-1500:]}")
