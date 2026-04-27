"""Behavioral tests for uv PR #18536 (abi3 wheels => Python lower bound)."""

from __future__ import annotations

import subprocess
import textwrap
from pathlib import Path

REPO = Path("/workspace/uv")
CRATE = REPO / "crates" / "uv-distribution-types"
ABI3_TEST = CRATE / "tests" / "_abi3_external_test.rs"

ABI3_TEST_CONTENT = textwrap.dedent("""\
    use std::str::FromStr;

    use uv_distribution_filename::WheelFilename;
    use uv_distribution_types::implied_markers;

    fn marker_str(filename: &str) -> String {
        let wheel = WheelFilename::from_str(filename).unwrap();
        let markers = implied_markers(&wheel);
        match markers.contents() {
            Some(c) => format!("{c}"),
            None => String::new(),
        }
    }

    #[test]
    fn abi3_cp39_lower_bound_pure_any() {
        let s = marker_str("example-1.0-cp39-abi3-any.whl");
        assert!(
            s.contains("python_full_version >= '3.9'"),
            "expected lower bound `>= '3.9'` for cp39-abi3, got: {s}"
        );
        assert!(
            !s.contains("python_full_version < '3.10'"),
            "abi3 must NOT cap python_full_version, got: {s}"
        );
        assert!(
            s.contains("platform_python_implementation == 'CPython'"),
            "expected CPython implementation marker, got: {s}"
        );
    }

    #[test]
    fn abi3_cp312_lower_bound_pure_any() {
        let s = marker_str("example-1.0-cp312-abi3-any.whl");
        assert!(
            s.contains("python_full_version >= '3.12'"),
            "expected lower bound `>= '3.12'` for cp312-abi3, got: {s}"
        );
        assert!(
            !s.contains("python_full_version < '3.13'"),
            "abi3 must NOT cap python_full_version, got: {s}"
        );
    }

    #[test]
    fn abi3_cp3_major_only_lower_bound() {
        let s = marker_str("example-1.0-cp3-abi3-any.whl");
        assert!(
            s.contains("python_full_version >= '3'"),
            "expected lower bound `>= '3'` for cp3-abi3, got: {s}"
        );
        assert!(
            !s.contains("python_full_version < '4'"),
            "abi3 with major-only tag must NOT cap python_full_version, got: {s}"
        );
    }

    #[test]
    fn abi3_combines_with_manylinux_platform_markers() {
        let s = marker_str("example-1.0-cp39-abi3-manylinux_2_28_x86_64.whl");
        assert!(
            s.contains("python_full_version >= '3.9'"),
            "got: {s}"
        );
        assert!(
            s.contains("platform_python_implementation == 'CPython'"),
            "got: {s}"
        );
        assert!(s.contains("sys_platform == 'linux'"), "got: {s}");
        assert!(s.contains("platform_machine == 'x86_64'"), "got: {s}");
        assert!(
            !s.contains("python_full_version < '3.10'"),
            "abi3 must NOT cap python_full_version, got: {s}"
        );
    }

    #[test]
    fn non_abi3_cp39_remains_exact_version() {
        let s = marker_str("example-1.0-cp39-cp39-any.whl");
        // For a non-abi3 cp tag, the marker must collapse to the
        // `python_full_version == 'X.Y.*'` form (see existing
        // test_implied_python_markers: "example-1.0-cp310-cp310-any.whl" =>
        // "python_full_version == '3.10.*' and platform_python_implementation == 'CPython'").
        assert!(
            s.contains("python_full_version == '3.9.*'"),
            "non-abi3 cp39-cp39 must collapse to `== '3.9.*'`, got: {s}"
        );
        assert!(
            s.contains("platform_python_implementation == 'CPython'"),
            "got: {s}"
        );
    }

    #[test]
    fn py3_none_any_unchanged() {
        let s = marker_str("example-1.0-py3-none-any.whl");
        assert!(
            s.contains("python_full_version >= '3'"),
            "got: {s}"
        );
        assert!(
            s.contains("python_full_version < '4'"),
            "py3-none-any must keep `< '4'` cap, got: {s}"
        );
    }
""")


def _write_external_test():
    ABI3_TEST.parent.mkdir(parents=True, exist_ok=True)
    ABI3_TEST.write_text(ABI3_TEST_CONTENT)


