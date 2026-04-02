"""
Task: uv-torch-rocm72-backend
Repo: astral-sh/uv @ 96f329b8d2ab82245b86beb0be835dcbd7be254a
PR:   18730

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
import textwrap
from pathlib import Path

REPO = "/repo"
BACKEND_RS = f"{REPO}/crates/uv-torch/src/backend.rs"
SCHEMA_JSON = f"{REPO}/uv.schema.json"

# ---------------------------------------------------------------------------
# Shared: single cargo test run with all Rust behavioral tests
# ---------------------------------------------------------------------------

_cargo_cache: dict | None = None


def _run_cargo_tests() -> dict:
    """Write all Rust tests to one file, run cargo test once, cache results."""
    global _cargo_cache
    if _cargo_cache is not None:
        return _cargo_cache

    test_code = textwrap.dedent("""\
        use std::str::FromStr;
        use url::Url;
        use uv_torch::{AmdGpuArchitecture, TorchBackend};

        // --- rocm72_fromstr ---

        #[test]
        fn parse_rocm72() {
            let backend = TorchBackend::from_str("rocm7.2");
            assert!(backend.is_ok(), "Failed to parse 'rocm7.2' as TorchBackend");
        }

        #[test]
        fn parse_rocm72_equals_variant() {
            let b1 = TorchBackend::from_str("rocm7.2").unwrap();
            let b2 = TorchBackend::from_str("rocm7.2").unwrap();
            assert_eq!(b1, b2, "Parsing 'rocm7.2' twice should yield equal variants");
        }

        // --- rocm72_version_accessors ---

        #[test]
        fn rocm_version_is_7_2() {
            let b = TorchBackend::from_str("rocm7.2").unwrap();
            let v = b.rocm_version();
            assert!(v.is_some(), "Rocm72 should return Some rocm_version");
            assert_eq!(v.unwrap().to_string(), "7.2", "ROCm version should be 7.2");
        }

        #[test]
        fn cuda_version_is_none() {
            let b = TorchBackend::from_str("rocm7.2").unwrap();
            assert!(b.cuda_version().is_none(), "Rocm72 should have no CUDA version");
        }

        // --- new_gpu_architectures ---

        #[test]
        fn parse_gfx1150() {
            let a = AmdGpuArchitecture::from_str("gfx1150");
            assert!(a.is_ok(), "Failed to parse 'gfx1150'");
            assert_eq!(a.unwrap().to_string(), "gfx1150");
        }

        #[test]
        fn parse_gfx1151() {
            let a = AmdGpuArchitecture::from_str("gfx1151");
            assert!(a.is_ok(), "Failed to parse 'gfx1151'");
            assert_eq!(a.unwrap().to_string(), "gfx1151");
        }

        // --- rocm72_index_urls ---

        #[test]
        fn from_index_recognizes_rocm72_pytorch() {
            let url = Url::parse("https://download.pytorch.org/whl/rocm7.2").unwrap();
            let backend = TorchBackend::from_index(&url);
            assert!(backend.is_some(), "from_index should recognize rocm7.2 PyTorch URL");
            assert_eq!(backend.unwrap(), TorchBackend::from_str("rocm7.2").unwrap());
        }

        // --- existing_backends_still_work (p2p regression) ---

        #[test]
        fn rocm71_still_parses() {
            assert!(TorchBackend::from_str("rocm7.1").is_ok(), "rocm7.1 should still parse");
        }

        #[test]
        fn existing_archs_still_parse() {
            for s in &["gfx900", "gfx906", "gfx1100", "gfx1200"] {
                assert!(AmdGpuArchitecture::from_str(s).is_ok(), "Failed to parse {s}");
            }
        }

        #[test]
        fn cpu_backend_still_works() {
            let b = TorchBackend::from_str("cpu").unwrap();
            assert!(b.cuda_version().is_none());
            assert!(b.rocm_version().is_none());
        }
    """)

    test_dir = Path(REPO) / "crates" / "uv-torch" / "tests"
    test_dir.mkdir(parents=True, exist_ok=True)
    test_file = test_dir / "rocm72_all.rs"

    results: dict = {}
    try:
        test_file.write_text(test_code)
        r = subprocess.run(
            ["cargo", "test", "-p", "uv-torch", "--test", "rocm72_all"],
            cwd=REPO,
            capture_output=True,
            timeout=300,
        )
        output = r.stdout.decode() + r.stderr.decode()
        results["_output"] = output
        results["_compiled"] = "error[" not in output
        results["_returncode"] = r.returncode

        # Parse individual test results from cargo output
        for line in output.splitlines():
            stripped = line.strip()
            if stripped.startswith("test ") and " ... " in stripped:
                name = stripped.split()[1]
                results[name] = "... ok" in stripped
    except subprocess.TimeoutExpired:
        results["_output"] = "TIMEOUT: cargo test exceeded 300s"
        results["_compiled"] = False
        results["_returncode"] = -1
    finally:
        test_file.unlink(missing_ok=True)

    _cargo_cache = results
    return results


def _assert_cargo(test_name: str) -> None:
    """Assert a specific Rust test passed within the combined cargo run."""
    results = _run_cargo_tests()
    assert results.get("_compiled"), (
        f"uv-torch failed to compile:\n{results.get('_output', 'no output')}"
    )
    assert results.get(test_name, False), (
        f"Rust test '{test_name}' failed.\ncargo output:\n{results.get('_output', '')}"
    )


# ---------------------------------------------------------------------------
# Gate (pass_to_pass, static) — compilation check
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_compilation():
    """uv-torch crate compiles without errors."""
    results = _run_cargo_tests()
    assert results.get("_compiled"), (
        f"cargo check failed:\n{results.get('_output', 'no output')}"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests via cargo
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_rocm72_fromstr():
    """TorchBackend parses 'rocm7.2' via FromStr."""
    _assert_cargo("parse_rocm72")
    _assert_cargo("parse_rocm72_equals_variant")


# [pr_diff] fail_to_pass
def test_rocm72_version_accessors():
    """ROCm version returns 7.2 and CUDA version returns None for rocm7.2."""
    _assert_cargo("rocm_version_is_7_2")
    _assert_cargo("cuda_version_is_none")


# [pr_diff] fail_to_pass
def test_new_gpu_architectures():
    """New AMD GPU architectures gfx1150 and gfx1151 parse and display correctly."""
    _assert_cargo("parse_gfx1150")
    _assert_cargo("parse_gfx1151")


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — index URL statics (source inspection)
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_rocm72_index_urls():
    """Index URLs for rocm7.2 are properly wired up."""
    # Behavioral: from_index recognizes the rocm7.2 PyTorch URL
    _assert_cargo("from_index_recognizes_rocm72_pytorch")
    # Source inspection for Pyx URL (from_index only tests PyTorch URLs):
    content = Path(BACKEND_RS).read_text()
    assert "PYX_ROCM72_INDEX_URL" in content, (
        "backend.rs must define PYX_ROCM72_INDEX_URL static"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — schema update (pure Python, no cargo needed)
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_schema_includes_rocm72():
    """uv.schema.json includes 'rocm7.2' as a valid torch mode value."""
    schema_path = Path(SCHEMA_JSON)
    assert schema_path.exists(), "uv.schema.json not found"
    schema_str = schema_path.read_text()
    assert '"rocm7.2"' in schema_str, "uv.schema.json should contain '\"rocm7.2\"'"

    # Verify it appears as a const value (not just a random string)
    found = False
    for match in re.finditer(r'"const"\s*:\s*"([^"]+)"', schema_str):
        if match.group(1) == "rocm7.2":
            found = True
            break
    assert found, "rocm7.2 should appear as a JSON schema const value"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — GPU driver mappings (structural, unavoidable)
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_rocm72_gpu_driver_mappings():
    """backend.rs contains Rocm72 GPU driver mapping entries."""
    # Source inspection because: LINUX_AMD_GPU_DRIVERS is a private static array;
    # there is no runtime API to query which backends map to which architectures.
    content = Path(BACKEND_RS).read_text()
    rocm72_count = content.count("Rocm72")
    # The gold solution has 14 driver entries + ~8 match arms = ~22 total Rocm72 refs.
    # Require at least 12 to ensure driver mappings aren't omitted.
    assert rocm72_count >= 12, (
        f"Expected >=12 references to Rocm72 in backend.rs "
        f"(driver mappings + match arms), got {rocm72_count}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — regression
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_existing_backends_still_work():
    """Existing ROCm 7.1, GPU architectures, and CPU backend still parse."""
    _assert_cargo("rocm71_still_parses")
    _assert_cargo("existing_archs_still_parse")
    _assert_cargo("cpu_backend_still_works")


# ---------------------------------------------------------------------------
# Pass-to-pass (agent_config) — CLAUDE.md rules
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — CLAUDE.md:7 @ 96f329b8d2ab82245b86beb0be835dcbd7be254a
def test_no_panic_unwrap_in_new_code():
    """No unwrap()/panic!()/unreachable!() in Rocm72-related match arms (CLAUDE.md:7)."""
    content = Path(BACKEND_RS).read_text()
    lines = content.splitlines()
    violations = []
    for i, line in enumerate(lines, 1):
        if "Rocm72" not in line:
            continue
        # Skip infrastructure: URL defs, statics, driver array, comments, attributes
        if any(kw in line for kw in [
            "INDEX_URL", "LazyLock", "static", "//", "LINUX_AMD_GPU", "#["
        ]):
            continue
        for bad in [".unwrap()", "panic!", "unreachable!"]:
            if bad in line:
                violations.append(f"  line {i}: {bad} in: {line.strip()}")
    assert not violations, (
        "CLAUDE.md:7 forbids panic!/unwrap()/unreachable! in new code:\n"
        + "\n".join(violations)
    )
