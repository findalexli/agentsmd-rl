"""
Task: biome-markdown-link-ref-trailing-text
Repo: biome @ aafca2d086eb24226a9cf1a69179561f70d02773
PR:   9780

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/biome"

CHECKER_SRC = """\
fn main() {
    let args: Vec<String> = std::env::args().collect();
    let input = &args[1];
    let parsed = biome_markdown_parser::parse_markdown(input);
    let output = format!("{:#?}", parsed.syntax());
    if output.contains("MD_LINK_REFERENCE_DEFINITION") {
        println!("LINK_REF_DEF");
    } else {
        println!("NOT_LINK_REF_DEF");
    }
}
"""


def _ensure_checker():
    """Write the checker example if it was removed or doesn't exist."""
    example_dir = Path(REPO) / "crates/biome_markdown_parser/examples"
    example_dir.mkdir(exist_ok=True)
    checker = example_dir / "check_link_ref.rs"
    if not checker.exists() or checker.read_text() != CHECKER_SRC:
        checker.write_text(CHECKER_SRC)


def _run_checker(input_text):
    """Run the checker example and return its stdout line."""
    r = subprocess.run(
        ["cargo", "run", "--example", "check_link_ref",
         "-p", "biome_markdown_parser", "--", input_text],
        cwd=REPO, capture_output=True, text=True, timeout=300
    )
    assert r.returncode == 0, f"Checker crashed on input '{input_text}':\n{r.stderr[-2000:]}"
    return r.stdout.strip()


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

def test_syntax_check():
    """Modified files must compile without errors."""
    r = subprocess.run(
        ["cargo", "check", "-p", "biome_markdown_parser"],
        cwd=REPO, capture_output=True, text=True, timeout=300
    )
    assert r.returncode == 0, f"Compilation failed:\n{r.stderr[-2000:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

def test_reject_trailing_text():
    """Parser must not treat '[label]: /url invalid' as a link reference definition."""
    _ensure_checker()
    result = _run_checker("[label]: /url invalid")
    assert result == "NOT_LINK_REF_DEF", \
        f"Expected NOT_LINK_REF_DEF for '[label]: /url invalid', got: {result}"


def test_reject_varied_trailing():
    """Multiple inputs with non-title trailing text must all be rejected."""
    _ensure_checker()
    inputs = [
        "[a]: /url not-title",
        "[b]: /url some extra text",
        "[c]: http://example.com garbage",
    ]
    for inp in inputs:
        result = _run_checker(inp)
        assert result == "NOT_LINK_REF_DEF", \
            f"Expected NOT_LINK_REF_DEF for '{inp}', got: {result}"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression checks
# ---------------------------------------------------------------------------

def test_valid_defs_preserved():
    """Valid link reference definitions with proper titles must still parse."""
    _ensure_checker()
    valid_inputs = [
        '[d]: /url "title"',
        "[e]: /url 'title'",
        "[f]: /url (title)",
        "[g]: /url",
    ]
    for inp in valid_inputs:
        result = _run_checker(inp)
        assert result == "LINK_REF_DEF", \
            f"Expected LINK_REF_DEF for '{inp}', got: {result}"


def test_existing_tests_pass():
    """Upstream markdown parser test suite still passes."""
    r = subprocess.run(
        ["cargo", "test", "-p", "biome_markdown_parser"],
        cwd=REPO, capture_output=True, text=True, timeout=600
    )
    assert r.returncode == 0, \
        f"Upstream tests failed:\n{r.stdout[-3000:]}\n{r.stderr[-2000:]}"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) - Repo CI gates
# ---------------------------------------------------------------------------

def test_repo_clippy():
    """Repo's clippy linting passes (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "clippy", "-p", "biome_markdown_parser", "--", "-D", "warnings"],
        cwd=REPO, capture_output=True, text=True, timeout=300
    )
    assert r.returncode == 0, f"Clippy failed:\n{r.stderr[-2000:]}"


def test_repo_format():
    """Repo's code formatting passes (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "fmt", "--", "--check"],
        cwd=REPO, capture_output=True, text=True, timeout=300
    )
    assert r.returncode == 0, f"Format check failed:\n{r.stderr[-500:]}"
