"""
Test outputs for biomejs/biome#9735
Fix markdown parser panic on multi-byte characters in emphasis context
"""

import subprocess
import os
import sys

REPO = os.environ.get("REPO", "/workspace/biome_repo")

# Rust integration test exercising parse_markdown with multi-byte content.
# Two test functions: one verifies correct multi-line parsing, one verifies
# text preservation.  Uses Rust Unicode escapes throughout.
#
# The bug only manifests with MULTI-LINE blockquotes: the continuation line's
# quote prefix ("> ") is consumed but its byte length is not counted in the
# accumulated total, causing the resulting byte index to land inside a
# multi-byte character.
_RUST_REGRESSION_TEST = r"""
use biome_markdown_parser::parse_markdown;

#[test]
fn multibyte_multiline_blockquote_parses_correctly() {
    // Multi-line blockquotes where the continuation line's quote prefix
    // causes an accumulated byte-length mismatch.  Before the fix the
    // parser panicked with "byte index N is not a char boundary".
    let inputs: Vec<&str> = vec![
        // CJK on both lines -- the 2-byte quote prefix offset lands
        // inside a 3-byte CJK character
        ">\u{3053}\u{3093}\u{306b}\u{3061}\u{306f}\n> \u{4e16}\u{754c}\n",
        // Emoji + CJK first line, CJK continuation
        ">\u{1f4a1} \u{30c6}\u{30b9}\u{30c8}\n> \u{30c6}\u{30ad}\u{30b9}\u{30c8}\n",
        // CJK with inline link spanning two lines
        ">\u{65e5}\u{672c}\u{8a9e}[\u{30ea}\u{30f3}\u{30af}](https://example.com)\n> \u{7d9a}\u{304d}\n",
    ];
    for (i, input) in inputs.iter().enumerate() {
        let parsed = parse_markdown(input);
        let tree = format!("{:#?}", parsed.tree());
        // A correct parse tree for a blockquote with paragraph content is
        // non-trivial; a stub returning an empty tree would fail this.
        assert!(
            tree.len() > 100,
            "Input {i}: parse tree too small, likely empty or malformed: {}",
            &tree[..tree.len().min(200)]
        );
    }
}

#[test]
fn multibyte_text_preserved_through_parsing() {
    // Verify the full multi-byte source text survives a multi-line blockquote
    // parse by inspecting the concrete syntax tree (CST) debug output.
    let input = ">\u{1f4a1} \u{30c6}\u{30b9}\u{30c8}\n> \u{30c6}\u{30ad}\u{30b9}\u{30c8}\n";
    let parsed = parse_markdown(input);
    let cst = format!("{:#?}", parsed.syntax());

    assert!(cst.contains("\u{1f4a1}"), "Emoji character lost during parsing");
    assert!(cst.contains("\u{30c6}\u{30b9}\u{30c8}"), "CJK characters from first line lost");
    assert!(cst.contains("\u{30c6}\u{30ad}\u{30b9}\u{30c8}"), "CJK characters from continuation line lost");
}
"""

# Module-level cache so both f2p tests share a single cargo compilation.
_regression_result = {}


def _run_rust_regression():
    """Write a temp Rust integration test, compile & run it, cache the result."""
    if "rc" not in _regression_result:
        test_path = os.path.join(
            REPO,
            "crates/biome_markdown_parser/tests/_multibyte_regression.rs",
        )
        try:
            with open(test_path, "w", encoding="utf-8") as f:
                f.write(_RUST_REGRESSION_TEST)
            result = subprocess.run(
                [
                    "cargo", "test", "-p", "biome_markdown_parser",
                    "--test", "_multibyte_regression",
                ],
                capture_output=True,
                text=True,
                timeout=300,
                cwd=REPO,
            )
            _regression_result["rc"] = result.returncode
            _regression_result["output"] = result.stdout + "\n" + result.stderr
        finally:
            if os.path.exists(test_path):
                os.remove(test_path)
    return _regression_result["rc"], _regression_result["output"]


# -- pass-to-pass tests -------------------------------------------------------


def test_cargo_check():
    """Test that the code compiles without errors (pass_to_pass)."""
    result = subprocess.run(
        ["cargo", "check", "-p", "biome_markdown_parser"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert result.returncode == 0, (
        f"Cargo check failed:\n{result.stderr[-1000:]}"
    )


def test_markdown_parser_tests_pass():
    """Test that the markdown parser tests pass (pass_to_pass)."""
    result = subprocess.run(
        ["cargo", "test", "-p", "biome_markdown_parser", "--", "spec_test"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert result.returncode == 0, (
        f"Markdown parser tests failed:\n{result.stderr[-1000:]}"
    )


def test_markdown_formatter_check():
    """Test that markdown formatter compiles without errors (pass_to_pass)."""
    result = subprocess.run(
        ["cargo", "check", "-p", "biome_markdown_formatter"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert result.returncode == 0, (
        f"Cargo check for formatter failed:\n{result.stderr[-1000:]}"
    )


def test_cargo_fmt():
    """Test that all Rust files are formatted correctly (pass_to_pass)."""
    result = subprocess.run(
        ["cargo", "fmt", "--all", "--", "--check"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert result.returncode == 0, (
        f"Format check failed:\n{result.stderr[-1000:]}"
    )


def test_cargo_clippy_markdown_parser():
    """Test that clippy passes on the markdown parser crate (pass_to_pass)."""
    result = subprocess.run(
        ["cargo", "clippy", "--package", "biome_markdown_parser", "--", "-D", "warnings"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert result.returncode == 0, (
        f"Clippy failed:\n{result.stderr[-1000:]}"
    )


# -- fail-to-pass tests -------------------------------------------------------


def test_multibyte_blockquote_parsing():
    """Test that parsing blockquotes with multi-byte chars produces correct AST (fail_to_pass).

    The bug caused parse_markdown to panic when computing inline source
    lengths for multi-byte characters in blockquote context.  This test
    writes a Rust integration test that calls parse_markdown with several
    multi-byte blockquote inputs and asserts the resulting parse trees are
    non-trivial (not empty or stub-like).
    """
    rc, output = _run_rust_regression()
    assert rc == 0, (
        f"Multi-byte blockquote parsing failed (parser likely panicked):\n"
        f"{output[-2000:]}"
    )


def test_multibyte_content_preservation():
    """Test that multi-byte text survives parsing intact (fail_to_pass).

    After parsing, every multi-byte character from the input must appear
    in the concrete syntax tree.  A buggy source-span computation would
    produce invalid byte boundaries and lose or corrupt multi-byte text.
    """
    rc, output = _run_rust_regression()
    assert rc == 0, (
        f"Multi-byte content preservation test failed:\n"
        f"{output[-2000:]}"
    )


if __name__ == "__main__":
    tests = [
        test_cargo_check,
        test_markdown_parser_tests_pass,
        test_markdown_formatter_check,
        test_cargo_fmt,
        test_cargo_clippy_markdown_parser,
        test_multibyte_blockquote_parsing,
        test_multibyte_content_preservation,
    ]

    failed = []
    for test in tests:
        try:
            print(f"Running {test.__name__}...", end=" ", flush=True)
            test()
            print("PASSED")
        except AssertionError as e:
            print(f"FAILED: {e}")
            failed.append(test.__name__)
        except Exception as e:
            print(f"ERROR: {e}")
            failed.append(test.__name__)

    if failed:
        print(f"\n{len(failed)} tests failed:")
        for name in failed:
            print(f"  - {name}")
        sys.exit(1)
    else:
        print("\nAll tests passed!")
        sys.exit(0)
