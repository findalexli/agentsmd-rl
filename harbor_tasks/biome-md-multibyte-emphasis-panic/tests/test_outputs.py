"""
Task: biome-md-multibyte-emphasis-panic
Repo: biome @ b22f31afd5e0d40cf5a2b10dad85accf7d34a2b8
PR:   9775

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/biome"

# Shared Rust integration test file used by the f2p tests below.
# Written once; subsequent tests reuse the cached compilation.
_RUST_TEST_FILE = Path(REPO) / "crates/biome_markdown_parser/tests/test_multibyte_panic_check.rs"

_RUST_TEST_CODE = r'''\
use biome_markdown_parser::parse_markdown;

/// Exact reproduction from PR #9775: blockquote with emoji, CJK, and inline link.
#[test]
fn parse_blockquote_multibyte_link() {
    let input = ">\u{1f4a1} Biome\u{306f}\u{3001}[Prettier\u{306e}\u{30aa}\u{30d7}\u{30b7}\u{30e7}\u{30f3}\u{306b}\u{5bfe}\u{3059}\u{308b}\u{8003}\u{3048}\u{65b9}](https://example.com)\u{3068}\u{540c}\u{69d8}\u{306e}\u{30a2}\u{30d7}\u{30ed}\u{30fc}\u{30c1}\u{3092}\u{63a1}\u{7528}\u{3057}\u{3066}\u{3044}\u{307e}\u{3059}\u{3002}";
    let result = parse_markdown(input);
    let tree = result.tree();
    let tree_str = format!("{tree:#?}");
    assert!(result.diagnostics().is_empty(),
        "Parser produced errors: {:?}", result.diagnostics());
    assert!(tree_str.contains("MdInlineLink"),
        "Expected MdInlineLink in parsed tree, got:\n{tree_str}");
    assert!(tree_str.contains("MdQuote"),
        "Expected MdQuote in parsed tree");
}

/// Korean text inside a blockquote with links.
#[test]
fn parse_korean_blockquote_link() {
    let input = ">\u{1f4cc} \u{c774}\u{ac83}\uc740 [\ud14c\uc2a4\ud2b8](https://example.com)\uc785\ub2c8\ub2e4.";
    let result = parse_markdown(input);
    let tree = result.tree();
    let tree_str = format!("{tree:#?}");
    assert!(result.diagnostics().is_empty(),
        "Parser produced errors: {:?}", result.diagnostics());
    assert!(tree_str.contains("MdInlineLink"),
        "Expected MdInlineLink in parsed tree");
}

/// Multiple inline links with CJK text between them.
#[test]
fn parse_multiple_multibyte_links() {
    let input = ">\u{1f527} \u914d\u7f6e\u306f[\u6b63\u3057\u3044\u8a2d\u5b9a}](https://example.com)\u306e\u306f\u305a\u3067\u3059\u3002\u3055\u3089\u306b[\u3082\u3046\u4e00\u3064}](https://example.com/2)\u3042\u308a\u307e\u3059\u3002";
    let result = parse_markdown(input);
    let tree = result.tree();
    let tree_str = format!("{tree:#?}");
    assert!(result.diagnostics().is_empty(),
        "Parser produced errors: {:?}", result.diagnostics());
    // Must find both inline links
    assert!(tree_str.matches("MdInlineLink").count() >= 2,
        "Expected at least 2 MdInlineLink nodes");
}

/// Emoji-only link text in a blockquote.
#[test]
fn parse_emoji_only_link() {
    let input = "> [\u{1f680}\u{1f525}\u{2728}](https://example.com) \u30c6\u30b9\u30c8";
    let result = parse_markdown(input);
    let tree = result.tree();
    let tree_str = format!("{tree:#?}");
    assert!(result.diagnostics().is_empty(),
        "Parser produced errors: {:?}", result.diagnostics());
    assert!(tree_str.contains("MdInlineLink"),
        "Expected MdInlineLink in parsed tree");
}
'''


def _ensure_test_file():
    """Write the shared Rust test file if not already present."""
    if not _RUST_TEST_FILE.exists():
        _RUST_TEST_FILE.write_text(_RUST_TEST_CODE)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — compilation check
# ---------------------------------------------------------------------------

def test_cargo_check():
    """Modified crate must compile without errors."""
    r = subprocess.run(
        ["cargo", "check", "-p", "biome_markdown_parser"],
        cwd=REPO, capture_output=True, timeout=300,
    )
    assert r.returncode == 0, f"Compilation failed:\n{r.stderr.decode()[-3000:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

def test_parse_multibyte_emphasis():
    """Parsing markdown with multi-byte chars in blockquote+link context must not panic."""
    _ensure_test_file()
    r = subprocess.run(
        ["cargo", "test", "-p", "biome_markdown_parser",
         "--test", "test_multibyte_panic_check", "--",
         "parse_blockquote_multibyte_link"],
        cwd=REPO, capture_output=True, timeout=600,
    )
    assert r.returncode == 0, (
        f"Multi-byte emphasis parsing failed (likely panic on char boundary):\n"
        f"{r.stderr.decode()[-3000:]}"
    )


def test_parse_multibyte_emphasis_varied():
    """Different multi-byte inputs in inline emphasis context must not panic."""
    _ensure_test_file()
    r = subprocess.run(
        ["cargo", "test", "-p", "biome_markdown_parser",
         "--test", "test_multibyte_panic_check", "--",
         "parse_korean_blockquote_link", "parse_multiple_multibyte_links",
         "parse_emoji_only_link"],
        cwd=REPO, capture_output=True, timeout=600,
    )
    assert r.returncode == 0, (
        f"Varied multi-byte parsing failed:\n"
        f"{r.stderr.decode()[-3000:]}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — regression
# ---------------------------------------------------------------------------

def test_existing_markdown_parser_tests():
    """Existing markdown parser spec tests still pass."""
    r = subprocess.run(
        ["cargo", "test", "-p", "biome_markdown_parser", "--test", "spec_test"],
        cwd=REPO, capture_output=True, timeout=600,
    )
    assert r.returncode == 0, (
        f"Existing spec tests failed:\n"
        f"{r.stderr.decode()[-3000:]}"
    )


def test_repo_markdown_parser_clippy():
    """Repo's clippy lints pass for markdown parser crate (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "clippy", "-p", "biome_markdown_parser", "--all-features", "--all-targets", "--", "--deny", "warnings"],
        cwd=REPO, capture_output=True, timeout=300,
    )
    assert r.returncode == 0, f"Clippy failed:\n{r.stderr.decode()[-2000:]}"


def test_repo_markdown_parser_all_tests():
    """All markdown parser tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "test", "-p", "biome_markdown_parser"],
        cwd=REPO, capture_output=True, timeout=300,
    )
    assert r.returncode == 0, f"Tests failed:\n{r.stderr.decode()[-2000:]}"


def test_repo_markdown_formatter_tests():
    """Markdown formatter tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "test", "-p", "biome_markdown_formatter"],
        cwd=REPO, capture_output=True, timeout=300,
    )
    assert r.returncode == 0, f"Formatter tests failed:\n{r.stderr.decode()[-2000:]}"


def test_repo_format_check():
    """Repo's Rust code formatting passes (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "fmt", "--all", "--", "--check"],
        cwd=REPO, capture_output=True, timeout=60,
    )
    assert r.returncode == 0, f"Format check failed:\n{r.stderr.decode()[-2000:]}"


def test_repo_related_markdown_crates_check():
    """Related markdown crates compile without errors (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "check", "-p", "biome_markdown_factory", "-p", "biome_markdown_syntax", "-p", "biome_markdown_formatter"],
        cwd=REPO, capture_output=True, timeout=300,
    )
    assert r.returncode == 0, f"Related markdown crates check failed:\n{r.stderr.decode()[-2000:]}"
