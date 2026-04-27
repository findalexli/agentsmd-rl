"""Behavior tests for strings.ReplacePairs in Hugo's tpl/strings package.

Each test invokes `go test` with build tag `rpextras` against an injected
Go test file. At base (no ReplacePairs method), the Go package fails to
compile under -tags=rpextras and the tests fail.
"""

import os
import subprocess
from pathlib import Path

import pytest

REPO = Path("/workspace/hugo")
STRINGS_PKG = REPO / "tpl" / "strings"
EXTRAS_DST = STRINGS_PKG / "extras_replacepairs_test.go"

_EXTRAS_GO = r'''//go:build rpextras
// +build rpextras

package strings

import (
	"html/template"
	"testing"

	qt "github.com/frankban/quicktest"
)

func TestRPExt_InlineSinglePair(t *testing.T) {
	c := qt.New(t)
	r, err := ns.ReplacePairs("a", "b", "aab")
	c.Assert(err, qt.IsNil)
	c.Assert(r, qt.Equals, "bbb")
}

func TestRPExt_InlineMultiplePairs(t *testing.T) {
	c := qt.New(t)
	r, err := ns.ReplacePairs("a", "b", "b", "c", "aab")
	c.Assert(err, qt.IsNil)
	c.Assert(r, qt.Equals, "bbc")
}

func TestRPExt_SliceForm(t *testing.T) {
	c := qt.New(t)
	r, err := ns.ReplacePairs([]string{"a", "b", "b", "c"}, "aab")
	c.Assert(err, qt.IsNil)
	c.Assert(r, qt.Equals, "bbc")
}

func TestRPExt_SinglePass(t *testing.T) {
	c := qt.New(t)
	r, err := ns.ReplacePairs([]string{"app", "pear", "apple", "orange"}, "apple")
	c.Assert(err, qt.IsNil)
	c.Assert(r, qt.Equals, "pearle")
}

func TestRPExt_TemplateHTMLSource(t *testing.T) {
	c := qt.New(t)
	r, err := ns.ReplacePairs([]string{"a", "b"}, template.HTML("aab"))
	c.Assert(err, qt.IsNil)
	c.Assert(r, qt.Equals, "bbb")
}

func TestRPExt_EmptySource(t *testing.T) {
	c := qt.New(t)
	r, err := ns.ReplacePairs("a", "b", "")
	c.Assert(err, qt.IsNil)
	c.Assert(r, qt.Equals, "")
}

func TestRPExt_EmptyPairs(t *testing.T) {
	c := qt.New(t)
	r, err := ns.ReplacePairs([]string{}, "aab")
	c.Assert(err, qt.IsNil)
	c.Assert(r, qt.Equals, "aab")
}

func TestRPExt_TooFewArgs(t *testing.T) {
	c := qt.New(t)
	_, err := ns.ReplacePairs()
	c.Assert(err, qt.ErrorMatches, ".*requires at least 2.*")
	_, err = ns.ReplacePairs("s")
	c.Assert(err, qt.ErrorMatches, ".*requires at least 2.*")
}

func TestRPExt_TwoArgsFirstNotSlice(t *testing.T) {
	c := qt.New(t)
	_, err := ns.ReplacePairs("a", "s")
	c.Assert(err, qt.ErrorMatches, ".*first must be a slice.*")
	_, err = ns.ReplacePairs(42, "s")
	c.Assert(err, qt.ErrorMatches, ".*first must be a slice.*")
}

func TestRPExt_UnevenPairs(t *testing.T) {
	c := qt.New(t)
	_, err := ns.ReplacePairs([]string{"a"}, "s")
	c.Assert(err, qt.ErrorMatches, ".*uneven number.*")
	_, err = ns.ReplacePairs("a", "b", "c", "s")
	c.Assert(err, qt.ErrorMatches, ".*uneven number.*")
}

func TestRPExt_TemplateHTMLPair(t *testing.T) {
	c := qt.New(t)
	r, err := ns.ReplacePairs(template.HTML("a"), "b", "aab")
	c.Assert(err, qt.IsNil)
	c.Assert(r, qt.Equals, "bbb")
}

func TestRPExt_IntCastSource(t *testing.T) {
	c := qt.New(t)
	r, err := ns.ReplacePairs([]string{"a", "b"}, 42)
	c.Assert(err, qt.IsNil)
	c.Assert(r, qt.Equals, "42")
}

func TestRPExt_AnyTypeSliceWithIntPair(t *testing.T) {
	c := qt.New(t)
	r, err := ns.ReplacePairs([]any{1, "one"}, "1abc")
	c.Assert(err, qt.IsNil)
	c.Assert(r, qt.Equals, "oneabc")
}

func TestRPExt_MultipleCallsCacheReuse(t *testing.T) {
	c := qt.New(t)
	pairs := []string{"foo", "bar", "baz", "qux"}
	for i := 0; i < 5; i++ {
		r, err := ns.ReplacePairs(pairs, "foo baz")
		c.Assert(err, qt.IsNil)
		c.Assert(r, qt.Equals, "bar qux")
	}
}
'''


def setup_module(module):
    """Inject the extras Go test file into Hugo's tpl/strings package."""
    EXTRAS_DST.write_text(_EXTRAS_GO)


def teardown_module(module):
    """Remove the injected extras file."""
    try:
        EXTRAS_DST.unlink()
    except FileNotFoundError:
        pass


def _go_test(test_name: str, with_extras: bool = True, timeout: int = 600):
    """Run `go test` for a single Go test name. Returns CompletedProcess."""
    cmd = ["go", "test", "-count=1", "-v"]
    if with_extras:
        cmd += ["-tags=rpextras"]
    cmd += ["-run", f"^{test_name}$", "./tpl/strings/"]
    return subprocess.run(
        cmd, cwd=str(REPO), capture_output=True, text=True, timeout=timeout
    )


