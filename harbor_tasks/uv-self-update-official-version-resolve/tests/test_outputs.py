"""
Task: uv-self-update-official-version-resolve
Repo: astral-sh/uv @ 10477cd1ce808690a024e867417ce58df901d0c1
PR:   14994

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/repo"

# ---------------------------------------------------------------------------
# Shared: single Rust integration test compiled once for uv-bin-install
# ---------------------------------------------------------------------------

_BIN_INSTALL_RUST_TESTS = """\
use uv_bin_install::{ArchiveFormat, Binary};
use uv_pep440::{Version, VersionSpecifiers};

// -- binary_uv_name --

#[test]
fn uv_name_is_uv() {
    assert_eq!(Binary::Uv.name(), "uv");
}

#[test]
fn ruff_name_still_ruff() {
    assert_eq!(Binary::Ruff.name(), "ruff");
}

// -- binary_uv_download_url_format --

#[test]
fn uv_download_url_github_format() {
    let urls = Binary::Uv
        .download_urls(
            &Version::new([0, 6, 0]),
            "x86_64-unknown-linux-gnu",
            ArchiveFormat::TarGz,
        )
        .expect("should produce valid URLs");

    assert!(!urls.is_empty(), "Should have at least one URL");
    let url = urls[0].to_string();
    assert!(
        url.contains("github.com/astral-sh/uv/releases/download/"),
        "URL should be a GitHub uv release URL, got: {url}"
    );
    assert!(url.contains("0.6.0"), "URL should contain version, got: {url}");
    assert!(
        url.contains("x86_64-unknown-linux-gnu"),
        "URL should contain platform, got: {url}"
    );
    assert!(url.ends_with(".tar.gz"), "URL should end with .tar.gz, got: {url}");
}

// -- binary_uv_default_constraints_empty --

#[test]
fn uv_default_constraints_empty() {
    assert_eq!(
        Binary::Uv.default_constraints(),
        VersionSpecifiers::empty(),
        "Uv should have empty default constraints"
    );
}

// -- binary_uv_multiplatform_urls --

#[test]
fn uv_aarch64_darwin_zip() {
    let urls = Binary::Uv
        .download_urls(
            &Version::new([0, 7, 2]),
            "aarch64-apple-darwin",
            ArchiveFormat::Zip,
        )
        .expect("should produce valid URLs");

    let url = urls[0].to_string();
    assert!(url.contains("0.7.2"), "got: {url}");
    assert!(url.contains("aarch64-apple-darwin"), "got: {url}");
    assert!(url.ends_with(".zip"), "got: {url}");
}

#[test]
fn uv_windows_zip() {
    let urls = Binary::Uv
        .download_urls(
            &Version::new([1, 0, 0]),
            "x86_64-pc-windows-msvc",
            ArchiveFormat::Zip,
        )
        .expect("should produce valid URLs");

    let url = urls[0].to_string();
    assert!(url.contains("x86_64-pc-windows-msvc"), "got: {url}");
    assert!(url.contains("github.com/astral-sh/uv/"), "got: {url}");
}

// -- binary_uv_single_url_no_mirror --

#[test]
fn uv_single_url() {
    let urls = Binary::Uv
        .download_urls(
            &Version::new([0, 6, 0]),
            "x86_64-unknown-linux-gnu",
            ArchiveFormat::TarGz,
        )
        .expect("Uv URLs");

    assert_eq!(urls.len(), 1, "Uv should have 1 URL (no mirror), got {}", urls.len());
}

