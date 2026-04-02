"""
Task: uv-dynamic-field-case-sensitive
Repo: astral-sh/uv @ b38bea427cca74f993c78213522a16a902b6046e
PR:   #18669

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import shutil
from pathlib import Path

import pytest

REPO = "/repo"
FILE = "crates/uv-pypi-types/src/metadata/metadata_resolver.rs"
FILE_PATH = Path(REPO) / FILE

# Rust test module injected into the source file to exercise case-insensitive
# Dynamic field matching from both parse_pkg_info and parse_metadata.
INJECTED_TESTS = r"""

#[cfg(test)]
mod injected_case_tests {
    use super::*;

    // ── parse_pkg_info: lowercase field names ──────────────────

    #[test]
    fn lowercase_requires_dist() {
        let s = "Metadata-Version: 2.3\nName: asdf\nVersion: 1.0\nDynamic: requires-dist";
        let meta = ResolutionMetadata::parse_pkg_info(s.as_bytes());
        assert!(meta.is_err(), "lowercase 'requires-dist' must be detected as Dynamic");
        assert!(matches!(meta.unwrap_err(), MetadataError::DynamicField("Requires-Dist")));
    }

    #[test]
    fn lowercase_requires_python() {
        let s = "Metadata-Version: 2.3\nName: asdf\nVersion: 1.0\nDynamic: requires-python";
        let meta = ResolutionMetadata::parse_pkg_info(s.as_bytes());
        assert!(meta.is_err(), "lowercase 'requires-python' must be detected as Dynamic");
        assert!(matches!(meta.unwrap_err(), MetadataError::DynamicField("Requires-Python")));
    }

    #[test]
    fn lowercase_provides_extra() {
        let s = "Metadata-Version: 2.3\nName: asdf\nVersion: 1.0\nDynamic: provides-extra";
        let meta = ResolutionMetadata::parse_pkg_info(s.as_bytes());
        assert!(meta.is_err(), "lowercase 'provides-extra' must be detected as Dynamic");
        assert!(matches!(meta.unwrap_err(), MetadataError::DynamicField("Provides-Extra")));
    }

    // ── parse_metadata: lowercase "version" ────────────────────

    #[test]
    fn lowercase_version_dynamic() {
        let s = "Metadata-Version: 2.3\nName: asdf\nVersion: 1.0\nDynamic: version";
        let meta = ResolutionMetadata::parse_metadata(s.as_bytes()).unwrap();
        assert!(meta.dynamic, "lowercase 'version' must set dynamic=true");
    }

    // ── parse_pkg_info: uppercase field names ──────────────────

    #[test]
    fn uppercase_requires_dist() {
        let s = "Metadata-Version: 2.3\nName: asdf\nVersion: 1.0\nDynamic: REQUIRES-DIST";
        let meta = ResolutionMetadata::parse_pkg_info(s.as_bytes());
        assert!(meta.is_err(), "uppercase 'REQUIRES-DIST' must be detected as Dynamic");
        assert!(matches!(meta.unwrap_err(), MetadataError::DynamicField("Requires-Dist")));
    }

    #[test]
    fn uppercase_version_dynamic() {
        let s = "Metadata-Version: 2.3\nName: asdf\nVersion: 1.0\nDynamic: VERSION";
        let meta = ResolutionMetadata::parse_metadata(s.as_bytes()).unwrap();
        assert!(meta.dynamic, "uppercase 'VERSION' must set dynamic=true");
    }

    // ── Regression: canonical casing still works ───────────────

    #[test]
    fn canonical_requires_dist_still_rejected() {
        let s = "Metadata-Version: 2.3\nName: asdf\nVersion: 1.0\nDynamic: Requires-Dist";
        let meta = ResolutionMetadata::parse_pkg_info(s.as_bytes());
        assert!(meta.is_err(), "canonical 'Requires-Dist' must still be rejected");
    }

    #[test]
    fn canonical_version_still_dynamic() {
        let s = "Metadata-Version: 2.3\nName: asdf\nVersion: 1.0\nDynamic: Version";
        let meta = ResolutionMetadata::parse_metadata(s.as_bytes()).unwrap();
        assert!(meta.dynamic, "canonical 'Version' must still set dynamic=true");
    }

    // ── Mixed case (additional robustness) ─────────────────────

