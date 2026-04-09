"""
Task: biome-astro-regex-escape-frontmatter
Repo: biome @ 467fd87daec3d8c1fe64850a82480364480b313e
PR:   9728

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = Path("/workspace/biome")
LEXER_MOD = REPO / "crates/biome_html_parser/src/lexer/mod.rs"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — compilation check
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_compilation():
    """biome_html_parser crate must compile without errors."""
    r = subprocess.run(
        ["cargo", "check", "-p", "biome_html_parser"],
        cwd=REPO, capture_output=True, timeout=300,
    )
    assert r.returncode == 0, (
        f"Compilation failed:\n{r.stderr.decode()[-2000:]}"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# Rust integration test code that exercises the parser with escaped regex
# patterns in Astro frontmatter.  Written to a temp file and compiled/run
# via cargo test.
_RUST_INTEGRATION_TEST = r'''
use biome_html_parser::{parse_html, HtmlParserOptions};
use biome_html_syntax::HtmlFileSource;

/// Regex `/\d{4}/` inside Astro frontmatter must parse without diagnostics.
#[test]
fn astro_regex_escape_quantifier_d4() {
    let file_source = HtmlFileSource::astro();
    let options = HtmlParserOptions::from(&file_source);
    let source = "---\nconst RE = /\\d{4}/\n---\n\n<div />\n";
    let parsed = parse_html(source, options);
    assert!(
        parsed.diagnostics().is_empty(),
        "Expected 0 diagnostics for /\\d{{4}}/, got {}",
        parsed.diagnostics().len(),
    );
}

/// Regex `/\w{2,3}/` inside Astro frontmatter must also parse cleanly.
#[test]
fn astro_regex_escape_quantifier_w23() {
    let file_source = HtmlFileSource::astro();
    let options = HtmlParserOptions::from(&file_source);
    let source = "---\nconst RE = /\\w{2,3}/\n---\n\n<p />\n";
    let parsed = parse_html(source, options);
    assert!(
        parsed.diagnostics().is_empty(),
        "Expected 0 diagnostics for /\\w{{2,3}}/, got {}",
        parsed.diagnostics().len(),
    );
}

/// Multiple regex literals with escapes on the same line.
#[test]
fn astro_multiple_regex_on_one_line() {
    let file_source = HtmlFileSource::astro();
    let options = HtmlParserOptions::from(&file_source);
    let source = "---\nconst a = /\\d+/; const b = /\\w{3}/;\n---\n\n<span />\n";
    let parsed = parse_html(source, options);
    assert!(
        parsed.diagnostics().is_empty(),
        "Expected 0 diagnostics for multiple regex literals, got {}",
        parsed.diagnostics().len(),
    );
}
'''


# [pr_diff] fail_to_pass
def test_astro_regex_escape_frontmatter():
    """Astro frontmatter with escaped regex patterns must parse without errors."""
    test_file = REPO / "crates/biome_html_parser/tests/test_astro_regex.rs"
    test_file.write_text(_RUST_INTEGRATION_TEST)
    try:
        r = subprocess.run(
            ["cargo", "test", "-p", "biome_html_parser",
             "--test", "test_astro_regex", "--", "--nocapture"],
            cwd=REPO, capture_output=True, timeout=300,
        )
        output = r.stdout.decode() + r.stderr.decode()
        assert r.returncode == 0, (
            f"Integration test failed (regex in Astro frontmatter):\n"
            f"{output[-3000:]}"
        )
    finally:
        test_file.unlink(missing_ok=True)


# [pr_diff] fail_to_pass
def test_escape_handler_order():
    """General escape handler must come AFTER deferred slash resolution.

    In QuotesSeen::check_byte, the block:
        if byte == b'\\\\' { ... self.prev_non_ws_byte = Some(byte); ... }
    must appear after the call to self.slash_starts_regex().  If escape
    handling runs first, a deferred '/' is overwritten before it can be
    resolved as a regex opener.
    """
    src = LEXER_MOD.read_text()

    # Find the QuotesSeen impl block
    impl_match = re.search(r"impl QuotesSeen\b", src)
    assert impl_match, "Could not find 'impl QuotesSeen' in mod.rs"
    impl_start = impl_match.start()

    # We only care about code AFTER the in_regex handler, which processes
    # escapes inside an open regex (that handler is correct in any position).
    # The general escape handler is the one that also sets prev_non_ws_byte.
    # Find it by matching the full pattern (not the one inside in_regex).
    check_byte_src = src[impl_start:]

    # Find the call to slash_starts_regex() — this is the deferred-slash
    # resolution logic.
    slash_regex_pos = check_byte_src.find("slash_starts_regex()")
    assert slash_regex_pos != -1, (
        "Could not find 'slash_starts_regex()' in QuotesSeen impl"
    )

    # Find the general escape handler: the `if byte == b'\\'` that contains
    # `self.prev_non_ws_byte = Some(byte)`.  The in_regex handler does NOT
    # set prev_non_ws_byte, so this pattern uniquely identifies the general
    # handler.
    pattern = re.compile(
        r"if byte == b'\\\\'\s*\{[^}]*prev_non_ws_byte\s*=\s*Some\(byte\)",
        re.DOTALL,
    )
    escape_match = pattern.search(check_byte_src)
    assert escape_match, (
        "Could not find the general escape handler "
        "(if byte == b'\\\\' { ... prev_non_ws_byte = Some(byte) ... })"
    )

    assert escape_match.start() > slash_regex_pos, (
        f"General escape handler (pos {escape_match.start()}) must come "
        f"AFTER slash_starts_regex() (pos {slash_regex_pos}).  "
        "The escape handler appearing before deferred-slash resolution "
        "causes the deferred '/' to be lost, breaking regex detection."
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — regression
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_existing_quotes_seen_tests():
    """Existing QuotesSeen unit tests must still pass (no regressions)."""
    r = subprocess.run(
        ["cargo", "test", "-p", "biome_html_parser", "--lib", "--",
         "lexer::quotes_seen", "--nocapture"],
        cwd=REPO, capture_output=True, timeout=300,
    )
    output = r.stdout.decode() + r.stderr.decode()
    assert r.returncode == 0, (
        f"Existing quotes_seen tests failed:\n{output[-3000:]}"
    )
    # Verify at least the pre-existing tests ran (not 0 tests)
    assert "0 passed" not in output, (
        "Expected existing quotes_seen tests to run, but 0 passed"
    )


# [repo_tests] pass_to_pass - Repo CI: cargo check
def test_repo_cargo_check_html_parser():
    """Repo's cargo check -p biome_html_parser passes (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "check", "-p", "biome_html_parser"],
        cwd=REPO, capture_output=True, text=True, timeout=300,
    )
    assert r.returncode == 0, (
        f"cargo check failed:\n{r.stderr[-2000:]}"
    )


