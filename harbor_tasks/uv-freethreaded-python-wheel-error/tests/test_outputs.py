"""
Task: uv-freethreaded-python-wheel-error
Repo: astral-sh/uv @ 87da0ce43ac12fc50e28931f42b1164453f04790
PR:   #18740

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = Path("/repo")
ERROR_RS = REPO / "crates/uv-distribution/src/error.rs"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_compilation():
    """uv-distribution crate compiles without errors."""
    r = subprocess.run(
        ["cargo", "check", "-p", "uv-distribution"],
        cwd=REPO, capture_output=True, timeout=300,
    )
    assert r.returncode == 0, (
        f"Compilation failed:\n{r.stderr.decode()[-2000:]}"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# Injected Rust test that constructs the error using the OLD (u8, u8) API.
# On base: compiles fine (type is still (u8, u8)).
# On any correct fix: fails to compile (type changed).
_OLD_API_INJECT = """

#[cfg(test)]
mod harbor_old_api_check {
    use super::Error;
    use std::str::FromStr;
    use uv_distribution_filename::WheelFilename;
    use uv_platform_tags::{Arch, Os, Platform};

    #[test]
    fn harbor_old_tuple_api() {
        let _ = Error::BuiltWheelIncompatibleHostPlatform {
            filename: WheelFilename::from_str(
                "test-1.0-cp315-abi3t-macosx_11_0_arm64.whl",
            ).unwrap(),
            python_platform: Platform::new(
                Os::Macos { major: 11, minor: 0 },
                Arch::Aarch64,
            ),
            python_version: (3u8, 15u8),
        };
    }
}
"""


# [pr_diff] fail_to_pass
def test_old_tuple_api_rejected():
    """python_version type changed from (u8, u8) -- old API must not compile."""
    backup = ERROR_RS.read_text()
    try:
        ERROR_RS.write_text(backup + _OLD_API_INJECT)
        r = subprocess.run(
            ["cargo", "check", "--tests", "-p", "uv-distribution"],
            cwd=REPO, capture_output=True, timeout=300,
        )
        assert r.returncode != 0, (
            "Old (u8, u8) tuple API still compiles -- python_version type not changed"
        )
    finally:
        ERROR_RS.write_text(backup)


# Injected Rust tests for PythonVersion Display and full error messages.
# On base: PythonVersion doesn't exist, uv_python not a dependency -> compile failure.
# On correct fix: compiles and all assertions pass.
_DISPLAY_INJECT = """

#[cfg(test)]
mod harbor_display_check {
    use super::{Error, PythonVersion};
    use std::str::FromStr;
    use uv_distribution_filename::WheelFilename;
    use uv_platform_tags::{Arch, Os, Platform};
    use uv_python::PythonVariant;

    #[test]
    fn harbor_freethreaded_version_display() {
        let pv = PythonVersion {
            version: (3, 15),
            variant: PythonVariant::Freethreaded,
        };
        let s = format!("{pv}");
        assert_eq!(s, "3.15t", "Freethreaded PythonVersion should be 3.15t, got {s}");
    }

    #[test]
    fn harbor_default_version_display() {
        let pv = PythonVersion {
            version: (3, 14),
            variant: PythonVariant::Default,
        };
        let s = format!("{pv}");
        assert_eq!(s, "3.14", "Default PythonVersion should be 3.14, got {s}");
    }

    #[test]
    fn harbor_host_error_freethreaded() {
        let err = Error::BuiltWheelIncompatibleHostPlatform {
            filename: WheelFilename::from_str(
                "foo-1.0-cp315-abi3t-macosx_11_0_arm64.whl",
            ).unwrap(),
            python_platform: Platform::new(
                Os::Macos { major: 11, minor: 0 },
                Arch::Aarch64,
            ),
            python_version: PythonVersion {
                version: (3, 15),
                variant: PythonVariant::Freethreaded,
            },
        };
        let msg = err.to_string();
        assert!(
            msg.contains("Python 3.15t"),
            "Host error should mention Python 3.15t, got: {msg}"
        );
    }

