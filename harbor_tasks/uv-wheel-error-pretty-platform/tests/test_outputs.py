"""
Task: uv-wheel-error-pretty-platform
Repo: astral-sh/uv @ 202e0f083180c36907ee7fbb5bdf7707722a9521
PR:   #18738

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

import pytest

REPO = "/repo"
PLATFORM_RS = Path(REPO) / "crates/uv-platform-tags/src/platform.rs"
ERROR_RS = Path(REPO) / "crates/uv-distribution/src/error.rs"

# Rust tests injected into error.rs to verify Display output of error variants.
# Each test constructs an error with a specific OS and asserts the rendered message
# contains the human-readable OS name (not the raw internal representation).
VERIFIER_RUST_TESTS = r'''
#[cfg(test)]
mod __verifier_pretty_platform {
    use super::Error;
    use std::str::FromStr;
    use uv_distribution_filename::WheelFilename;
    use uv_platform_tags::{Arch, Os, Platform};

    #[test]
    fn host_macos() {
        let err = Error::BuiltWheelIncompatibleHostPlatform {
            filename: WheelFilename::from_str(
                "cryptography-47.0.0.dev1-cp315-abi3t-macosx_11_0_arm64.whl",
            )
            .unwrap(),
            python_platform: Platform::new(
                Os::Macos {
                    major: 11,
                    minor: 0,
                },
                Arch::Aarch64,
            ),
            python_version: (3, 15),
        };
        let msg = err.to_string();
        assert!(msg.contains("macOS"), "Expected 'macOS' in: {msg}");
    }

    #[test]
    fn target_manylinux() {
        let err = Error::BuiltWheelIncompatibleTargetPlatform {
            filename: WheelFilename::from_str("foo-1.0.0-py313-none-any.whl").unwrap(),
            python_platform: Platform::new(
                Os::Manylinux {
                    major: 2,
                    minor: 28,
                },
                Arch::X86_64,
            ),
            python_version: (3, 12),
        };
        let msg = err.to_string();
        assert!(msg.contains("Linux"), "Expected 'Linux' in: {msg}");
        assert!(
            !msg.contains("manylinux"),
            "Should not contain raw 'manylinux': {msg}"
        );
    }

    #[test]
    fn host_musllinux() {
        let err = Error::BuiltWheelIncompatibleHostPlatform {
            filename: WheelFilename::from_str("foo-1.0.0-py3-none-linux_x86_64.whl").unwrap(),
            python_platform: Platform::new(
                Os::Musllinux {
                    major: 1,
                    minor: 2,
                },
                Arch::X86_64,
            ),
            python_version: (3, 11),
        };
        let msg = err.to_string();
        assert!(msg.contains("Linux"), "Expected 'Linux' in: {msg}");
        assert!(
            !msg.contains("musllinux"),
            "Should not contain raw 'musllinux': {msg}"
        );
    }

    #[test]
    fn host_windows() {
        let err = Error::BuiltWheelIncompatibleHostPlatform {
            filename: WheelFilename::from_str("foo-1.0.0-py3-none-win_amd64.whl").unwrap(),
            python_platform: Platform::new(Os::Windows, Arch::X86_64),
            python_version: (3, 12),
        };
        let msg = err.to_string();
        assert!(msg.contains("Windows"), "Expected 'Windows' in: {msg}");
    }
}
'''


@pytest.fixture(scope="session")
def behavioral_results():
    """Inject verifier Rust tests into error.rs, compile and run, then restore."""
    original = ERROR_RS.read_text()
    try:
        ERROR_RS.write_text(original + VERIFIER_RUST_TESTS)
        r = subprocess.run(
            ["cargo", "test", "-p", "uv-distribution", "__verifier_pretty_platform"],
            cwd=REPO,
            capture_output=True,
            timeout=300,
        )
        return r.stdout.decode() + r.stderr.decode(), r.returncode
    finally:
        ERROR_RS.write_text(original)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — compilation check
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_cargo_check():
    """Modified crates must compile without errors."""
    r = subprocess.run(
        ["cargo", "check", "-p", "uv-platform-tags", "-p", "uv-distribution"],
        cwd=REPO,
        capture_output=True,
        timeout=300,
    )
    assert r.returncode == 0, f"cargo check failed:\n{r.stderr.decode()[-2000:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_host_error_macos_pretty(behavioral_results):
    """Host platform error shows 'macOS' (capitalized) instead of raw 'macos'."""
    output, _ = behavioral_results
    assert "host_macos ... ok" in output, (
        f"Host macOS capitalization test failed:\n{output[-2000:]}"
    )


# [pr_diff] fail_to_pass
def test_target_error_linux_pretty(behavioral_results):
    """Target platform error shows 'Linux' instead of raw 'manylinux'."""
    output, _ = behavioral_results
    assert "target_manylinux ... ok" in output, (
        f"Target manylinux → Linux test failed:\n{output[-2000:]}"
    )


# [pr_diff] fail_to_pass
def test_host_error_musllinux_pretty(behavioral_results):
    """Host platform error shows 'Linux' for musllinux, not raw 'musllinux'."""
    output, _ = behavioral_results
    assert "host_musllinux ... ok" in output, (
        f"Musllinux → Linux test failed:\n{output[-2000:]}"
    )


# [pr_diff] fail_to_pass
def test_host_error_windows_pretty(behavioral_results):
    """Host platform error shows 'Windows' (capitalized) instead of raw 'windows'."""
    output, _ = behavioral_results
    assert "host_windows ... ok" in output, (
        f"Windows capitalization test failed:\n{output[-2000:]}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — regression
# ---------------------------------------------------------------------------


# [repo_tests] pass_to_pass
def test_existing_platform_tags_tests():
    """Upstream uv-platform-tags test suite still passes."""
    r = subprocess.run(
        ["cargo", "test", "-p", "uv-platform-tags"],
        cwd=REPO,
        capture_output=True,
        timeout=300,
    )
    output = r.stdout.decode() + r.stderr.decode()
    assert "test result: ok" in output, (
        f"uv-platform-tags tests failed:\n{output[-2000:]}"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — CLAUDE.md rules
# ---------------------------------------------------------------------------


# [agent_config] pass_to_pass — CLAUDE.md:7 @ 202e0f083180c36907ee7fbb5bdf7707722a9521
def test_no_unwrap_panic_in_new_code():
    """New non-test code in platform.rs avoids unwrap/panic/unreachable/unsafe (CLAUDE.md:7)."""
    r = subprocess.run(
        ["git", "diff", "HEAD", "--", "crates/uv-platform-tags/src/platform.rs"],
        cwd=REPO,
        capture_output=True,
        timeout=10,
    )
    diff_output = r.stdout.decode()
    if not diff_output.strip():
        return  # No changes to platform.rs — nothing to check

    # Extract added lines, stopping at test module boundary
    non_test_added = []
    for line in diff_output.splitlines():
        if not line.startswith("+") or line.startswith("+++"):
            continue
        content = line[1:]
        if "#[cfg(test)]" in content:
            break
        non_test_added.append(content)

    code = "\n".join(non_test_added)
    for forbidden in ["unwrap()", "panic!", "unreachable!"]:
        assert forbidden not in code, (
            f"Non-test code in platform.rs uses '{forbidden}' (CLAUDE.md:7)"
        )
    # Check unsafe separately (avoid matching "unsafe" in comments/strings)
    assert not re.search(r"\bunsafe\b", code), (
        "Non-test code in platform.rs uses 'unsafe' (CLAUDE.md:7)"
    )


# [agent_config] pass_to_pass — CLAUDE.md:10 @ 202e0f083180c36907ee7fbb5bdf7707722a9521
def test_no_allow_in_new_code():
    """New non-test code prefers #[expect()] over #[allow()] (CLAUDE.md:10)."""
    for path in [PLATFORM_RS, ERROR_RS]:
        r = subprocess.run(
            ["git", "diff", "HEAD", "--", str(path)],
            cwd=REPO,
            capture_output=True,
            timeout=10,
        )
        diff_output = r.stdout.decode()
        if not diff_output.strip():
            continue

        # Extract added non-test lines
        in_test = False
        for line in diff_output.splitlines():
            if not line.startswith("+") or line.startswith("+++"):
                continue
            content = line[1:]
            if "#[cfg(test)]" in content:
                in_test = True
            if in_test:
                continue
            assert "#[allow(" not in content, (
                f"New non-test code uses #[allow()] instead of #[expect()] (CLAUDE.md:10): {content.strip()}"
            )
