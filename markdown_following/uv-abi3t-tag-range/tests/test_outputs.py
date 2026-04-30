"""
Task: uv-abi3t-tag-range
Repo: uv @ b7d5faf568b30c86daf7503f8518e11cbfeeaa81
PR:   18777

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/uv"
TAGS_RS = Path(REPO) / "crates/uv-platform-tags/src/tags.rs"

# Custom Rust tests injected into the crate's test module.
# These check the behavioral fix: abi3t tags should be emitted for ALL
# abi3-compatible versions (3.2+), not just starting from 3.15.
CUSTOM_RUST_TESTS = r'''
    #[test]
    fn abi3t_emitted_for_cp32_with_freethreaded_315() {
        // Free-threaded CPython 3.15 should emit abi3t for cp32 through cp315
        let tags = Tags::from_env(
            &Platform::new(Os::Manylinux { major: 2, minor: 28 }, Arch::X86_64),
            (3, 15), "cpython", (3, 15), false, true, false,
        ).unwrap();
        let s = format!("{tags}");
        assert!(s.contains("cp32-abi3t"), "Missing cp32-abi3t tag");
        assert!(s.contains("cp314-abi3t"), "Missing cp314-abi3t tag");
        assert!(s.contains("cp38-abi3t"), "Missing cp38-abi3t tag");
    }

    #[test]
    fn abi3t_emitted_for_freethreaded_313() {
        // Free-threaded CPython 3.13 should emit abi3t for cp32 through cp313
        let tags = Tags::from_env(
            &Platform::new(Os::Manylinux { major: 2, minor: 28 }, Arch::X86_64),
            (3, 13), "cpython", (3, 13), false, true, false,
        ).unwrap();
        let s = format!("{tags}");
        assert!(s.contains("cp32-abi3t"), "Missing cp32-abi3t for 3.13t");
        assert!(s.contains("cp313-abi3t"), "Missing cp313-abi3t for 3.13t");
        assert!(s.contains("cp310-abi3t"), "Missing cp310-abi3t for 3.13t");
    }
'''


def _inject_custom_tests():
    """Inject custom Rust tests into the test module of tags.rs.

    Returns the original content for restoration.
    """
    original = TAGS_RS.read_text()
    # The test module's closing brace is the last `}` in the file
    idx = original.rfind("}")
    modified = original[:idx] + CUSTOM_RUST_TESTS + "\n}"
    TAGS_RS.write_text(modified)
    return original


def _run_cargo_test(test_name, timeout=300):
    """Run a specific cargo test in the uv-platform-tags crate."""
    return subprocess.run(
        ["cargo", "test", "--package", "uv-platform-tags", "--",
         f"tags::tests::{test_name}", "--exact"],
        cwd=REPO, capture_output=True, timeout=timeout,
    )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, repo_tests) — compilation check
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_crate_compiles():
    """The uv-platform-tags crate must compile without errors."""
    r = subprocess.run(
        ["cargo", "check", "--package", "uv-platform-tags"],
        cwd=REPO, capture_output=True, timeout=300,
    )
    assert r.returncode == 0, f"Compilation failed:\n{r.stderr.decode()}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_abi3t_tags_for_lower_versions():
    """Free-threaded CPython 3.15 must emit abi3t tags for versions 3.2-3.14."""
    original = _inject_custom_tests()
    try:
        r = _run_cargo_test("abi3t_emitted_for_cp32_with_freethreaded_315")
        assert r.returncode == 0, (
            f"abi3t tags not emitted for lower versions:\n"
            f"{r.stdout.decode()}\n{r.stderr.decode()}"
        )
    finally:
        TAGS_RS.write_text(original)


# [pr_diff] fail_to_pass
def test_abi3t_tags_with_python313():
    """Free-threaded CPython 3.13 must also emit abi3t tags (3.2-3.13)."""
    original = _inject_custom_tests()
    try:
        r = _run_cargo_test("abi3t_emitted_for_freethreaded_313")
        assert r.returncode == 0, (
            f"abi3t tags not emitted for 3.13t:\n"
            f"{r.stdout.decode()}\n{r.stderr.decode()}"
        )
    finally:
        TAGS_RS.write_text(original)


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — regression
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_existing_tests_pass():
    """Upstream snapshot test for free-threaded tags still passes."""
    r = _run_cargo_test("test_system_tags_freethreaded_include_abi3t")
    assert r.returncode == 0, (
        f"Existing tests failed:\n{r.stdout.decode()}\n{r.stderr.decode()}"
    )


# [repo_tests] pass_to_pass
def test_uv_platform_tags_cargo_test():
    """All tests in uv-platform-tags crate pass (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "test", "--package", "uv-platform-tags"],
        cwd=REPO, capture_output=True, text=True, timeout=300,
    )
    assert r.returncode == 0, (
        f"Cargo test failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"
    )


# [repo_tests] pass_to_pass
def test_uv_platform_tags_clippy():
    """Clippy lints pass for uv-platform-tags crate (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "clippy", "--package", "uv-platform-tags",
         "--all-targets", "--all-features", "--", "-D", "warnings"],
        cwd=REPO, capture_output=True, text=True, timeout=300,
    )
    assert r.returncode == 0, (
        f"Clippy failed:\n{r.stderr[-500:]}"
    )


# [repo_tests] pass_to_pass
def test_uv_platform_tags_cargo_fmt():
    """Rustfmt check passes for uv-platform-tags crate (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "fmt", "--package", "uv-platform-tags", "--check"],
        cwd=REPO, capture_output=True, text=True, timeout=300,
    )
    assert r.returncode == 0, (
        f"cargo fmt check failed:\n{r.stderr[-500:]}"
    )


# [repo_tests] pass_to_pass
def test_doc_build():
    """Documentation builds successfully for uv-platform-tags crate (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "doc", "--no-deps", "--package", "uv-platform-tags"],
        cwd=REPO, capture_output=True, text=True, timeout=300,
    )
    assert r.returncode == 0, (
        f"Documentation build failed:\n{r.stderr[-500:]}"
    )
