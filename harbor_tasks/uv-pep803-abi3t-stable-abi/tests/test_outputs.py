"""
Task: uv-pep803-abi3t-stable-abi
Repo: uv @ 30e33420497d6d493d70895291e849f5dcf4f2b5
PR:   18767

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import os
import subprocess

REPO = "/workspace/uv"


def _write_file(rel_path: str, content: str):
    """Write content to a file relative to REPO."""
    full_path = os.path.join(REPO, rel_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w") as f:
        f.write(content)


# Rust integration test: parsing abi3t (uses only FromStr/Display, compiles on base)
_PARSE_TEST = """\
use std::str::FromStr;
use uv_platform_tags::AbiTag;

#[test]
fn abi3t_parses_ok() {
    let result = AbiTag::from_str("abi3t");
    assert!(result.is_ok(), "abi3t should be a recognized ABI tag (PEP 803)");
    assert_eq!(result.unwrap().to_string(), "abi3t");
}

#[test]
fn abi3t_distinct_from_abi3() {
    let abi3 = AbiTag::from_str("abi3").unwrap();
    let abi3t = AbiTag::from_str("abi3t").unwrap();
    assert_ne!(
        format!("{abi3}"), format!("{abi3t}"),
        "abi3 and abi3t must have different string representations"
    );
}
"""

# Rust integration test: is_stable_abi() method (won't compile on base — method missing)
_STABLE_TEST = """\
use std::str::FromStr;
use uv_platform_tags::AbiTag;

#[test]
fn abi3t_is_stable_abi() {
    let tag = AbiTag::from_str("abi3t").unwrap();
    assert!(tag.is_stable_abi(), "abi3t must be classified as a stable ABI");
}

#[test]
fn abi3t_pretty_mentions_freethreaded() {
    let tag = AbiTag::from_str("abi3t").unwrap();
    let pretty = tag.pretty().expect("abi3t should have a pretty description");
    let lower = pretty.to_lowercase();
    assert!(
        lower.contains("free") && lower.contains("thread"),
        "abi3t pretty description should mention free-threading, got: {pretty}"
    );
}
"""

# Rust integration test: wheel filename with abi3t
_WHEEL_TEST = """\
use std::str::FromStr;
use uv_distribution_filename::WheelFilename;

#[test]
fn abi3t_wheel_parses() {
    let whl = WheelFilename::from_str(
        "foo-1.2.3-cp315-abi3t-manylinux_2_17_x86_64.whl"
    );
    assert!(whl.is_ok(), "Wheel with abi3t ABI tag should parse: {:?}", whl.err());
    let parsed = whl.unwrap();
    let abi_strs: Vec<String> = parsed.abi_tags().iter().map(|t| t.to_string()).collect();
    assert!(
        abi_strs.contains(&"abi3t".to_string()),
        "Parsed wheel should have abi3t in ABI tags, got: {abi_strs:?}"
    );
}

#[test]
fn compound_abi3_abi3t_wheel() {
    let whl = WheelFilename::from_str(
        "foo-1.2.3-cp315-abi3.abi3t-manylinux_2_17_x86_64.whl"
    ).expect("Wheel with abi3.abi3t should parse");
    let abi_strs: Vec<String> = whl.abi_tags().iter().map(|t| t.to_string()).collect();
    assert!(abi_strs.contains(&"abi3".to_string()), "Should contain abi3, got: {abi_strs:?}");
    assert!(abi_strs.contains(&"abi3t".to_string()), "Should contain abi3t, got: {abi_strs:?}");
}
"""


def _ensure_test_files():
    """Write all Rust integration test files (idempotent)."""
    _write_file("crates/uv-platform-tags/tests/pep803_parse.rs", _PARSE_TEST)
    _write_file("crates/uv-platform-tags/tests/pep803_stable.rs", _STABLE_TEST)
    _write_file("crates/uv-distribution-filename/tests/pep803_wheel.rs", _WHEEL_TEST)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass) — compilation check
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_cargo_check_compiles():
    """All changed crates must compile without errors."""
    r = subprocess.run(
        ["cargo", "check", "--package", "uv-platform-tags",
         "--package", "uv-distribution-filename",
         "--package", "uv-distribution-types"],
        cwd=REPO, capture_output=True, timeout=600,
    )
    assert r.returncode == 0, f"Compilation failed:\n{r.stderr.decode()[-3000:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_abi3t_tag_parsing():
    """AbiTag::from_str('abi3t') must succeed and roundtrip through Display."""
    _ensure_test_files()
    r = subprocess.run(
        ["cargo", "test", "--package", "uv-platform-tags",
         "--test", "pep803_parse", "--", "abi3t_parses_ok"],
        cwd=REPO, capture_output=True, timeout=600,
    )
    assert r.returncode == 0, f"abi3t parsing failed:\n{r.stderr.decode()[-3000:]}"


# [pr_diff] fail_to_pass
def test_abi3t_is_stable_abi():
    """is_stable_abi() must return true for abi3t."""
    _ensure_test_files()
    r = subprocess.run(
        ["cargo", "test", "--package", "uv-platform-tags",
         "--test", "pep803_stable", "--", "abi3t_is_stable_abi", "--exact"],
        cwd=REPO, capture_output=True, timeout=600,
    )
    assert r.returncode == 0, f"is_stable_abi test failed:\n{r.stderr.decode()[-3000:]}"


# [pr_diff] fail_to_pass
def test_abi3t_pretty_description():
    """abi3t pretty() must mention free-threading."""
    _ensure_test_files()
    r = subprocess.run(
        ["cargo", "test", "--package", "uv-platform-tags",
         "--test", "pep803_stable", "--", "abi3t_pretty_mentions_freethreaded"],
        cwd=REPO, capture_output=True, timeout=600,
    )
    assert r.returncode == 0, f"pretty description test failed:\n{r.stderr.decode()[-3000:]}"


# [pr_diff] fail_to_pass
def test_abi3t_wheel_filename_parsing():
    """Wheel filename with abi3t ABI tag must parse and contain abi3t."""
    _ensure_test_files()
    r = subprocess.run(
        ["cargo", "test", "--package", "uv-distribution-filename",
         "--test", "pep803_wheel", "--", "abi3t_wheel_parses"],
        cwd=REPO, capture_output=True, timeout=600,
    )
    assert r.returncode == 0, f"Wheel abi3t parsing failed:\n{r.stderr.decode()[-3000:]}"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — existing tests still pass
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_existing_abi_unit_tests():
    """Existing ABI tag unit tests must still pass."""
    r = subprocess.run(
        ["cargo", "test", "--package", "uv-platform-tags", "--lib",
         "--", "abi_tag::tests"],
        cwd=REPO, capture_output=True, timeout=600,
    )
    assert r.returncode == 0, f"Existing ABI tests failed:\n{r.stderr.decode()[-3000:]}"
    # Verify at least some tests actually ran
    stderr = r.stderr.decode()
    assert "0 passed" not in stderr, f"No ABI tests were found:\n{stderr[-1000:]}"