def _run_external_test(test_name: str) -> subprocess.CompletedProcess:
    """Compile & run the injected integration test, filtered to one fn."""
    _write_external_test()
    args = [
        "cargo",
        "test",
        "--package",
        "uv-distribution-types",
        "--test",
        "_abi3_external_test",
        "--quiet",
        "--",
        "--exact",
        test_name,
    ]
    return subprocess.run(
        args, cwd=REPO, capture_output=True, text=True, timeout=900
    )


def _run_lib_test(test_path: str) -> subprocess.CompletedProcess:
    args = [
        "cargo",
        "test",
        "--package",
        "uv-distribution-types",
        "--lib",
        "--quiet",
        "--",
        "--exact",
        test_path,
    ]
    return subprocess.run(
        args, cwd=REPO, capture_output=True, text=True, timeout=900
    )


# ---------- fail-to-pass (behavioural) ----------


def test_abi3_cp39_lower_bound_pure_any():
    """cp39-abi3 wheel must produce python_full_version >= '3.9' with no upper cap."""
    r = _run_external_test("abi3_cp39_lower_bound_pure_any")
    assert r.returncode == 0, (
        f"cargo test failed:\nSTDOUT:\n{r.stdout[-3000:]}\nSTDERR:\n{r.stderr[-3000:]}"
    )


def test_abi3_cp312_lower_bound_pure_any():
    """cp312-abi3 wheel must produce python_full_version >= '3.12' with no upper cap."""
    r = _run_external_test("abi3_cp312_lower_bound_pure_any")
    assert r.returncode == 0, (
        f"cargo test failed:\nSTDOUT:\n{r.stdout[-3000:]}\nSTDERR:\n{r.stderr[-3000:]}"
    )


def test_abi3_cp3_major_only_lower_bound():
    """cp3-abi3 (major-only Python tag) must produce python_full_version >= '3'."""
    r = _run_external_test("abi3_cp3_major_only_lower_bound")
    assert r.returncode == 0, (
        f"cargo test failed:\nSTDOUT:\n{r.stdout[-3000:]}\nSTDERR:\n{r.stderr[-3000:]}"
    )


def test_abi3_combines_with_manylinux_platform_markers():
    """abi3 lower-bound combines correctly with manylinux platform markers."""
    r = _run_external_test("abi3_combines_with_manylinux_platform_markers")
    assert r.returncode == 0, (
        f"cargo test failed:\nSTDOUT:\n{r.stdout[-3000:]}\nSTDERR:\n{r.stderr[-3000:]}"
    )


# ---------- pass-to-pass: non-abi3 behaviour MUST be unchanged ----------


def test_non_abi3_cp39_remains_exact_version():
    """Non-abi3 cp39-cp39 wheels must still produce >= '3.9' AND < '3.10'."""
    r = _run_external_test("non_abi3_cp39_remains_exact_version")
    assert r.returncode == 0, (
        f"cargo test failed:\nSTDOUT:\n{r.stdout[-3000:]}\nSTDERR:\n{r.stderr[-3000:]}"
    )


def test_py3_none_any_unchanged():
    """py3-none-any wheels must still produce >= '3' AND < '4'."""
    r = _run_external_test("py3_none_any_unchanged")
    assert r.returncode == 0, (
        f"cargo test failed:\nSTDOUT:\n{r.stdout[-3000:]}\nSTDERR:\n{r.stderr[-3000:]}"
    )


# ---------- pass-to-pass: upstream unit tests must keep passing ----------


def test_upstream_test_implied_python_markers():
    r = _run_lib_test("prioritized_distribution::tests::test_implied_python_markers")
    assert r.returncode == 0, (
        f"upstream unit test failed:\nSTDOUT:\n{r.stdout[-3000:]}\nSTDERR:\n{r.stderr[-3000:]}"
    )


def test_upstream_test_implied_markers():
    r = _run_lib_test("prioritized_distribution::tests::test_implied_markers")
    assert r.returncode == 0, (
        f"upstream unit test failed:\nSTDOUT:\n{r.stdout[-3000:]}\nSTDERR:\n{r.stderr[-3000:]}"
    )


def test_upstream_test_implied_platform_markers():
    r = _run_lib_test("prioritized_distribution::tests::test_implied_platform_markers")
    assert r.returncode == 0, (
        f"upstream unit test failed:\nSTDOUT:\n{r.stdout[-3000:]}\nSTDERR:\n{r.stderr[-3000:]}"
    )
