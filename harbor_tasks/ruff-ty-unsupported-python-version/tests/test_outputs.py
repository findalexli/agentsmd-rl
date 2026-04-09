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
# These tests exercise the python-version validation at the serde layer.
_HARNESS_TEST_MODULE = '''
#[cfg(test)]
mod harness_tests {
    use super::*;

    #[test]
    fn harness_rejects_unsupported_27() {
        let toml_str = "[environment]\\npython-version = \\"2.7\\"\\n";
        let result: Result<Options, toml::de::Error> = toml::from_str(toml_str);
        assert!(
            result.is_err(),
            "Should reject Python 2.7 as unsupported, but deserialization succeeded"
        );
    }

    #[test]
    fn harness_rejects_unsupported_36() {
        let toml_str = "[environment]\\npython-version = \\"3.6\\"\\n";
        let result: Result<Options, toml::de::Error> = toml::from_str(toml_str);
        assert!(
            result.is_err(),
            "Should reject Python 3.6 as unsupported, but deserialization succeeded"
        );
    }

    #[test]
    fn harness_accepts_supported_312() {
        let toml_str = "[environment]\\npython-version = \\"3.12\\"\\n";
        let result: Result<Options, toml::de::Error> = toml::from_str(toml_str);
        assert!(
            result.is_ok(),
            "Should accept Python 3.12: {}",
            result.unwrap_err()
        );
    }

    #[test]
    fn harness_accepts_supported_313() {
        let toml_str = "[environment]\\npython-version = \\"3.13\\"\\n";
        let result: Result<Options, toml::de::Error> = toml::from_str(toml_str);
        assert!(
            result.is_ok(),
            "Should accept Python 3.13: {}",
            result.unwrap_err()
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
        ["cargo", "test", "-p", "ty_project", "--", test_filter, "--exact"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=timeout,
        env={**os.environ, "CARGO_PROFILE_DEV_OPT_LEVEL": "1"},
    )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — compilation check
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
# Pass-to-pass (repo_tests) — repo's own CI checks
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


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_rejects_unsupported_python_27():
    """Deserializing python-version='2.7' in config must fail."""
    _ensure_harness_injected()
    r = _cargo_test("harness_tests::harness_rejects_unsupported_27")
    assert r.returncode == 0, (
        f"Test failed — deserialization should reject Python 2.7:\n"
        f"{r.stdout[-2000:]}\n{r.stderr[-2000:]}"
    )


# [pr_diff] fail_to_pass
def test_rejects_unsupported_python_36():
    """Deserializing python-version='3.6' in config must fail."""
    _ensure_harness_injected()
    r = _cargo_test("harness_tests::harness_rejects_unsupported_36")
    assert r.returncode == 0, (
        f"Test failed — deserialization should reject Python 3.6:\n"
        f"{r.stdout[-2000:]}\n{r.stderr[-2000:]}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — supported versions still work
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_accepts_supported_python_312():
    """Deserializing python-version='3.12' in config must succeed."""
    _ensure_harness_injected()
    r = _cargo_test("harness_tests::harness_accepts_supported_312")
    assert r.returncode == 0, (
        f"Test failed — deserialization should accept Python 3.12:\n"
        f"{r.stdout[-2000:]}\n{r.stderr[-2000:]}"
    )


# [pr_diff] pass_to_pass
def test_accepts_supported_python_313():
    """Deserializing python-version='3.13' in config must succeed."""
    _ensure_harness_injected()
    r = _cargo_test("harness_tests::harness_accepts_supported_313")
    assert r.returncode == 0, (
        f"Test failed — deserialization should accept Python 3.13:\n"
        f"{r.stdout[-2000:]}\n{r.stderr[-2000:]}"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:79 @ 62a863cf518086135dfd2321c92fbc3823f95de8
def test_no_panic_unwrap_in_validation():
    """No panic!/unwrap() in the validation function (AGENTS.md:79)."""
    source = OPTIONS_RS.read_text()

    # Find any function that validates/deserializes python version
    # (the fix adds a function like deserialize_supported_python_version)
    in_validation_fn = False
    brace_depth = 0
    for line in source.splitlines():
        stripped = line.strip()
        if stripped.startswith("//"):
            continue

        # Detect the start of a function that deals with python version deserialization
        if ("fn " in stripped
                and "python_version" in stripped.lower()
                and "deserializ" in stripped.lower()):
            in_validation_fn = True
            brace_depth = 0

        if in_validation_fn:
            brace_depth += stripped.count("{") - stripped.count("}")
            assert "panic!(" not in stripped, (
                f"panic! found in validation function: {stripped}"
            )
            assert ".unwrap()" not in stripped, (
                f".unwrap() found in validation function: {stripped}"
            )
            assert "unreachable!(" not in stripped, (
                f"unreachable! found in validation function: {stripped}"
            )
            if brace_depth <= 0 and "{" in source[:source.find(stripped)]:
                in_validation_fn = False


# [agent_config] pass_to_pass — AGENTS.md:76 @ 62a863cf518086135dfd2321c92fbc3823f95de8
def test_imports_at_file_top():
    """Rust imports must be at the top of the file, not locally in functions (AGENTS.md:76)."""
    source = OPTIONS_RS.read_text()
    lines = source.splitlines()

    # Find all 'use ' statements and verify they appear before any 'fn ' or 'impl ' or 'struct '
    # (i.e., at the top-level, not inside function bodies)
    in_fn_body = False
    brace_depth = 0
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("//") or stripped.startswith("#["):
            continue

        # Track brace depth to detect function bodies
        if any(stripped.startswith(kw) for kw in ["fn ", "pub fn ", "pub(crate) fn "]):
            if "{" in stripped:
                in_fn_body = True
                brace_depth = stripped.count("{") - stripped.count("}")
            continue

        if in_fn_body:
            brace_depth += stripped.count("{") - stripped.count("}")
            # Check for local use statements inside function bodies
            if stripped.startswith("use "):
                assert False, (
                    f"Local import at line {i}: {stripped} — "
                    f"AGENTS.md requires imports at the top of the file"
                )
            if brace_depth <= 0:
                in_fn_body = False
