"""
Task: biome-markdown-nested-list-blank-lines
Repo: biome @ 716e4e195d6a76f02850f3cf41b8b38b757708ec
PR:   9764

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import os

REPO = "/workspace/biome"

# Rust integration test exercising the markdown parser's handling of
# nested lists with blank lines between items.
REGRESSION_TEST_RS = r'''use biome_markdown_parser::parse_markdown;

#[test]
fn double_blank_nested_list_no_errors() {
    // Two blank lines between nested siblings
    let input = "- top\n  - sub a\n\n\n  - sub b\n";
    let result = parse_markdown(input);
    assert!(
        !result.has_errors(),
        "Parser emitted false errors for nested list with double blank lines"
    );
}

#[test]
fn triple_blank_nested_list_no_errors() {
    // Three blank lines between nested siblings
    let input = "- top\n  - sub a\n\n\n\n  - sub b\n";
    let result = parse_markdown(input);
    assert!(
        !result.has_errors(),
        "Parser emitted false errors for nested list with triple blank lines"
    );
}

#[test]
fn deeper_nested_blank_lines_no_errors() {
    // Three-level nesting with double blank lines at the deepest level
    let input = "- top\n  - mid\n    - sub a\n\n\n    - sub b\n";
    let result = parse_markdown(input);
    assert!(
        !result.has_errors(),
        "Parser emitted false errors for deeper nested list with double blank lines"
    );
}

#[test]
fn single_blank_nested_list_ok() {
    // Single blank line between nested siblings (always worked)
    let input = "- top\n  - sub a\n\n  - sub b\n";
    let result = parse_markdown(input);
    assert!(
        !result.has_errors(),
        "Parser should handle single blank line between nested list items"
    );
}
'''


def _ensure_regression_test():
    """Write the Rust regression test file."""
    path = os.path.join(
        REPO, "crates/biome_markdown_parser/tests/harbor_regression_test.rs"
    )
    with open(path, "w") as f:
        f.write(REGRESSION_TEST_RS)


def _run_rust_test(name, timeout=300):
    """Run a single named Rust test from the regression test file."""
    _ensure_regression_test()
    return subprocess.run(
        [
            "cargo", "test", "-p", "biome_markdown_parser",
            "--test", "harbor_regression_test",
            "--", name, "--exact",
        ],
        cwd=REPO,
        capture_output=True,
        timeout=timeout,
    )


# ---------------------------------------------------------------------------
# pass_to_pass - compilation gate
# ---------------------------------------------------------------------------

def test_cargo_check():
    """The biome_markdown_parser crate compiles without errors."""
    r = subprocess.run(
        ["cargo", "check", "-p", "biome_markdown_parser"],
        cwd=REPO,
        capture_output=True,
        timeout=300,
    )
    assert r.returncode == 0, f"Compilation failed:\n{r.stderr.decode()[-2000:]}"


# ---------------------------------------------------------------------------
# pass_to_pass - repo CI/CD checks (enrichment)
# ---------------------------------------------------------------------------

def test_cargo_fmt_check():
    """Rust code formatting passes (cargo fmt --check) (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "fmt", "--all", "--", "--check"],
        cwd=REPO,
        capture_output=True,
        timeout=300,
    )
    assert r.returncode == 0, f"Format check failed:\n{r.stderr.decode()[-2000:]}"


def test_cargo_clippy():
    """Clippy lints pass for biome_markdown_parser crate (pass_to_pass)."""
    r = subprocess.run(
        [
            "cargo", "clippy", "-p", "biome_markdown_parser",
            "--all-features", "--all-targets", "--", "-D", "warnings",
        ],
        cwd=REPO,
        capture_output=True,
        timeout=300,
    )
    assert r.returncode == 0, f"Clippy failed:\n{r.stderr.decode()[-2000:]}"


def test_cargo_test_markdown_parser():
    """All tests in biome_markdown_parser crate pass (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "test", "-p", "biome_markdown_parser", "--no-fail-fast"],
        cwd=REPO,
        capture_output=True,
        timeout=600,
    )
    assert r.returncode == 0, f"Tests failed:\n{r.stderr.decode()[-2000:]}"


def test_cargo_test_markdown_parser_lib():
    """Library unit tests for biome_markdown_parser pass (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "test", "-p", "biome_markdown_parser", "--lib"],
        cwd=REPO,
        capture_output=True,
        timeout=300,
    )
    assert r.returncode == 0, f"Lib tests failed:\n{r.stderr.decode()[-2000:]}"


def test_cargo_test_markdown_parser_doc():
    """Doc tests for biome_markdown_parser pass (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "test", "-p", "biome_markdown_parser", "--doc"],
        cwd=REPO,
        capture_output=True,
        timeout=300,
    )
    assert r.returncode == 0, f"Doc tests failed:\n{r.stderr.decode()[-2000:]}"


# ---------------------------------------------------------------------------
# fail_to_pass - core behavioral tests
# ---------------------------------------------------------------------------

def test_double_blank_nested_list_no_errors():
    """Double blank lines between nested list siblings must not produce parser errors."""
    r = _run_rust_test("double_blank_nested_list_no_errors")
    assert r.returncode == 0, (
        f"Test failed:\n{r.stdout.decode()[-2000:]}\n{r.stderr.decode()[-2000:]}"
    )


def test_triple_blank_nested_list_no_errors():
    """Triple blank lines between nested list siblings must not produce parser errors."""
    r = _run_rust_test("triple_blank_nested_list_no_errors")
    assert r.returncode == 0, (
        f"Test failed:\n{r.stdout.decode()[-2000:]}\n{r.stderr.decode()[-2000:]}"
    )


def test_deeper_nested_blank_lines_no_errors():
    """Deeper nested lists (3 levels) with double blank lines must not produce parser errors."""
    r = _run_rust_test("deeper_nested_blank_lines_no_errors")
    assert r.returncode == 0, (
        f"Test failed:\n{r.stdout.decode()[-2000:]}\n{r.stderr.decode()[-2000:]}"
    )


# ---------------------------------------------------------------------------
# pass_to_pass - regression guard
# ---------------------------------------------------------------------------

def test_single_blank_nested_list_ok():
    """Single blank line between nested list items should parse correctly (always worked)."""
    r = _run_rust_test("single_blank_nested_list_ok")
    assert r.returncode == 0, (
        f"Test failed:\n{r.stdout.decode()[-2000:]}\n{r.stderr.decode()[-2000:]}"
    )
