import subprocess
import os
from pathlib import Path

REPO = Path("/workspace/ruff")


def test_is_standard_method_exists():
    """Parameters::is_standard() exists and correctly identifies standard parameter lists."""
    test_file = REPO / "crates/ty_python_semantic/src/types/tests.rs"
    backup = test_file.read_text()

    try:
        with open(test_file, "a") as f:
            f.write("""
#[test]
fn harness_is_standard() {
    use crate::types::signatures::{Parameters, ParametersKind};
    let db = setup_db();

    // Empty parameters are standard
    let params = Parameters::empty();
    assert!(params.is_standard());
    assert!(matches!(params.kind(), ParametersKind::Standard));

    // Todo parameters are gradual, not standard
    let todo_params = Parameters::todo();
    assert!(!todo_params.is_standard());
}
""")
        r = subprocess.run(
            ["cargo", "test", "-p", "ty_python_semantic", "--", "harness_is_standard"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=900,
        )
        assert r.returncode == 0, (
            f"harness_is_standard failed (rc={r.returncode}):\n"
            f"STDERR:\n{r.stderr[-1500:]}\n"
            f"STDOUT:\n{r.stdout[-500:]}"
        )
    finally:
        test_file.write_text(backup)


def test_crate_compiles():
    """The ty_python_semantic crate compiles without errors."""
    r = subprocess.run(
        ["cargo", "check", "-p", "ty_python_semantic"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=900,
    )
    assert r.returncode == 0, (
        f"cargo check failed (rc={r.returncode}):\n"
        f"STDERR:\n{r.stderr[-1500:]}"
    )


def test_todo_types():
    """Existing todo_types unit test passes."""
    r = subprocess.run(
        ["cargo", "test", "-p", "ty_python_semantic", "--", "todo_types"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=900,
    )
    assert r.returncode == 0, (
        f"todo_types test failed (rc={r.returncode}):\n"
        f"STDERR:\n{r.stderr[-1500:]}"
    )

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_test_scripts_python():
    """pass_to_pass | CI job 'test scripts' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'python crates/ruff_python_ast/generate.py'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_scripts_python_2():
    """pass_to_pass | CI job 'test scripts' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'python crates/ruff_python_formatter/generate.py'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_scripts_scripts_add_rule_py():
    """pass_to_pass | CI job 'test scripts' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", './scripts/add_rule.py --name DoTheThing --prefix F --code 999 --linter pyflakes'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_scripts_cargo():
    """pass_to_pass | CI job 'test scripts' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'cargo check'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_scripts_scripts_add_plugin_py():
    """pass_to_pass | CI job 'test scripts' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", './scripts/add_plugin.py test --url https://pypi.org/project/-test/0.1.0/ --prefix TST && ./scripts/add_rule.py --name FirstRule --prefix TST --code 001 --linter test'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_scripts_uv():
    """pass_to_pass | CI job 'test scripts' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'uv run --directory=./python/py-fuzzer mypy'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_scripts_uv_2():
    """pass_to_pass | CI job 'test scripts' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'uv run --directory=./python/py-fuzzer ruff format --check'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_scripts_uv_3():
    """pass_to_pass | CI job 'test scripts' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'uv run --directory=./python/py-fuzzer ruff check'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

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
        ["bash", "-lc", 'cargo insta test --all-features --unreferenced reject --test-runner nextest --disable-nextest-doctest'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_cargo_test_run_doctests():
    """pass_to_pass | CI job 'cargo test' → step 'Run doctests'"""
    r = subprocess.run(
        ["bash", "-lc", 'cargo test --doc --all-features'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run doctests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_cargo_test_dogfood_ty_on_py_fuzzer():
    """pass_to_pass | CI job 'cargo test' → step 'Dogfood ty on py-fuzzer'"""
    r = subprocess.run(
        ["bash", "-lc", 'uv run --project=./python/py-fuzzer cargo run -p ty check --project=./python/py-fuzzer'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Dogfood ty on py-fuzzer' failed (returncode={r.returncode}):\n"
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

