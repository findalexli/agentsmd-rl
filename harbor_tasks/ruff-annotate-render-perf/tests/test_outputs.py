"""
Task: ruff-annotate-render-perf
Repo: astral-sh/ruff @ e7f1c536715d8a44aa830c1e4947e2ffcca06e0e
PR:   24146

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
import textwrap
from pathlib import Path

import pytest

REPO = Path("/repo")
DL_FILE = REPO / "crates/ruff_annotate_snippets/src/renderer/display_list.rs"
SB_FILE = REPO / "crates/ruff_annotate_snippets/src/renderer/styled_buffer.rs"

RUST_TESTS = textwrap.dedent("""\

#[cfg(test)]
mod _harbor_cow_optimization_tests {
    use super::*;
    use std::borrow::Cow;

    #[test]
    fn plain_ascii_avoids_allocation() {
        for input in &[
            "hello world 123 normal line of code",
            "fn main() { println!(\"test\"); }",
            "!@#$%^&*()_+-=[]{}|;':\",./<>?",
            "    let x = 42; // indented with spaces",
        ] {
            let result = normalize_whitespace(input);
            assert!(
                matches!(result, Cow::Borrowed(_)),
                "plain ASCII '{}' should return Cow::Borrowed", input
            );
            assert_eq!(&*result, *input);
        }
    }

    #[test]
    fn tab_replacement_produces_correct_output() {
        let cases: &[(&str, &[&str])] = &[
            ("before\\tafter", &["before", "after"]),
            ("a\\tb\\tc", &["a", "b", "c"]),
            ("\\t", &[]),
            ("no_tab_prefix\\there", &["no_tab_prefix", "here"]),
        ];
        for (input, expected_fragments) in cases {
            let result = normalize_whitespace(input);
            assert!(
                matches!(result, Cow::Owned(_)),
                "input with tab '{}' should return Cow::Owned", input
            );
            assert!(!result.contains('\\t'), "tab should be replaced in '{}'", input);
            for frag in *expected_fragments {
                assert!(result.contains(frag), "'{}' should contain '{}'", result, frag);
            }
        }
    }

    #[test]
    fn complex_clean_string_avoids_allocation() {
        for input in &[
            "def foo(x: int, y: str = 'hello') -> None:  # comment with $pecial chars!",
            "    let mut buffer = Vec::with_capacity(1024); // pre-allocate",
            "import os; import sys; print(os.path.join('/a', 'b'))",
        ] {
            let result = normalize_whitespace(input);
            assert!(
                matches!(result, Cow::Borrowed(_)),
                "clean string '{}' should return Cow::Borrowed", input
            );
            assert_eq!(&*result, *input);
        }
    }

    #[test]
    fn empty_string_avoids_allocation() {
        let result = normalize_whitespace("");
        assert!(
            matches!(result, Cow::Borrowed(_)),
            "empty string should return Cow::Borrowed"
        );
        assert_eq!(&*result, "");
    }

