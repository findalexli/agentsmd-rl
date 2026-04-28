"""Tests for biome HTML formatter PR #8833 (force-break + display:none handling)."""
from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path("/workspace/biome")
WHITESPACE_DIR = REPO / "crates/biome_html_formatter/tests/specs/html/whitespace"
FIXTURES = Path("/tests/fixtures")

FIXTURE_FILES = [
    "force-break-nontext-and-non-sensitive-sibling.html",
    "force-break-nontext-and-non-sensitive-sibling.html.snap",
    "force-break-nontext-and-non-sensitive-sibling-2.html",
    "force-break-nontext-and-non-sensitive-sibling-2.html.snap",
    "no-break-display-none.html",
    "no-break-display-none.html.snap",
]


def _refresh_fixtures() -> None:
    """Re-copy test fixtures into the repo to defend against tampering."""
    for name in FIXTURE_FILES:
        src = FIXTURES / name
        dst = WHITESPACE_DIR / name
        if not src.exists():
            raise FileNotFoundError(f"fixture missing: {src}")
        shutil.copy(src, dst)


@pytest.fixture(scope="module")
def cargo_results() -> dict[str, str]:
    """Run the html_formatter spec_tests once and return a {test_name: status} map.

    Cargo's first invocation in a fresh container does ~55s of re-link work
    even when sources are unchanged (a docker layer fingerprint quirk); after
    that, repeated runs are sub-second. So we run cargo test exactly once
    here at module scope.
    """
    _refresh_fixtures()

    # libtest's text output: lines like "test foo::bar ... ok" or "... FAILED"
    proc = subprocess.run(
        [
            "cargo",
            "test",
            "-p",
            "biome_html_formatter",
            "--test",
            "spec_tests",
            "--no-fail-fast",
            "--",
            "--test-threads",
            "1",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
    )
    output = proc.stdout + proc.stderr
    status: dict[str, str] = {}
    pattern = re.compile(r"^test (\S+) \.\.\. (ok|FAILED|ignored)\s*$", re.MULTILINE)
    for match in pattern.finditer(output):
        name, result = match.group(1), match.group(2)
        # Ignore the per-test-binary "test result:" summary lines (they don't match).
        if "::" in name:
            status[name] = result
    if not status:
        pytest.fail(
            f"could not parse any test results from cargo output\n"
            f"stdout tail:\n{proc.stdout[-1500:]}\n"
            f"stderr tail:\n{proc.stderr[-1500:]}"
        )
    return status


# --- Fail-to-pass ---------------------------------------------------------


def test_force_break_block_like_sibling_with_text(cargo_results: dict[str, str]) -> None:
    """A visible block-like child (e.g. `<div>`) adjacent to text in a parent
    must force the parent onto multiple lines.

    Concretely: ``<div>a<div>b</div> c</div>`` should reformat to a
    four-line block; on the buggy base it stays on a single line and the
    snapshot test fails.
    """
    name = "formatter::html::html::whitespace::force_break_nontext_and_non_sensitive_sibling_html"
    if name not in cargo_results:
        pytest.fail(f"test {name} did not run; cargo_results keys: {sorted(cargo_results)[:10]} ...")
    assert cargo_results[name] == "ok", (
        f"{name} status={cargo_results[name]} (expected ok). "
        f"On the buggy base commit the formatter emits "
        f"'<div>a<div>b</div> c</div>' on a single line; it should break."
    )


def test_force_break_block_like_sibling_with_text_variant(cargo_results: dict[str, str]) -> None:
    """Second fail-to-pass: a different visible block-like element
    (``<article>``) adjacent to text must also force parent multiline.

    Input ``<div>before<article>middle</article>after</div>`` must
    reformat to a four-line block; on the buggy base it stays on a
    single line.
    """
    name = "formatter::html::html::whitespace::force_break_nontext_and_non_sensitive_sibling_2_html"
    if name not in cargo_results:
        pytest.fail(f"test {name} did not run; cargo_results keys: {sorted(cargo_results)[:10]} ...")
    assert cargo_results[name] == "ok", (
        f"{name} status={cargo_results[name]} (expected ok). "
        f"On the buggy base commit the formatter does not break "
        f"around a visible block-like <article> child; it should."
    )


# --- Pass-to-pass: regression guards on the same code-path ----------------


def test_no_break_around_display_none_element(cargo_results: dict[str, str]) -> None:
    """Whitespace-sensitive children adjacent to a ``display: none`` element
    (e.g. ``<meta>``) must NOT be split onto separate lines.

    Input ``<div>123<meta attr />456</div>`` should stay on one line; this
    is the regression case the new branch in element_list.rs guards.
    """
    name = "formatter::html::html::whitespace::no_break_display_none_html"
    assert cargo_results.get(name) == "ok", (
        f"{name} status={cargo_results.get(name)} (expected ok). "
        f"display:none elements must not introduce whitespace breaks."
    )


def test_existing_whitespace_preserve_newline(cargo_results: dict[str, str]) -> None:
    """Existing snapshot test for newline preservation must still pass."""
    name = "formatter::html::html::whitespace::preserve_newline_after_element_html"
    assert cargo_results.get(name) == "ok", f"{name} regressed: {cargo_results.get(name)}"


def test_existing_whitespace_preserve_space(cargo_results: dict[str, str]) -> None:
    """Existing snapshot test for space preservation must still pass."""
    name = "formatter::html::html::whitespace::preserve_space_after_element_html"
    assert cargo_results.get(name) == "ok", f"{name} regressed: {cargo_results.get(name)}"


def test_no_other_spec_test_regressions(cargo_results: dict[str, str]) -> None:
    """No spec_tests outside the two new whitespace tests should regress.

    The PR only changes formatter logic for text-adjacent block-like /
    display:none siblings; every other spec test is a regression guard.
    """
    new_test_ids = {
        "formatter::html::html::whitespace::force_break_nontext_and_non_sensitive_sibling_html",
        "formatter::html::html::whitespace::force_break_nontext_and_non_sensitive_sibling_2_html",
        "formatter::html::html::whitespace::no_break_display_none_html",
    }
    failures = [
        name
        for name, st in cargo_results.items()
        if st == "FAILED" and name not in new_test_ids
    ]
    assert not failures, f"unexpected spec_test regressions: {failures}"


# --- Pass-to-pass: repo CI tooling ---------------------------------------


def test_repo_cargo_fmt_check() -> None:
    """`cargo fmt --check` must pass on the whole workspace."""
    r = subprocess.run(
        ["cargo", "fmt", "--check"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"cargo fmt failed:\n{r.stdout}\n{r.stderr}"


def test_repo_cargo_clippy_html_formatter() -> None:
    """`cargo clippy` on biome_html_formatter must pass with --deny warnings."""
    r = subprocess.run(
        [
            "cargo",
            "clippy",
            "-p",
            "biome_html_formatter",
            "--all-targets",
            "--",
            "--deny",
            "warnings",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert r.returncode == 0, f"cargo clippy failed:\n{r.stderr[-2000:]}"