# [repo_tests] pass_to_pass - Repo CI: cargo clippy
def test_repo_cargo_clippy_html_parser():
    """Repo's cargo clippy -p biome_html_parser passes (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "clippy", "-p", "biome_html_parser", "--", "-D", "warnings"],
        cwd=REPO, capture_output=True, text=True, timeout=300,
    )
    assert r.returncode == 0, (
        f"cargo clippy failed:\n{r.stderr[-2000:]}"
    )


# [repo_tests] pass_to_pass - Repo CI: cargo test --lib
def test_repo_cargo_test_lib_html_parser():
    """Repo's cargo test -p biome_html_parser --lib passes (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "test", "-p", "biome_html_parser", "--lib"],
        cwd=REPO, capture_output=True, text=True, timeout=300,
    )
    assert r.returncode == 0, (
        f"cargo test --lib failed:\n{r.stderr[-2000:]}"
    )


# [repo_tests] pass_to_pass - Repo CI: cargo test spec tests
def test_repo_cargo_test_spec_tests_html_parser():
    """Repo's cargo test -p biome_html_parser --test spec_tests passes (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "test", "-p", "biome_html_parser", "--test", "spec_tests"],
        cwd=REPO, capture_output=True, text=True, timeout=300,
    )
    assert r.returncode == 0, (
        f"cargo test --test spec_tests failed:\n{r.stderr[-2000:]}"
    )
