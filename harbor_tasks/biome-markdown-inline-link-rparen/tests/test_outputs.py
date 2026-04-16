"""
Tests for biomejs/biome#9642: fix(markdown-parser): incorrect inline link R_PAREN token range

The bug: When parsing inline links with titles (e.g., [link](/uri "title" )),
trailing whitespace before the closing parenthesis was being absorbed into the
R_PAREN token range, producing R_PAREN@X..Y " )" instead of R_PAREN@X..Y ")".
"""

import subprocess
import os
import re

REPO = "/workspace/biome"


def run_cmd(cmd, timeout=600):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout, cwd=REPO)
    return r


def test_markdown_parser_tests_pass():
    """Run the biome_markdown_parser test suite (pass_to_pass)."""
    r = run_cmd(["cargo", "test", "-p", "biome_markdown_parser"], timeout=600)
    assert r.returncode == 0, f"Markdown parser tests failed:\n{r.stderr[-2000:]}"


def test_links_rs_compiles():
    """The links.rs file compiles without errors (fail_to_pass)."""
    r = run_cmd(["cargo", "check", "-p", "biome_markdown_parser"], timeout=300)
    assert r.returncode == 0, f"Compilation failed:\n{r.stderr[-2000:]}"


def test_inline_link_snapshot_fixed():
    """The inline_link_whitespace snapshot reflects correct R_PAREN token ranges (fail_to_pass).

    The bug: trailing whitespace before the closing paren was absorbed into the
    R_PAREN token range (R_PAREN text = "  )" with length > 1 instead of just ")" length 1).
    After fix: R_PAREN token text is just ")" and trailing whitespace is in title content.

    This test verifies the fix by running cargo test (which executes the parser)
    AND checking the snapshot for the correct R_PAREN token structure.
    """
    # Run cargo test which compiles AND executes the Rust code against the snapshot.
    # This is behavioral: the parser runs and output is compared to snapshot.
    r = run_cmd(
        ["cargo", "test", "-p", "biome_markdown_parser", "--", "ok::ok::inline_link_whitespace_md"],
        timeout=300
    )
    assert r.returncode == 0, (
        f"inline_link_whitespace_md cargo test failed. "
        f"The parser output did not match the snapshot.\n"
        f"stderr: {r.stderr[-2000:]}"
    )

    # Verify the snapshot reflects correct behavior:
    # R_PAREN token text should be just ")" (length 1), NOT "  )" (length 3 with whitespace).
    # We check the OBSERVABLE PROPERTY (token text content) not exact byte positions.
    snapshot_path = os.path.join(
        REPO,
        "crates/biome_markdown_parser/tests/md_test_suite/ok/inline_link_whitespace.md.snap"
    )
    with open(snapshot_path) as f:
        content = f.read()

    # Extract all R_PAREN entries and their token text.
    # Pattern matches R_PAREN@{range} "{text}" and captures the text.
    r_paren_entries = re.findall(r'R_PAREN@(\d+\.\.\d+)\s+"([^"]+)"', content)
    assert len(r_paren_entries) > 0, "No R_PAREN entries found in snapshot"

    # Check that ALL R_PAREN tokens have text = ")" (just the closing paren, no whitespace).
    # The buggy snapshot has R_PAREN tokens with text like "  )" (whitespace absorbed).
    # The fixed snapshot has R_PAREN tokens with text = ")" (no whitespace absorbed).
    for range_str, text in r_paren_entries:
        assert text == ")", (
            f"Found R_PAREN@{range_str} with text {repr(text)} - "
            f"trailing whitespace was absorbed into R_PAREN token. "
            f"Expected text {repr(')')} (just closing paren, no whitespace). "
            f"The fix should consume trailing whitespace into the title content."
        )


def test_inline_link_whitespace_md_runs():
    """The inline_link_whitespace_md test runs without errors (fail_to_pass).

    On base commit (buggy): cargo test passes because parser output matches stored buggy snapshot.
    After fix: must run cargo insta review first to update snapshot, then test passes.
    If fix is applied but snapshot not updated: test FAILS (output differs from snapshot).
    """
    r = run_cmd(
        ["cargo", "test", "-p", "biome_markdown_parser", "--", "ok::ok::inline_link_whitespace_md"],
        timeout=300
    )
    assert r.returncode == 0, (
        f"inline_link_whitespace_md test failed. "
        f"This may mean the snapshot wasn't updated after the fix.\n"
        f"stderr: {r.stderr[-2000:]}"
    )


def test_repo_fmt():
    """Repo's formatting passes (pass_to_pass)."""
    r = run_cmd(["cargo", "fmt", "--all", "--", "--check"])
    assert r.returncode == 0, f"Formatting check failed:\n{r.stderr[-500:]}"


def test_repo_clippy():
    """Repo's clippy passes for biome_markdown_parser (pass_to_pass)."""
    r = run_cmd(["cargo", "clippy", "-p", "biome_markdown_parser", "--", "-D", "warnings"])
    assert r.returncode == 0, f"Clippy failed:\n{r.stderr[-500:]}"