    #[test]
    fn mixed_case_provides_extra() {
        let s = "Metadata-Version: 2.3\nName: asdf\nVersion: 1.0\nDynamic: pRoViDeS-eXtRa";
        let meta = ResolutionMetadata::parse_pkg_info(s.as_bytes());
        assert!(meta.is_err(), "mixed-case 'pRoViDeS-eXtRa' must be detected as Dynamic");
        assert!(matches!(meta.unwrap_err(), MetadataError::DynamicField("Provides-Extra")));
    }
}
"""


@pytest.fixture(scope="session", autouse=True)
def inject_rust_tests():
    """Inject Rust test functions into the source, compile once, clean up after."""
    backup = FILE_PATH.with_suffix(".rs.bak")
    shutil.copy2(FILE_PATH, backup)

    with open(FILE_PATH, "a") as f:
        f.write(INJECTED_TESTS)

    # Compile injected tests once
    r = subprocess.run(
        ["cargo", "test", "-p", "uv-pypi-types", "--no-run"],
        cwd=REPO,
        capture_output=True,
        timeout=600,
    )

    yield r.returncode == 0

    # Restore original file
    shutil.move(str(backup), str(FILE_PATH))


def _run_rust_test(name: str, *, timeout: int = 120) -> bool:
    """Run a single injected Rust test by name and return True if it passed."""
    r = subprocess.run(
        ["cargo", "test", "-p", "uv-pypi-types", "--", f"injected_case_tests::{name}", "--exact"],
        cwd=REPO,
        capture_output=True,
        timeout=timeout,
    )
    return r.returncode == 0


def _extract_function_body(content: str, func_name: str) -> str:
    """Extract the body of a Rust function by tracking brace depth."""
    start = content.find(f"fn {func_name}")
    assert start != -1, f"{func_name} not found in source"
    brace_start = content.find("{", start)
    depth = 0
    end = brace_start
    for i, ch in enumerate(content[brace_start:], brace_start):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    return content[brace_start:end]


# ---------------------------------------------------------------------------
# Gate (pass_to_pass, static) — crate must compile
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_compile(inject_rust_tests):
    """Crate compiles after modifications."""
    assert inject_rust_tests, "cargo test --no-run failed; source does not compile"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — case-insensitive Dynamic field matching
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_lowercase_requires_dist():
    """parse_pkg_info detects lowercase 'requires-dist' as dynamic."""
    assert _run_rust_test("lowercase_requires_dist")


# [pr_diff] fail_to_pass
def test_lowercase_requires_python():
    """parse_pkg_info detects lowercase 'requires-python' as dynamic."""
    assert _run_rust_test("lowercase_requires_python")


# [pr_diff] fail_to_pass
def test_lowercase_provides_extra():
    """parse_pkg_info detects lowercase 'provides-extra' as dynamic."""
    assert _run_rust_test("lowercase_provides_extra")


# [pr_diff] fail_to_pass
def test_lowercase_version_dynamic():
    """parse_metadata detects lowercase 'version' as dynamic."""
    assert _run_rust_test("lowercase_version_dynamic")


# [pr_diff] fail_to_pass
def test_uppercase_requires_dist():
    """parse_pkg_info detects uppercase 'REQUIRES-DIST' as dynamic."""
    assert _run_rust_test("uppercase_requires_dist")


# [pr_diff] fail_to_pass
def test_uppercase_version_dynamic():
    """parse_metadata detects uppercase 'VERSION' as dynamic."""
    assert _run_rust_test("uppercase_version_dynamic")


# [pr_diff] fail_to_pass
def test_mixed_case_provides_extra():
    """parse_pkg_info detects mixed-case 'pRoViDeS-eXtRa' as dynamic."""
    assert _run_rust_test("mixed_case_provides_extra")


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — canonical casing still works
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_canonical_requires_dist():
    """Canonical 'Requires-Dist' is still rejected (regression guard)."""
    assert _run_rust_test("canonical_requires_dist_still_rejected")


# [pr_diff] pass_to_pass
def test_canonical_version_dynamic():
    """Canonical 'Version' still sets dynamic=true (regression guard)."""
    assert _run_rust_test("canonical_version_still_dynamic")


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — upstream tests still pass
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_upstream_unit_tests():
    """Upstream metadata_resolver unit tests still pass."""
    r = subprocess.run(
        ["cargo", "test", "-p", "uv-pypi-types", "--", "metadata_resolver::tests"],
        cwd=REPO,
        capture_output=True,
        timeout=120,
    )
    assert r.returncode == 0, f"Upstream tests failed:\n{r.stderr.decode()[-500:]}"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_no_stub_macros():
    """No todo!() or unimplemented!() in metadata_resolver.rs."""
    content = FILE_PATH.read_text()
    assert "todo!(" not in content, "Found todo!() macro"
    assert "unimplemented!(" not in content, "Found unimplemented!() macro"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — CLAUDE.md rules
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — CLAUDE.md:7 @ b38bea427cca74f993c78213522a16a902b6046e
def test_no_unwrap_panic_in_parse_functions():
    """No .unwrap(), panic!(), or unreachable!() in parse_pkg_info/parse_metadata."""
    # AST-only because: Rust code cannot be imported/called from Python
    content = FILE_PATH.read_text()
    for func_name in ("parse_pkg_info", "parse_metadata"):
        body = _extract_function_body(content, func_name)
        assert ".unwrap()" not in body, f"{func_name} contains .unwrap()"
        assert "panic!(" not in body, f"{func_name} contains panic!()"
        assert "unreachable!(" not in body, f"{func_name} contains unreachable!()"


# [agent_config] pass_to_pass — CLAUDE.md:7 @ b38bea427cca74f993c78213522a16a902b6046e
def test_no_unsafe_in_parse_functions():
    """No unsafe blocks in parse_pkg_info/parse_metadata."""
    # AST-only because: Rust code cannot be imported/called from Python
    content = FILE_PATH.read_text()
    for func_name in ("parse_pkg_info", "parse_metadata"):
        body = _extract_function_body(content, func_name)
        assert "unsafe " not in body, f"{func_name} contains unsafe block"


# [agent_config] pass_to_pass — CLAUDE.md:10 @ b38bea427cca74f993c78213522a16a902b6046e
def test_expect_over_allow():
    """Uses #[expect()] instead of #[allow()] for clippy attributes in modified file."""
    # AST-only because: Rust code cannot be imported/called from Python
    content = FILE_PATH.read_text()
    # Check that no new #[allow(clippy:: directives were added
    assert "#[allow(clippy::" not in content, \
        "Use #[expect()] instead of #[allow()] per CLAUDE.md"