#[test]
fn ruff_still_has_mirror() {
    let urls = Binary::Ruff
        .download_urls(
            &Version::new([0, 9, 0]),
            "x86_64-unknown-linux-gnu",
            ArchiveFormat::TarGz,
        )
        .expect("Ruff URLs");

    assert_eq!(urls.len(), 2, "Ruff should still have 2 URLs, got {}", urls.len());
}
"""

_HARBOR_RESULTS: tuple[int, dict[str, bool], str] | None = None


def _run_bin_install_tests() -> tuple[int, dict[str, bool], str]:
    """Write all Binary::Uv integration tests into one file, compile once, parse results."""
    global _HARBOR_RESULTS
    if _HARBOR_RESULTS is not None:
        return _HARBOR_RESULTS

    test_dir = Path(REPO) / "crates/uv-bin-install/tests"
    test_dir.mkdir(parents=True, exist_ok=True)
    test_path = test_dir / "harbor.rs"

    try:
        test_path.write_text(_BIN_INSTALL_RUST_TESTS)
        r = subprocess.run(
            ["cargo", "test", "-p", "uv-bin-install", "--test", "harbor",
             "--", "--test-threads=1"],
            cwd=REPO, capture_output=True, timeout=300,
        )
        output = r.stdout.decode(errors="replace") + "\n" + r.stderr.decode(errors="replace")

        results: dict[str, bool] = {}
        for m in re.finditer(r"test (\w+) \.\.\. (ok|FAILED)", output):
            results[m.group(1)] = m.group(2) == "ok"

        _HARBOR_RESULTS = (r.returncode, results, output)
    finally:
        test_path.unlink(missing_ok=True)

    return _HARBOR_RESULTS


def _assert_rust_tests(expected: list[str]) -> None:
    """Assert named Rust tests passed in the single harbor integration test run."""
    returncode, results, output = _run_bin_install_tests()
    for name in expected:
        assert name in results, (
            f"Rust test '{name}' not found in cargo output. "
            f"Compilation may have failed.\n{output}"
        )
        assert results[name], f"Rust test '{name}' FAILED.\n{output}"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_compilation():
    """Both modified crates compile without errors."""
    for crate, extra in [("uv-bin-install", []), ("uv", ["--lib"])]:
        cmd = ["cargo", "check", "-p", crate] + extra
        r = subprocess.run(cmd, cwd=REPO, capture_output=True, timeout=300)
        assert r.returncode == 0, (
            f"cargo check -p {crate} failed:\n{r.stderr.decode(errors='replace')}"
        )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — Binary::Uv core API
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_binary_uv_name():
    """Binary::Uv variant exists and name() returns 'uv'."""
    _assert_rust_tests(["uv_name_is_uv", "ruff_name_still_ruff"])


# [pr_diff] fail_to_pass
def test_binary_uv_download_url_format():
    """Binary::Uv download URLs point to GitHub uv releases with correct format."""
    _assert_rust_tests(["uv_download_url_github_format"])


# [pr_diff] fail_to_pass
def test_binary_uv_default_constraints_empty():
    """Binary::Uv default_constraints returns empty (no version constraints)."""
    _assert_rust_tests(["uv_default_constraints_empty"])


# [pr_diff] fail_to_pass
def test_binary_uv_multiplatform_urls():
    """Binary::Uv download URLs work for different platforms and archive formats."""
    _assert_rust_tests(["uv_aarch64_darwin_zip", "uv_windows_zip"])


# [pr_diff] fail_to_pass
def test_binary_uv_single_url_no_mirror():
    """Binary::Uv has exactly 1 URL (no CDN mirror), while Ruff still has 2."""
    _assert_rust_tests(["uv_single_url", "ruff_still_has_mirror"])


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — regression
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_existing_uv_bin_install_tests():
    """Existing uv-bin-install library tests still pass."""
    r = subprocess.run(
        ["cargo", "test", "-p", "uv-bin-install", "--lib"],
        cwd=REPO, capture_output=True, timeout=300,
    )
    assert r.returncode == 0, (
        f"Existing uv-bin-install tests failed:\n"
        f"{r.stdout.decode(errors='replace')}\n{r.stderr.decode(errors='replace')}"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — CLAUDE.md rules
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — CLAUDE.md:7 @ 10477cd
def test_no_unwrap_in_official_path():
    """New official-path functions must not use .unwrap(), panic!, or unreachable!."""
    src = Path(f"{REPO}/crates/uv/src/commands/self_update.rs").read_text()

    # These functions must exist (fail_to_pass: absent in base commit)
    for fn_name in [
        "is_official_public_uv_install",
        "official_target_version_specifiers",
        "is_update_needed",
    ]:
        assert f"fn {fn_name}" in src, f"Missing function: {fn_name}"

    # Production code (before #[cfg(test)]) must not use forbidden patterns
    prod = src.split("#[cfg(test)]")[0] if "#[cfg(test)]" in src else src
    for pattern, label in [
        (".unwrap()", ".unwrap()"),
        ("panic!(", "panic!"),
        ("unreachable!(", "unreachable!"),
    ]:
        assert pattern not in prod, (
            f"Found '{label}' in self_update.rs production code. "
            f"CLAUDE.md:7: AVOID using panic!, unreachable!, .unwrap()"
        )


# [agent_config] fail_to_pass — CLAUDE.md:2 @ 10477cd
def test_self_update_has_tests():
    """self_update module must have working unit tests (CLAUDE.md: always add tests)."""
    r = subprocess.run(
        ["cargo", "test", "-p", "uv", "--lib", "--", "commands::self_update::tests"],
        cwd=REPO, capture_output=True, timeout=300,
    )
    output = r.stdout.decode(errors="replace") + r.stderr.decode(errors="replace")

    m = re.search(r"test result: ok\. (\d+) passed", output)
    passed = int(m.group(1)) if m else 0
    assert passed >= 2, (
        f"Expected >=2 passing self_update unit tests, got {passed}.\n{output}"
    )

    src = Path(f"{REPO}/crates/uv/src/commands/self_update.rs").read_text()
    test_section_match = re.search(r"#\[cfg\(test\)\]", src)
    assert test_section_match, "self_update.rs must have a #[cfg(test)] module"

    test_section = src[test_section_match.start():]
    assert_count = len(re.findall(r"assert[!_(]", test_section))
    assert assert_count >= 4, (
        f"Expected >=4 assertions in self_update tests, got {assert_count}"
    )
