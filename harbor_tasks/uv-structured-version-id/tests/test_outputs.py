"""
Task: uv-structured-version-id
Repo: uv @ 5108919f039509703656f394cb647bc01dd09766
PR:   18840

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/uv"
ID_RS = Path(REPO) / "crates/uv-distribution-types/src/id.rs"

# Rust test module injected into id.rs to test VersionId behavior.
# Uses a distinct module name to coexist with any tests the patch may add.
BENCHMARK_RUST_TESTS = r'''
#[cfg(test)]
mod benchmark_tests {
    use super::VersionId;
    use uv_redacted::DisplaySafeUrl;

    /// Archive URLs that differ only in hash algorithm/digest must be equal.
    #[test]
    fn bm_archive_urls_ignore_hash_fragments() {
        let urls = [
            "https://files.pythonhosted.org/packages/36/55/anyio-4.0.0-py3-none-any.whl#sha256=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            "https://files.pythonhosted.org/packages/36/55/anyio-4.0.0-py3-none-any.whl#sha512=bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
        ];
        let ids: Vec<_> = urls.iter().map(|u| VersionId::from_url(&DisplaySafeUrl::parse(u).unwrap())).collect();
        assert_eq!(ids[0], ids[1], "archive URLs with different hash fragments must be equal");
    }

    /// Archive URLs with same subdirectory but different hashes must be equal.
    #[test]
    fn bm_archive_subdirectory_ignore_hash() {
        let a = DisplaySafeUrl::parse(
            "https://example.com/proj-1.2.0.tar.gz#subdirectory=src&sha256=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
        ).unwrap();
        let b = DisplaySafeUrl::parse(
            "https://example.com/proj-1.2.0.tar.gz#sha512=bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb&subdirectory=src"
        ).unwrap();
        assert_eq!(
            VersionId::from_url(&a),
            VersionId::from_url(&b),
            "archive URLs with same subdirectory but different hashes must be equal"
        );
    }

    /// Archive URLs with different subdirectories must remain distinct.
    #[test]
    fn bm_archive_different_subdirectories_differ() {
        let a = DisplaySafeUrl::parse(
            "https://example.com/proj-1.0.0.tar.gz#subdirectory=pkg_a"
        ).unwrap();
        let b = DisplaySafeUrl::parse(
            "https://example.com/proj-1.0.0.tar.gz#subdirectory=pkg_b"
        ).unwrap();
        assert_ne!(
            VersionId::from_url(&a),
            VersionId::from_url(&b),
            "archive URLs with different subdirectories must be distinct"
        );
    }

    /// Git URLs with irrelevant fragments (egg=) should be equal when subdirectory matches.
    #[test]
    fn bm_git_urls_ignore_irrelevant_fragments() {
        let a = DisplaySafeUrl::parse(
            "git+https://github.com/example/pkg.git@v1.0.0#egg=pkg&subdirectory=src"
        ).unwrap();
        let b = DisplaySafeUrl::parse(
            "git+https://github.com/example/pkg.git@v1.0.0#subdirectory=src"
        ).unwrap();
        assert_eq!(
            VersionId::from_url(&a),
            VersionId::from_url(&b),
            "git URLs with same subdirectory but different irrelevant fragments must be equal"
        );
    }
}
'''


def _run_cargo_benchmark_tests():
    """Inject benchmark Rust tests into id.rs and run them via cargo test."""
    original = ID_RS.read_text()
    modified = original
    if "mod benchmark_tests" not in original:
        modified = original + "\n" + BENCHMARK_RUST_TESTS
        ID_RS.write_text(modified)
    try:
        r = subprocess.run(
            ["cargo", "test", "-p", "uv-distribution-types", "--",
             "benchmark_tests::bm_"],
            cwd=REPO, capture_output=True, timeout=600,
        )
        output = r.stdout.decode() + "\n" + r.stderr.decode()
        return output, r.returncode
    finally:
        # Restore original content so subsequent cargo commands see the real source
        ID_RS.write_text(original)


# Run injected Rust tests once at import time; individual test_ functions inspect results.
_cargo_output, _cargo_rc = _run_cargo_benchmark_tests()


def _rust_test_passed(short_name: str) -> bool:
    """Check whether a specific benchmark Rust test passed."""
    return f"benchmark_tests::{short_name} ... ok" in _cargo_output


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — compilation
# ---------------------------------------------------------------------------

def test_cargo_check():
    """uv-distribution-types crate must compile without errors."""
    r = subprocess.run(
        ["cargo", "check", "-p", "uv-distribution-types"],
        cwd=REPO, capture_output=True, timeout=600,
    )
    assert r.returncode == 0, (
        f"cargo check failed:\n{r.stderr.decode()[-2000:]}"
    )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, repo_tests) — repo's own CI/CD checks
# ---------------------------------------------------------------------------

def test_cargo_fmt_check():
    """Code formatting passes cargo fmt check (pass_to_pass)."""
    # rustfmt is required for cargo fmt
    subprocess.run(
        ["rustup", "component", "add", "rustfmt"],
        cwd=REPO, capture_output=True, timeout=60,
    )
    r = subprocess.run(
        ["cargo", "fmt", "-p", "uv-distribution-types", "--check"],
        cwd=REPO, capture_output=True, timeout=120,
    )
    assert r.returncode == 0, (
        f"Format check failed:\n{r.stderr.decode()[-2000:]}"
    )


def test_cargo_check_crate():
    """uv-distribution-types crate compiles without errors (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "check", "-p", "uv-distribution-types", "--lib"],
        cwd=REPO, capture_output=True, timeout=120,
    )
    assert r.returncode == 0, (
        f"Crate cargo check failed:\n{r.stderr.decode()[-2000:]}"
    )


