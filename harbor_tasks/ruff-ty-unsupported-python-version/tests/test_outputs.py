"""
Task: ruff-ty-unsupported-python-version
Repo: ruff @ 62a863cf518086135dfd2321c92fbc3823f95de8
PR:   24402

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import os
import subprocess
from pathlib import Path

REPO = "/workspace/ruff"
OPTIONS_RS = Path(REPO) / "crates/ty_project/src/metadata/options.rs"

# Rust test code injected into options.rs for behavioral deserialization checks.
# Exercises the python-version validation at the serde layer.
_HARNESS_TEST_MODULE = '''
#[cfg(test)]
mod harness_tests {
    use super::*;
    use crate::metadata::value::ValueSource;

    #[test]
    fn harness_rejects_unsupported_27() {
        let toml_str = "[environment]\\npython-version = \\"2.7\\"\\n";
        let result = Options::from_toml_str(toml_str, ValueSource::File(std::sync::Arc::new(ruff_db::system::SystemPathBuf::from("test.toml"))));
        assert!(
            result.is_err(),
            "Should reject Python 2.7 as unsupported, but deserialization succeeded"
        );
    }

    #[test]
    fn harness_rejects_unsupported_36() {
        let toml_str = "[environment]\\npython-version = \\"3.6\\"\\n";
        let result = Options::from_toml_str(toml_str, ValueSource::File(std::sync::Arc::new(ruff_db::system::SystemPathBuf::from("test.toml"))));
        assert!(
            result.is_err(),
            "Should reject Python 3.6 as unsupported, but deserialization succeeded"
        );
    }

    #[test]
    fn harness_accepts_supported_312() {
        let toml_str = "[environment]\\npython-version = \\"3.12\\"\\n";
        let result = Options::from_toml_str(toml_str, ValueSource::File(std::sync::Arc::new(ruff_db::system::SystemPathBuf::from("test.toml"))));
        assert!(
            result.is_ok(),
            "Should accept Python 3.12: {:?}",
            result.err()
        );
    }

    #[test]
    fn harness_accepts_supported_313() {
        let toml_str = "[environment]\\npython-version = \\"3.13\\"\\n";
        let result = Options::from_toml_str(toml_str, ValueSource::File(std::sync::Arc::new(ruff_db::system::SystemPathBuf::from("test.toml"))));
        assert!(
            result.is_ok(),
            "Should accept Python 3.13: {:?}",
            result.err()
        );
    }
}
'''


def _ensure_harness_injected():
    """Inject Rust test module into options.rs if not already present."""
    content = OPTIONS_RS.read_text()
    if "harness_rejects_unsupported_27" in content:
        return
    content += _HARNESS_TEST_MODULE
    OPTIONS_RS.write_text(content)


def _cargo_test(test_filter: str, timeout: int = 300) -> subprocess.CompletedProcess:
    """Run a specific cargo test in ty_project."""
    return subprocess.run(
        ["cargo", "test", "-p", "ty_project", "--lib", test_filter],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=timeout,
        env={**os.environ, "CARGO_PROFILE_DEV_OPT_LEVEL": "1"},
    )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) -- compilation check
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_compiles():
    """Modified ty_project crate compiles successfully."""
    r = subprocess.run(
        ["cargo", "check", "-p", "ty_project"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        env={**os.environ, "CARGO_PROFILE_DEV_OPT_LEVEL": "1"},
    )
    assert r.returncode == 0, f"Compilation failed:\n{r.stderr}"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) -- repo's own CI checks
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_check():
    """Repo's cargo check on ty_project passes (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "check", "-p", "ty_project"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
        env={**os.environ, "CARGO_PROFILE_DEV_OPT_LEVEL": "1"},
    )
    assert r.returncode == 0, f"Cargo check failed:\n{r.stderr[-1000:]}"


# [repo_tests] pass_to_pass
def test_repo_clippy():
    """Repo's cargo clippy on ty_project passes (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "clippy", "-p", "ty_project", "--", "-D", "warnings"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
        env={**os.environ, "CARGO_PROFILE_DEV_OPT_LEVEL": "1"},
    )
    assert r.returncode == 0, f"Clippy failed:\n{r.stderr[-1000:]}"


# [repo_tests] pass_to_pass
def test_repo_fmt():
    """Repo's rustfmt on ty_project passes (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "fmt", "-p", "ty_project", "--", "--check"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"Rustfmt check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_unit_tests():
    """Repo's unit tests for ty_project crate pass (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "test", "-p", "ty_project", "--lib"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        env={**os.environ, "CARGO_PROFILE_DEV_OPT_LEVEL": "1"},
    )
    assert r.returncode == 0, f"Unit tests failed:\n{r.stderr[-1000:]}\n{r.stdout[-1000:]}"


# [repo_tests] pass_to_pass
def test_repo_doc():
    """Repo's documentation for ty_project crate builds without warnings (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "doc", "--no-deps", "-p", "ty_project"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
        env={**os.environ, "RUSTDOCFLAGS": "-D warnings"},
    )
    assert r.returncode == 0, f"Documentation build failed:\n{r.stderr[-1000:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) -- core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_rejects_unsupported_python_27():
    """Deserializing python-version='2.7' in config must fail."""
    _ensure_harness_injected()
    r = _cargo_test("harness_tests::harness_rejects_unsupported_27")
    assert r.returncode == 0, (
        f"Test failed -- deserialization should reject Python 2.7:\n"
        f"{r.stdout[-2000:]}\n{r.stderr[-2000:]}"
    )


# [pr_diff] fail_to_pass
def test_rejects_unsupported_python_36():
    """Deserializing python-version='3.6' in config must fail."""
    _ensure_harness_injected()
    r = _cargo_test("harness_tests::harness_rejects_unsupported_36")
    assert r.returncode == 0, (
        f"Test failed -- deserialization should reject Python 3.6:\n"
        f"{r.stdout[-2000:]}\n{r.stderr[-2000:]}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) -- supported versions still work
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_accepts_supported_python_312():
    """Deserializing python-version='3.12' in config must succeed."""
    _ensure_harness_injected()
    r = _cargo_test("harness_tests::harness_accepts_supported_312")
    assert r.returncode == 0, (
        f"Test failed -- deserialization should accept Python 3.12:\n"
        f"{r.stdout[-2000:]}\n{r.stderr[-2000:]}"
    )


# [pr_diff] pass_to_pass
def test_accepts_supported_python_313():
    """Deserializing python-version='3.13' in config must succeed."""
    _ensure_harness_injected()
    r = _cargo_test("harness_tests::harness_accepts_supported_313")
    assert r.returncode == 0, (
        f"Test failed -- deserialization should accept Python 3.13:\n"
        f"{r.stdout[-2000:]}\n{r.stderr[-2000:]}"
    )