"""
Task: ruff-ipython-percent-foo-parsing
Repo: astral-sh/ruff @ 9d2b16029a6a141b2d15e966a69faa4c2ec41572
PR:   24152

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import os
import subprocess
from pathlib import Path

REPO = "/workspace/ruff"
BASE_COMMIT = "9d2b16029a6a141b2d15e966a69faa4c2ec41572"
CARGO_TIMEOUT = 300
LEXER_PATH = "crates/ruff_python_parser/src/lexer.rs"

# Rust integration test that verifies parsing behavior directly.
# We write a small test crate that imports ruff_python_parser's public API,
# then run individual tests via cargo test --test verify_fix.
_VERIFY_TEST_RS = r'''
use ruff_python_parser::{parse, Mode, ParseOptions};

#[test]
fn verify_magic_question_in_assignment() {
    for (input, expected_value) in [
        ("bar = %foo?", r#"value: "foo?""#),
        ("x = %timeit?", r#"value: "timeit?""#),
        ("y = %who?", r#"value: "who?""#),
    ] {
        let parsed = parse(input, ParseOptions::from(Mode::Ipython)).unwrap();
        let debug = format!("{:#?}", parsed.syntax());
        assert!(
            debug.contains(expected_value),
            "For `{input}`, expected {expected_value} in assignment but got:\n{debug}"
        );
    }
}

#[test]
fn verify_shell_question_in_assignment() {
    for (input, expected_value) in [
        ("baz = !pwd?", r#"value: "pwd?""#),
        ("v = !ls?", r#"value: "ls?""#),
    ] {
        let parsed = parse(input, ParseOptions::from(Mode::Ipython)).unwrap();
        let debug = format!("{:#?}", parsed.syntax());
        assert!(
            debug.contains(expected_value),
            "For `{input}`, expected {expected_value} in assignment but got:\n{debug}"
        );
    }
}

#[test]
fn verify_standalone_magic_help_still_works() {
    for (input, bad_value) in [
        ("%foo?", r#"value: "foo?""#),
        ("%timeit?", r#"value: "timeit?""#),
        ("%who?", r#"value: "who?""#),
    ] {
        let parsed = parse(input, ParseOptions::from(Mode::Ipython)).unwrap();
        let debug = format!("{:#?}", parsed.syntax());
        assert!(
            !debug.contains(bad_value),
            "Standalone `{input}` should NOT have {bad_value} — ? should be help-end token:\n{debug}"
        );
    }
}

#[test]
fn verify_multiple_assignments_with_question() {
    let parsed = parse(
        "a = %timeit?\nb = !ls?\nc = %who?",
        ParseOptions::from(Mode::Ipython),
    ).unwrap();
    let debug = format!("{:#?}", parsed.syntax());
    assert!(
        debug.contains(r#"value: "timeit?""#),
        "Expected 'timeit?' in assignment:\n{debug}"
    );
    assert!(
        debug.contains(r#"value: "ls?""#),
        "Expected 'ls?' in assignment:\n{debug}"
    );
    assert!(
        debug.contains(r#"value: "who?""#),
        "Expected 'who?' in assignment:\n{debug}"
    );
}
'''

_VERIFY_TEST_PATH = Path(REPO) / "crates/ruff_python_parser/tests/verify_fix.rs"

_compiled = False


def _ensure_compiled():
    """Write the Rust test file and compile it once."""
    global _compiled
    if _compiled:
        return
    _VERIFY_TEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    _VERIFY_TEST_PATH.write_text(_VERIFY_TEST_RS)
    r = subprocess.run(
        ["cargo", "test", "-p", "ruff_python_parser", "--test", "verify_fix",
         "--no-run"],
        cwd=REPO,
        capture_output=True,
        timeout=CARGO_TIMEOUT,
    )
    if r.returncode != 0:
        raise RuntimeError(
            f"Failed to compile verify_fix tests:\n{r.stderr.decode()[-2000:]}"
        )
    _compiled = True


def _run_verify_test(name: str) -> str:
    """Run a single named Rust test from verify_fix. Returns output on failure."""
    _ensure_compiled()
    r = subprocess.run(
        ["cargo", "test", "-p", "ruff_python_parser", "--test", "verify_fix",
         name, "--", "--nocapture"],
        cwd=REPO,
        capture_output=True,
        timeout=CARGO_TIMEOUT,
    )
    out = r.stdout.decode() + r.stderr.decode()
    assert r.returncode == 0, f"{name} failed:\n{out[-3000:]}"
    return out


def _get_added_lines(file_path: str) -> list[str]:
    """Get lines added to file_path relative to BASE_COMMIT (raw, with leading whitespace)."""
    r = subprocess.run(
        ["git", "diff", BASE_COMMIT, "--", file_path],
        cwd=REPO, capture_output=True, timeout=30,
    )
    return [
        ln[1:] for ln in r.stdout.decode().splitlines()
        if ln.startswith('+') and not ln.startswith('+++')
    ]


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — compilation check
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_compilation():
    """ruff_python_parser crate must compile without errors."""
    r = subprocess.run(
        ["cargo", "check", "-p", "ruff_python_parser"],
        cwd=REPO,
        capture_output=True,
        timeout=CARGO_TIMEOUT,
    )
    assert r.returncode == 0, f"Compilation failed:\n{r.stderr.decode()[-2000:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_magic_question_in_assignment():
    """bar = %foo? must parse %foo? as magic command with value 'foo?' (? not split off)."""
    _run_verify_test("verify_magic_question_in_assignment")


# [pr_diff] fail_to_pass
def test_shell_question_in_assignment():
    """baz = !pwd? must parse !pwd? as shell command with value 'pwd?' (? not split off)."""
    _run_verify_test("verify_shell_question_in_assignment")


# [pr_diff] fail_to_pass
def test_multiple_assignments_with_question():
    """Multiple assignment magics with ? (%timeit?, !ls?, %who?) all parse with ? in value."""
    _run_verify_test("verify_multiple_assignments_with_question")


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / repo_tests) — regression
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_standalone_magic_help_preserved():
    """Standalone %foo? (not in assignment) still uses help-end semantics."""
    _run_verify_test("verify_standalone_magic_help_still_works")


# [repo_tests] pass_to_pass
def test_lexer_no_regression():
    """All existing lexer tests still pass (no regressions introduced)."""
    env = {**os.environ, "INSTA_FORCE_PASS": "1", "INSTA_UPDATE": "always"}
    r = subprocess.run(
        ["cargo", "test", "-p", "ruff_python_parser", "--lib", "lexer::tests"],
        cwd=REPO,
        capture_output=True,
        timeout=CARGO_TIMEOUT,
        env=env,
    )
    out = r.stdout.decode() + r.stderr.decode()
    assert r.returncode == 0, f"Lexer test regression:\n{out[-2000:]}"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:79 @ 9d2b16029a6a141b2d15e966a69faa4c2ec41572
def test_no_panic_unreachable_in_new_code():
    """New code must not introduce panic!/unreachable! macros (AGENTS.md:79)."""
    for line in _get_added_lines(LEXER_PATH):
        stripped = line.strip()
        if stripped.startswith('//'):
            continue
        assert 'panic!' not in stripped, f"panic! found in new code: {stripped}"
        assert 'unreachable!' not in stripped, (
            f"unreachable! found in new code: {stripped}"
        )


# [agent_config] pass_to_pass — AGENTS.md:76 @ 9d2b16029a6a141b2d15e966a69faa4c2ec41572
def test_no_local_use_imports():
    """Rust imports must be at top of file, not local in functions (AGENTS.md:76)."""
    for line in _get_added_lines(LEXER_PATH):
        stripped = line.strip()
        if stripped.startswith('use ') and line != stripped:
            assert False, f"Local 'use' import found in new code: {stripped}"


# [agent_config] pass_to_pass — AGENTS.md:81 @ 9d2b16029a6a141b2d15e966a69faa4c2ec41572
def test_no_allow_attributes():
    """Clippy lint suppression must use #[expect()] not #[allow()] (AGENTS.md:81)."""
    for line in _get_added_lines(LEXER_PATH):
        stripped = line.strip()
        if stripped.startswith('//'):
            continue
        assert '#[allow(' not in stripped, (
            f"Use #[expect()] instead of #[allow()] per AGENTS.md:81: {stripped}"
        )
