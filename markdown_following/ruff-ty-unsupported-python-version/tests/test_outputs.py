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
# pass_to_pass (static) -- compilation check
# ---------------------------------------------------------------------------

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
    assert r.returncode == 0, f"Compilation failed:\n{r.stderr[-1000:]}"


# ---------------------------------------------------------------------------
# pass_to_pass (repo_tests) -- repo's own CI checks, scoped to ty_project
# ---------------------------------------------------------------------------

def test_repo_clippy():
    """Repo's cargo clippy on ty_project passes (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "clippy", "-p", "ty_project", "--", "-D", "warnings"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180,
        env={**os.environ, "CARGO_PROFILE_DEV_OPT_LEVEL": "1"},
    )
    assert r.returncode == 0, f"Clippy failed:\n{r.stderr[-1000:]}"


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


def test_repo_unit_tests():
    """Repo's unit tests for ty_project crate pass, excluding injected harness tests."""
    r = subprocess.run(
        ["cargo", "test", "-p", "ty_project", "--lib", "--", "--skip", "harness"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        env={**os.environ, "CARGO_PROFILE_DEV_OPT_LEVEL": "1"},
    )
    assert r.returncode == 0, f"Unit tests failed:\n{r.stderr[-1000:]}\n{r.stdout[-1000:]}"


def test_repo_doc():
    """Repo's documentation for ty_project crate builds without warnings."""
    r = subprocess.run(
        ["cargo", "doc", "--no-deps", "-p", "ty_project"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180,
        env={**os.environ, "RUSTDOCFLAGS": "-D warnings"},
    )
    assert r.returncode == 0, f"Documentation build failed:\n{r.stderr[-1000:]}"


# ---------------------------------------------------------------------------
# fail_to_pass (pr_diff) -- core behavioral tests for the feature
# ---------------------------------------------------------------------------

def test_rejects_unsupported_python_27():
    """Deserializing python-version='2.7' in config must fail."""
    _ensure_harness_injected()
    r = _cargo_test("harness_tests::harness_rejects_unsupported_27")
    assert r.returncode == 0, (
        f"Test failed -- deserialization should reject Python 2.7:\n"
        f"{r.stdout[-2000:]}\n{r.stderr[-2000:]}"
    )


def test_rejects_unsupported_python_36():
    """Deserializing python-version='3.6' in config must fail."""
    _ensure_harness_injected()
    r = _cargo_test("harness_tests::harness_rejects_unsupported_36")
    assert r.returncode == 0, (
        f"Test failed -- deserialization should reject Python 3.6:\n"
        f"{r.stdout[-2000:]}\n{r.stderr[-2000:]}"
    )


# ---------------------------------------------------------------------------
# pass_to_pass (pr_diff) -- supported versions still work
# ---------------------------------------------------------------------------

def test_accepts_supported_python_312():
    """Deserializing python-version='3.12' in config must succeed."""
    _ensure_harness_injected()
    r = _cargo_test("harness_tests::harness_accepts_supported_312")
    assert r.returncode == 0, (
        f"Test failed -- deserialization should accept Python 3.12:\n"
        f"{r.stdout[-2000:]}\n{r.stderr[-2000:]}"
    )


def test_accepts_supported_python_313():
    """Deserializing python-version='3.13' in config must succeed."""
    _ensure_harness_injected()
    r = _cargo_test("harness_tests::harness_accepts_supported_313")
    assert r.returncode == 0, (
        f"Test failed -- deserialization should accept Python 3.13:\n"
        f"{r.stdout[-2000:]}\n{r.stderr[-2000:]}"
    )


# ---------------------------------------------------------------------------
# pass_to_pass (repo_tests) -- CI-style bash -lc check
# ---------------------------------------------------------------------------

def test_ci_cargo_check_ty_project():
    """CI-style cargo check on ty_project via bash -lc."""
    r = subprocess.run(
        ["bash", "-lc", "cargo check -p ty_project"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180,
        env={**os.environ, "CARGO_PROFILE_DEV_OPT_LEVEL": "1"},
    )
    assert r.returncode == 0, (
        f"CI cargo check failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1000:]}\nstderr: {r.stderr[-1000:]}"
    )

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_cargo_test_ty_mdtests_github_annotations():
    """pass_to_pass | CI job 'cargo test' → step 'ty mdtests (GitHub annotations)'"""
    r = subprocess.run(
        ["bash", "-lc", 'cargo test -p ty_python_semantic --test mdtest'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'ty mdtests (GitHub annotations)' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_cargo_test_run_tests():
    """pass_to_pass | CI job 'cargo test' → step 'Run tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'cargo insta test --all-features --unreferenced reject --test-runner nextest'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_cargo_test_dogfood_ty_on_py_fuzzer():
    """pass_to_pass | CI job 'cargo test' → step 'Dogfood ty on py-fuzzer'"""
    r = subprocess.run(
        ["bash", "-lc", 'uv run --project=./python/py-fuzzer cargo run -p ty check --project=./python/py-fuzzer'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Dogfood ty on py-fuzzer' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_cargo_test_dogfood_ty_on_the_scripts_directory():
    """pass_to_pass | CI job 'cargo test' → step 'Dogfood ty on the scripts directory'"""
    r = subprocess.run(
        ["bash", "-lc", 'uv run --project=./scripts cargo run -p ty check --project=./scripts'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Dogfood ty on the scripts directory' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_cargo_test_dogfood_ty_on_ty_benchmark():
    """pass_to_pass | CI job 'cargo test' → step 'Dogfood ty on ty_benchmark'"""
    r = subprocess.run(
        ["bash", "-lc", 'uv run --project=./scripts/ty_benchmark cargo run -p ty check --project=./scripts/ty_benchmark'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Dogfood ty on ty_benchmark' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_cargo_test_cargo():
    """pass_to_pass | CI job 'cargo test' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'cargo doc --all --no-deps'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_cargo_test_cargo_2():
    """pass_to_pass | CI job 'cargo test' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'cargo doc --no-deps -p ty_python_semantic -p ty -p ty_test -p ruff_db -p ruff_python_formatter --document-private-items'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_cargo_build_build_tests():
    """pass_to_pass | CI job 'cargo build' → step 'Build tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'cargo "+${MSRV}" test --no-run --all-features'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_cargo_fuzz_build_cargo():
    """pass_to_pass | CI job 'cargo fuzz build' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'cargo fuzz build -s none'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_benchmarks_instrumented_ty_build_benchmarks():
    """pass_to_pass | CI job 'benchmarks instrumented ty' → step 'Build benchmarks'"""
    r = subprocess.run(
        ["bash", "-lc", 'cargo codspeed build -m simulation -m memory --features "codspeed,ty_instrumented" --profile profiling --no-default-features -p ruff_benchmark --bench ty'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build benchmarks' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_benchmarks_walltime_build_benchmarks():
    """pass_to_pass | CI job 'benchmarks walltime' → step 'Build benchmarks'"""
    r = subprocess.run(
        ["bash", "-lc", 'cargo codspeed build -m walltime --features "codspeed,ty_walltime" --profile profiling --no-default-features -p ruff_benchmark'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build benchmarks' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_ruff_lsp_build_ruff_binary():
    """pass_to_pass | CI job 'test ruff-lsp' → step 'Build Ruff binary'"""
    r = subprocess.run(
        ["bash", "-lc", 'cargo build -p ruff --bin ruff'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build Ruff binary' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

# === Execution-mined f2p tests (taskforge.exec_f2p_miner) ===
# Source: dual-pass exec at base vs gold inside the task's docker image
# Test command: cargo test -p ty_python_semantic --test mdtest || true
# 0 fail→pass + 50 pass→pass test name(s) discovered.

def test_exec_p2p_mdtest_abstract_md(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'mdtest::abstract.md'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mdtest_annotations_annotated_md(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'mdtest::annotations/annotated.md'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mdtest_annotations_any_md(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'mdtest::annotations/any.md'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mdtest_annotations_callable_md(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'mdtest::annotations/callable.md'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mdtest_annotations_deferred_md(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'mdtest::annotations/deferred.md'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mdtest_annotations_generic_alias_md(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'mdtest::annotations/generic_alias.md'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mdtest_annotations_int_float_complex_md(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'mdtest::annotations/int_float_complex.md'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mdtest_annotations_invalid_md(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'mdtest::annotations/invalid.md'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mdtest_annotations_literal_md(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'mdtest::annotations/literal.md'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mdtest_annotations_literal_string_md(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'mdtest::annotations/literal_string.md'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mdtest_annotations_never_md(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'mdtest::annotations/never.md'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mdtest_annotations_new_types_md(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'mdtest::annotations/new_types.md'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mdtest_annotations_optional_md(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'mdtest::annotations/optional.md'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mdtest_annotations_self_md(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'mdtest::annotations/self.md'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mdtest_annotations_starred_md(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'mdtest::annotations/starred.md'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mdtest_annotations_stdlib_typing_aliases_md(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'mdtest::annotations/stdlib_typing_aliases.md'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mdtest_annotations_string_md(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'mdtest::annotations/string.md'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mdtest_annotations_union_md(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'mdtest::annotations/union.md'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mdtest_annotations_unsupported_special_forms_md(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'mdtest::annotations/unsupported_special_forms.md'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mdtest_annotations_unsupported_special_types_md(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'mdtest::annotations/unsupported_special_types.md'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mdtest_annotations_unsupported_type_qualifiers_md(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'mdtest::annotations/unsupported_type_qualifiers.md'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mdtest_assignment_annotations_md(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'mdtest::assignment/annotations.md'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mdtest_assignment_augmented_md(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'mdtest::assignment/augmented.md'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mdtest_assignment_multi_target_md(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'mdtest::assignment/multi_target.md'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mdtest_assignment_unbound_md(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'mdtest::assignment/unbound.md'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mdtest_assignment_walrus_md(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'mdtest::assignment/walrus.md'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mdtest_async_md(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'mdtest::async.md'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mdtest_attributes_md(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'mdtest::attributes.md'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mdtest_bidirectional_md(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'mdtest::bidirectional.md'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mdtest_binary_booleans_md(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'mdtest::binary/booleans.md'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mdtest_binary_classes_md(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'mdtest::binary/classes.md'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mdtest_binary_custom_md(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'mdtest::binary/custom.md'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mdtest_binary_instances_md(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'mdtest::binary/instances.md'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mdtest_binary_integers_md(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'mdtest::binary/integers.md'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mdtest_binary_tuples_md(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'mdtest::binary/tuples.md'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mdtest_binary_unions_md(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'mdtest::binary/unions.md'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mdtest_boolean_short_circuit_md(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'mdtest::boolean/short_circuit.md'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mdtest_boundness_declaredness_public_md(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'mdtest::boundness_declaredness/public.md'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mdtest_call_abstract_method_md(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'mdtest::call/abstract_method.md'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mdtest_call_annotation_md(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'mdtest::call/annotation.md'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mdtest_call_builtins_md(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'mdtest::call/builtins.md'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mdtest_call_callable_instance_md(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'mdtest::call/callable_instance.md'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mdtest_call_callables_as_descriptors_md(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'mdtest::call/callables_as_descriptors.md'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mdtest_call_constructor_md(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'mdtest::call/constructor.md'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mdtest_call_dunder_md(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'mdtest::call/dunder.md'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mdtest_call_dunder_import_md(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'mdtest::call/dunder_import.md'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mdtest_call_function_md(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'mdtest::call/function.md'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mdtest_call_getattr_static_md(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'mdtest::call/getattr_static.md'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mdtest_call_invalid_syntax_md(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'mdtest::call/invalid_syntax.md'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_mdtest_call_methods_md(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'mdtest::call/methods.md'
    pass  # placeholder — recorded in manifest under origin: exec_diff