def test_cargo_clippy_crate():
    """uv-distribution-types crate passes clippy lints (pass_to_pass)."""
    # Ensure clippy is installed
    subprocess.run(
        ["rustup", "component", "add", "clippy"],
        cwd=REPO, capture_output=True, timeout=60,
    )
    r = subprocess.run(
        ["cargo", "clippy", "-p", "uv-distribution-types", "--lib"],
        cwd=REPO, capture_output=True, timeout=120,
    )
    assert r.returncode == 0, (
        f"Clippy check failed:\n{r.stderr.decode()[-2000:]}"
    )


def test_cargo_test_crate():
    """Tests for uv-distribution-types crate pass (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "test", "-p", "uv-distribution-types", "--lib"],
        cwd=REPO, capture_output=True, timeout=120,
    )
    assert r.returncode == 0, (
        f"Crate tests failed:\n{r.stderr.decode()[-2000:]}"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests via injected Rust tests
# ---------------------------------------------------------------------------

def test_archive_urls_ignore_hash_fragments():
    """Two archive URLs differing only in hash digest must produce equal VersionIds."""
    assert _rust_test_passed("bm_archive_urls_ignore_hash_fragments"), (
        f"Rust test failed.\n{_cargo_output[-3000:]}"
    )


def test_archive_urls_with_subdirectory_ignore_hash():
    """Archive URLs sharing a subdirectory but with different hashes must be equal."""
    assert _rust_test_passed("bm_archive_subdirectory_ignore_hash"), (
        f"Rust test failed.\n{_cargo_output[-3000:]}"
    )


def test_archive_urls_different_subdirectories_differ():
    """Archive URLs with different subdirectories must produce different VersionIds."""
    assert _rust_test_passed("bm_archive_different_subdirectories_differ"), (
        f"Rust test failed.\n{_cargo_output[-3000:]}"
    )


def test_git_urls_ignore_irrelevant_fragments():
    """Git URLs with/without irrelevant fragments (egg=) must be equal when subdirectory matches."""
    assert _rust_test_passed("bm_git_urls_ignore_irrelevant_fragments"), (
        f"Rust test failed.\n{_cargo_output[-3000:]}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (agent_config) — AGENTS.md line 7
# ---------------------------------------------------------------------------

def test_no_unwrap_in_production_code():
    """AGENTS.md: AVOID .unwrap() in production code of id.rs (use .expect() instead)."""
    content = ID_RS.read_text()
    # Split at #[cfg(test)] to isolate production code from test modules
    production_code = re.split(r"#\[cfg\(test\)\]", content)[0]
    unwraps = [
        (i + 1, line)
        for i, line in enumerate(production_code.splitlines())
        if ".unwrap()" in line and not line.strip().startswith("//")
    ]
    assert len(unwraps) == 0, (
        f"Found .unwrap() in production code of id.rs (use .expect() instead):\n"
        + "\n".join(f"  line {n}: {l.strip()}" for n, l in unwraps)
    )