    #[test]
    fn unicode_control_chars_replaced() {
        let cases: &[(&str, char)] = &[
            ("hello\\u{202a}world", '\\u{202a}'),   // LRE
            ("foo\\u{202b}bar", '\\u{202b}'),         // RLE
            ("x\\u{200d}y", '\\u{200d}'),             // ZWJ
            ("a\\u{2066}b", '\\u{2066}'),             // LRI
            ("m\\u{202c}n", '\\u{202c}'),             // PDF
        ];
        for (input, bad_char) in cases {
            let result = normalize_whitespace(input);
            assert!(
                matches!(result, Cow::Owned(_)),
                "input with control char should return Cow::Owned for '{}'", input
            );
            assert!(
                !result.contains(*bad_char),
                "control char {:?} should be removed", bad_char
            );
        }
    }
}
""")


@pytest.fixture(scope="session", autouse=True)
def inject_rust_tests():
    """Inject Rust test module into display_list.rs for Cow optimization tests."""
    original = DL_FILE.read_text()
    DL_FILE.write_text(original + RUST_TESTS)
    subprocess.run(
        ["cargo", "test", "-p", "ruff_annotate_snippets", "--no-run"],
        cwd=REPO, capture_output=True, timeout=300,
    )
    yield
    DL_FILE.write_text(original)


@pytest.fixture(scope="session")
def cow_test_results(inject_rust_tests):
    """Run all Cow optimization Rust tests in a single cargo invocation."""
    return subprocess.run(
        ["cargo", "test", "-p", "ruff_annotate_snippets", "--",
         "_harbor_cow_optimization_tests"],
        cwd=REPO, capture_output=True, text=True, timeout=120,
    )


def _assert_rust_test_passed(results: subprocess.CompletedProcess, test_name: str):
    """Assert a specific Rust test passed in the batch results."""
    combined = results.stdout + results.stderr
    if f"{test_name} ... ok" in combined:
        return
    assert False, (
        f"Rust test '{test_name}' did not pass.\n"
        f"stdout:\n{results.stdout}\nstderr:\n{results.stderr}"
    )


# ---------------------------------------------------------------------------
# Gate (pass_to_pass, static) -- crate must compile
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_crate_compiles():
    """The ruff_annotate_snippets crate must compile without errors."""
    r = subprocess.run(
        ["cargo", "check", "-p", "ruff_annotate_snippets"],
        cwd=REPO, capture_output=True, text=True, timeout=300,
    )
    assert r.returncode == 0, f"cargo check failed:\n{r.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) -- Cow optimization behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_plain_ascii_avoids_allocation(cow_test_results):
    """normalize_whitespace returns Cow::Borrowed for plain ASCII text."""
    _assert_rust_test_passed(cow_test_results, "plain_ascii_avoids_allocation")


# [pr_diff] fail_to_pass
def test_tab_replacement_correct(cow_test_results):
    """normalize_whitespace returns Cow::Owned with correct output for tab input."""
    _assert_rust_test_passed(cow_test_results, "tab_replacement_produces_correct_output")


# [pr_diff] fail_to_pass
def test_complex_clean_avoids_allocation(cow_test_results):
    """normalize_whitespace avoids allocation for complex strings without replacement chars."""
    _assert_rust_test_passed(cow_test_results, "complex_clean_string_avoids_allocation")


# [pr_diff] fail_to_pass
def test_empty_string_avoids_allocation(cow_test_results):
    """normalize_whitespace avoids allocation for empty string."""
    _assert_rust_test_passed(cow_test_results, "empty_string_avoids_allocation")


# [pr_diff] fail_to_pass
def test_unicode_control_chars_replaced(cow_test_results):
    """normalize_whitespace replaces Unicode control chars and returns Cow::Owned."""
    _assert_rust_test_passed(cow_test_results, "unicode_control_chars_replaced")


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) -- existing tests still pass
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_existing_crate_tests():
    """Existing ruff_annotate_snippets tests must not regress."""
    # Strip injected test module so upstream tests run cleanly
    content = DL_FILE.read_text()
    marker = "\n#[cfg(test)]\nmod _harbor_cow_optimization_tests {"
    if marker in content:
        clean = content[:content.index(marker)] + "\n"
        DL_FILE.write_text(clean)
    try:
        r = subprocess.run(
            ["cargo", "test", "-p", "ruff_annotate_snippets"],
            cwd=REPO, capture_output=True, text=True, timeout=300,
        )
        assert r.returncode == 0, f"Existing tests failed:\n{r.stdout}\n{r.stderr}"
    finally:
        DL_FILE.write_text(content)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) -- StyledBuffer optimizations
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_render_pre_allocates():
    """StyledBuffer::render pre-allocates string capacity instead of String::new()."""
    # AST-only because: pre-allocation is a performance optimization with no observable
    # behavioral change; only way to verify is checking the source for capacity hints
    content = SB_FILE.read_text()
    assert "with_capacity" in content or ".reserve" in content, (
        "render should pre-allocate string capacity (with_capacity or reserve)"
    )


# [pr_diff] fail_to_pass
def test_puts_avoids_per_char_putc():
    """StyledBuffer::puts does not delegate to per-character putc loop."""
    # AST-only because: internal dispatch change with identical external behavior;
    # no way to distinguish putc-loop vs batch-write from outside the function
    content = SB_FILE.read_text()
    lines = content.split("\n")
    in_puts = False
    brace_depth = 0
    puts_body = []
    for line in lines:
        if "fn puts(" in line:
            in_puts = True
            brace_depth = 0
        if in_puts:
            brace_depth += line.count("{") - line.count("}")
            puts_body.append(line)
            if brace_depth <= 0 and len(puts_body) > 1:
                break
    puts_text = "\n".join(puts_body)
    assert "self.putc" not in puts_text, (
        "puts should batch character writes instead of calling putc per character"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) -- AGENTS.md rules
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass -- AGENTS.md:76 @ e7f1c536
def test_no_local_imports():
    """Rust imports must be at file top, not locally in functions (AGENTS.md:76)."""
    for path in [DL_FILE, SB_FILE]:
        content = path.read_text()
        in_fn = False
        brace_depth = 0
        for line in content.splitlines():
            stripped = line.strip()
            if re.match(r"(pub(\(crate\))?\s+)?fn\s+\w+", stripped):
                in_fn = True
                brace_depth = 0
            if in_fn:
                brace_depth += stripped.count("{") - stripped.count("}")
                if brace_depth > 0 and re.match(r"use\s+", stripped):
                    pytest.fail(f"Local import found inside function in {path.name}")
                if brace_depth <= 0 and "{" in line:
                    in_fn = brace_depth > 0


# [agent_config] pass_to_pass -- AGENTS.md:79 @ e7f1c536
def test_no_new_unwrap_panic():
    """No new unwrap()/panic!()/unreachable!() in modified files (AGENTS.md:79)."""
    r = subprocess.run(
        ["git", "diff", "HEAD", "--", str(DL_FILE), str(SB_FILE)],
        cwd=REPO, capture_output=True, text=True, timeout=30,
    )
    new_lines = [l for l in r.stdout.splitlines()
                 if l.startswith("+") and not l.startswith("+++")]
    violations = [l for l in new_lines
                  if re.search(r"\b(unwrap\(\)|panic!\(|unreachable!\()", l)]
    assert len(violations) == 0, (
        f"New unwrap/panic/unreachable found:\n" + "\n".join(violations)
    )


# [agent_config] pass_to_pass -- AGENTS.md:81 @ e7f1c536
def test_prefer_expect_over_allow():
    """Use #[expect()] not #[allow()] for Clippy lint suppression (AGENTS.md:81)."""
    r = subprocess.run(
        ["git", "diff", "HEAD", "--", str(DL_FILE), str(SB_FILE)],
        cwd=REPO, capture_output=True, text=True, timeout=30,
    )
    new_lines = [l for l in r.stdout.splitlines()
                 if l.startswith("+") and not l.startswith("+++")]
    allows = [l for l in new_lines if re.search(r"#\[allow\(clippy::", l)]
    assert len(allows) == 0, (
        f"Use #[expect()] instead of #[allow()] for Clippy lint suppression:\n"
        + "\n".join(allows)
    )