def _assert_go_test_passed(r, name):
    """Assert: Go test compiled, ran, and passed (no false 'no tests' positives)."""
    assert r.returncode == 0, (
        f"{name}: go test exit={r.returncode}\n"
        f"--- stdout ---\n{r.stdout[-3000:]}\n"
        f"--- stderr ---\n{r.stderr[-1500:]}"
    )
    # Go's `go test -run X` prints "ok ... --- PASS: TestName" when X matches.
    # If X matches nothing, output is just "ok ... 0 tests" or similar — no
    # "--- PASS:" line. Require the per-test PASS line as proof of execution.
    assert "--- PASS:" in r.stdout, (
        f"{name}: per-test PASS line missing — test may not have been "
        f"compiled or matched by -run\n{r.stdout[-2000:]}"
    )


# ── fail-to-pass: behavior ─────────────────────────────────────────────────

def test_inline_form_single_pair():
    r = _go_test("TestRPExt_InlineSinglePair")
    _assert_go_test_passed(r, "TestRPExt_InlineSinglePair")


def test_inline_form_multiple_pairs():
    r = _go_test("TestRPExt_InlineMultiplePairs")
    _assert_go_test_passed(r, "TestRPExt_InlineMultiplePairs")


def test_slice_form():
    r = _go_test("TestRPExt_SliceForm")
    _assert_go_test_passed(r, "TestRPExt_SliceForm")


def test_single_pass_replacement():
    r = _go_test("TestRPExt_SinglePass")
    _assert_go_test_passed(r, "TestRPExt_SinglePass")


def test_template_html_source():
    r = _go_test("TestRPExt_TemplateHTMLSource")
    _assert_go_test_passed(r, "TestRPExt_TemplateHTMLSource")


def test_empty_source_returns_empty():
    r = _go_test("TestRPExt_EmptySource")
    _assert_go_test_passed(r, "TestRPExt_EmptySource")


def test_empty_pairs_returns_source_unchanged():
    r = _go_test("TestRPExt_EmptyPairs")
    _assert_go_test_passed(r, "TestRPExt_EmptyPairs")


def test_template_html_pair_value():
    r = _go_test("TestRPExt_TemplateHTMLPair")
    _assert_go_test_passed(r, "TestRPExt_TemplateHTMLPair")


def test_int_source_cast_to_string():
    r = _go_test("TestRPExt_IntCastSource")
    _assert_go_test_passed(r, "TestRPExt_IntCastSource")


def test_any_slice_with_int_pair_value():
    r = _go_test("TestRPExt_AnyTypeSliceWithIntPair")
    _assert_go_test_passed(r, "TestRPExt_AnyTypeSliceWithIntPair")


def test_repeated_calls_consistent():
    r = _go_test("TestRPExt_MultipleCallsCacheReuse")
    _assert_go_test_passed(r, "TestRPExt_MultipleCallsCacheReuse")


# ── fail-to-pass: errors ───────────────────────────────────────────────────

def test_error_too_few_args():
    r = _go_test("TestRPExt_TooFewArgs")
    _assert_go_test_passed(r, "TestRPExt_TooFewArgs")


def test_error_two_args_first_not_slice():
    r = _go_test("TestRPExt_TwoArgsFirstNotSlice")
    _assert_go_test_passed(r, "TestRPExt_TwoArgsFirstNotSlice")


def test_error_uneven_pairs():
    r = _go_test("TestRPExt_UnevenPairs")
    _assert_go_test_passed(r, "TestRPExt_UnevenPairs")


# ── fail-to-pass: registration ─────────────────────────────────────────────

def test_method_registered_in_init():
    """init.go registers ReplacePairs via ns.AddMethodMapping; package builds."""
    init_go = (STRINGS_PKG / "init.go").read_text()
    assert "ReplacePairs" in init_go, (
        "init.go must register ReplacePairs via ns.AddMethodMapping(...) so "
        "templates can call strings.ReplacePairs"
    )
    r = subprocess.run(
        ["go", "build", "./tpl/strings/..."],
        cwd=str(REPO), capture_output=True, text=True, timeout=600,
    )
    assert r.returncode == 0, f"go build failed:\n{r.stderr[-2000:]}"


# ── pass-to-pass: existing repo tests ──────────────────────────────────────

def test_existing_strings_tests_pass():
    """Repo's existing tpl/strings tests pass (regression guard)."""
    r = subprocess.run(
        ["go", "test", "-count=1", "./tpl/strings/"],
        cwd=str(REPO), capture_output=True, text=True, timeout=900,
    )
    assert r.returncode == 0, (
        f"existing tests failed:\nstdout:{r.stdout[-2000:]}\nstderr:{r.stderr[-2000:]}"
    )


def test_go_vet_clean():
    """go vet finds no issues in tpl/strings."""
    r = subprocess.run(
        ["go", "vet", "./tpl/strings/..."],
        cwd=str(REPO), capture_output=True, text=True, timeout=300,
    )
    assert r.returncode == 0, f"go vet failed:\n{r.stderr[-2000:]}"


def test_gofmt_clean():
    """Modified files conform to gofmt."""
    r = subprocess.run(
        ["gofmt", "-l", "tpl/strings/strings.go", "tpl/strings/init.go"],
        cwd=str(REPO), capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"gofmt errored:\n{r.stderr}"
    assert r.stdout.strip() == "", f"files need gofmt:\n{r.stdout}"