    #[test]
    fn harbor_target_error_default() {
        let err = Error::BuiltWheelIncompatibleTargetPlatform {
            filename: WheelFilename::from_str(
                "bar-2.0-cp312-abi3-manylinux_2_17_x86_64.whl",
            ).unwrap(),
            python_platform: Platform::new(
                Os::Manylinux { major: 2, minor: 17 },
                Arch::X86_64,
            ),
            python_version: PythonVersion {
                version: (3, 12),
                variant: PythonVariant::Default,
            },
        };
        let msg = err.to_string();
        assert!(
            msg.contains("Python 3.12"),
            "Target error should mention Python 3.12, got: {msg}"
        );
        assert!(
            !msg.contains("3.12t"),
            "Default target error should not contain 3.12t, got: {msg}"
        );
    }
}
"""


# [pr_diff] fail_to_pass
def test_freethreaded_display():
    """PythonVersion displays 't' suffix for freethreaded; error messages include variant."""
    backup = ERROR_RS.read_text()
    try:
        ERROR_RS.write_text(backup + _DISPLAY_INJECT)
        r = subprocess.run(
            ["cargo", "test", "-p", "uv-distribution", "--", "harbor_display_check"],
            cwd=REPO, capture_output=True, timeout=300,
        )
        output = r.stdout.decode() + r.stderr.decode()
        assert r.returncode == 0, f"Display tests failed:\n{output[-2000:]}"
    finally:
        ERROR_RS.write_text(backup)


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — regression
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_crate_tests_pass():
    """uv-distribution crate's own tests pass."""
    r = subprocess.run(
        ["cargo", "test", "-p", "uv-distribution"],
        cwd=REPO, capture_output=True, timeout=300,
    )
    output = r.stdout.decode() + r.stderr.decode()
    assert r.returncode == 0, f"Crate tests failed:\n{output[-2000:]}"


# [repo_tests] pass_to_pass
def test_platform_tags_regression():
    """uv-platform-tags tests still pass."""
    r = subprocess.run(
        ["cargo", "test", "-p", "uv-platform-tags"],
        cwd=REPO, capture_output=True, timeout=300,
    )
    assert r.returncode == 0, (
        f"Platform tags tests failed:\n{r.stderr.decode()[-2000:]}"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from CLAUDE.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — CLAUDE.md:7 @ 87da0ce4
def test_no_forbidden_patterns_in_error():
    """No unwrap()/panic!()/unreachable!()/unsafe/allow() in error.rs non-test code (CLAUDE.md:7)."""
    content = ERROR_RS.read_text()
    # Extract non-test portion (everything before #[cfg(test)])
    if "#[cfg(test)]" in content:
        non_test = content[: content.index("#[cfg(test)]")]
    else:
        non_test = content
    for pattern in [".unwrap()", "panic!(", "unreachable!(", "unsafe "]:
        assert pattern not in non_test, (
            f"Found '{pattern}' in non-test portion of error.rs"
        )
    # CLAUDE.md:10 — PREFER #[expect()] over #[allow()] for clippy disabling
    for line in non_test.splitlines():
        stripped = line.strip()
        if stripped.startswith("#[allow("):
            assert False, (
                f"Found #[allow()] in error.rs — use #[expect()] instead per CLAUDE.md:10: {stripped}"
            )


# [agent_config] pass_to_pass — CLAUDE.md:16 @ 87da0ce4
def test_top_level_imports_in_error():
    """No local imports (deeply indented use statements) in error.rs (CLAUDE.md:16)."""
    content = ERROR_RS.read_text()
    if "#[cfg(test)]" in content:
        non_test = content[: content.index("#[cfg(test)]")]
    else:
        non_test = content
    for line in non_test.splitlines():
        stripped = line.rstrip()
        if stripped.startswith("        use "):
            assert False, f"Local import found in error.rs: {stripped.strip()}"


# [agent_config] pass_to_pass — CLAUDE.md:17-18 @ 87da0ce4
def test_no_abbreviated_names_in_error():
    """No shortened variable names in error.rs (CLAUDE.md:17-18)."""
    content = ERROR_RS.read_text()
    if "#[cfg(test)]" in content:
        non_test = content[: content.index("#[cfg(test)]")]
    else:
        non_test = content
    # Check for common abbreviations the rule explicitly forbids
    import re
    # Look for variable bindings with shortened names
    for line in non_test.splitlines():
        stripped = line.strip()
        # Skip comments and string literals
        if stripped.startswith("//") or stripped.startswith("///"):
            continue
        # Check for "let ver " or "let rp " style abbreviations
        if re.search(r'\blet\s+(?:mut\s+)?(?:ver|rp)\b', stripped):
            assert False, (
                f"Found abbreviated variable name in error.rs: {stripped}"
            )
