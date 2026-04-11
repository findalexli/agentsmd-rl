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

_RUST_TEST_CODE = r'''use biome_markdown_parser::parse_markdown;

/// Exact reproduction from PR #9775: blockquote with emoji, CJK, and inline link.
#[test]
fn parse_blockquote_multibyte_link() {
    let input = ">💡 Biomeは、[Prettierのオプションに対する考え方](https://example.com)と同様のアプローチを採用しています。";
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
    let input = ">📌 이것은 [테스트](https://example.com)입니다.";
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
    let input = ">🔧 配置は[正しい設定}](https://example.com)のはずです。さらに[もう一つ}](https://example.com/2)あります。";
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
    let input = "> [🚀🔥✨](https://example.com) テスト";
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
    """Write the shared Rust test file if not already present and format it."""
    if not _RUST_TEST_FILE.exists():
        _RUST_TEST_FILE.write_text(_RUST_TEST_CODE)
        # Format the generated file to match repo standards
        subprocess.run(
            ["cargo", "fmt", "--", str(_RUST_TEST_FILE)],
            cwd=REPO, capture_output=True, timeout=60,
        )


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


def test_repo_format_check():
    """Repo's Rust code formatting passes (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "fmt", "--all", "--", "--check"],
        cwd=REPO, capture_output=True, timeout=60,
    )
    assert r.returncode == 0, f"Format check failed:\n{r.stderr.decode()[-2000:]}"


def test_repo_markdown_list_tightness():
    """Markdown list tightness tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "test", "-p", "biome_markdown_parser", "--test", "list_tightness"],
        cwd=REPO, capture_output=True, timeout=300,
    )
    assert r.returncode == 0, f"List tightness tests failed:\n{r.stderr.decode()[-2000:]}"
