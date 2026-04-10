"""
Task: biome-md-last-hardline
Repo: biome @ 0bc2198735230c3bad14a831652543bd304fa0d6
PR:   9856

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import os
import subprocess
from pathlib import Path

REPO = "/workspace/biome"

# Custom Rust test code that exercises the markdown formatter directly.
# Written to quick_test.rs before running cargo test.
QUICK_TEST_RS = r'''
use biome_markdown_formatter::{MdFormatLanguage, context::MdFormatOptions};
use biome_markdown_parser::parse_markdown;

fn format_md(source: &str) -> String {
    let parse = parse_markdown(source);
    let options = MdFormatOptions::default();
    let result = biome_formatter::format_node(
        &parse.syntax(),
        MdFormatLanguage::new(options),
        false,
    ).unwrap();
    result.print().unwrap().as_code().to_string()
}

// Single-line paragraph ending with hard line break (two trailing spaces).
// The trailing spaces should be removed since the paragraph ends there anyway.
#[test]
fn test_single_last_hardline() {
    let output = format_md("foo  \n\n");
    assert!(!output.starts_with("foo  \n"),
        "Trailing spaces on last hard line should be removed. Got: {:?}", output);
    assert!(output.starts_with("foo\n"),
        "Content should be preserved without trailing spaces. Got: {:?}", output);
}

// Multi-line paragraph: middle hard line preserved, last one removed.
#[test]
fn test_multi_last_hardline() {
    let output = format_md("aaa     \nbbb     \n\n");
    // Middle hard line (aaa) should keep its two-space marker
    assert!(output.contains("aaa  \n"),
        "Middle hard line should be preserved with 2 spaces. Got: {:?}", output);
    // Last hard line (bbb) should NOT have trailing spaces
    assert!(!output.contains("bbb  \n"),
        "Last hard line trailing spaces should be removed. Got: {:?}", output);
    assert!(output.contains("bbb\n"),
        "Last line content should be preserved. Got: {:?}", output);
}

// Varied content to prevent hardcoded constant solutions.
#[test]
fn test_varied_last_hardline() {
    let output = format_md("hello world  \ngoodbye  \n\n");
    assert!(output.contains("hello world  \n"),
        "Middle hard line should be preserved. Got: {:?}", output);
    assert!(output.contains("goodbye\n"),
        "Last hard line trailing spaces should be removed. Got: {:?}", output);
    assert!(!output.contains("goodbye  \n"),
        "Should not have trailing spaces on last line. Got: {:?}", output);
}
'''


def _ensure_quick_test():
    """Write the custom Rust test file to the formatter crate."""
    qt_path = os.path.join(REPO, "crates/biome_markdown_formatter/tests/quick_test.rs")
    Path(qt_path).write_text(QUICK_TEST_RS)


def _run_rust_test(test_name: str, timeout: int = 600) -> subprocess.CompletedProcess:
    """Run a specific Rust test from the quick_test module."""
    return subprocess.run(
        ["cargo", "test", "-p", "biome_markdown_formatter",
         "--test", "spec_tests", f"quick_test::{test_name}", "--", "--exact"],
        cwd=REPO, capture_output=True, timeout=timeout,
    )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_cargo_check():
    """Formatter crate compiles without errors."""
    _ensure_quick_test()
    r = subprocess.run(
        ["cargo", "check", "-p", "biome_markdown_formatter"],
        cwd=REPO, capture_output=True, timeout=600,
    )
    assert r.returncode == 0, (
        f"Compilation failed:\n{r.stderr.decode()[-2000:]}"
    )


# [repo_tests] pass_to_pass
def test_markdown_formatter_tests():
    """Repo's markdown formatter prettier tests pass (pass_to_pass)."""
    # Run prettier_tests only - these don't depend on quick_test.rs content
    r = subprocess.run(
        ["cargo", "test", "-p", "biome_markdown_formatter", "--test", "prettier_tests", "--", "--test-threads=1"],
        cwd=REPO, capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, (
        f"Markdown formatter tests failed:\n{r.stderr[-500:]}"
    )


# [repo_tests] pass_to_pass
def test_markdown_parser_check():
    """Markdown parser crate compiles without errors (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "check", "-p", "biome_markdown_parser"],
        cwd=REPO, capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, (
        f"Markdown parser check failed:\n{r.stderr[-500:]}"
    )


# [repo_tests] pass_to_pass
def test_markdown_formatter_spec_tests():
    """Repo's markdown formatter spec tests pass (pass_to_pass)."""
    # Run only formatter tests, exclude quick_test which has the fail_to_pass tests
    r = subprocess.run(
        ["cargo", "test", "-p", "biome_markdown_formatter", "--test", "spec_tests", "formatter", "--", "--test-threads=1"],
        cwd=REPO, capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, (
        f"Markdown formatter spec tests failed:\n{r.stderr[-500:]}"
    )

# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_single_last_hardline():
    """Single-line paragraph: trailing hard line break spaces removed."""
    _ensure_quick_test()
    r = _run_rust_test("test_single_last_hardline")
    assert r.returncode == 0, (
        f"Test failed:\\n{r.stdout.decode()[-1000:]}\\n{r.stderr.decode()[-1000:]}"
    )


# [pr_diff] fail_to_pass
def test_multi_last_hardline():
    """Multi-line paragraph: last hard line removed, middle preserved."""
    _ensure_quick_test()
    r = _run_rust_test("test_multi_last_hardline")
    assert r.returncode == 0, (
        f"Test failed:\\n{r.stdout.decode()[-1000:]}\\n{r.stderr.decode()[-1000:]}"
    )


# [pr_diff] fail_to_pass
def test_varied_last_hardline():
    """Different paragraph content to prevent hardcoded solutions."""
    _ensure_quick_test()
    r = _run_rust_test("test_varied_last_hardline")
    assert r.returncode == 0, (
        f"Test failed:\\n{r.stdout.decode()[-1000:]}\\n{r.stderr.decode()[-1000:]}"
    )
