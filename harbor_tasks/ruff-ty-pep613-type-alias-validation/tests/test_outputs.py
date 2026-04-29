"""
Task: ruff-ty-pep613-type-alias-validation
Repo: astral-sh/ruff @ 50ee3c2e70ccd8b945b1280cc1a1bf92612744db
PR:   24370

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import os
import subprocess
import tempfile
from pathlib import Path

REPO = "/workspace/ruff"
TYPE_EXPR_RS = Path(REPO) / "crates/ty_python_semantic/src/types/infer/builder/type_expression.rs"
BUILDER_RS = Path(REPO) / "crates/ty_python_semantic/src/types/infer/builder.rs"
POST_INFERENCE_MOD = Path(REPO) / "crates/ty_python_semantic/src/types/infer/builder/post_inference/mod.rs"
PEP613_ALIAS_RS = Path(REPO) / "crates/ty_python_semantic/src/types/infer/builder/post_inference/pep_613_alias.rs"

CARGO_ENV = {**os.environ, "CARGO_PROFILE_DEV_OPT_LEVEL": "1"}


def _run_ty_check(python_code: str, timeout: int = 600) -> subprocess.CompletedProcess:
    """Write a Python snippet to a temp file and run ty check on it."""
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
        f.write(python_code)
        f.flush()
        try:
            r = subprocess.run(
                ["cargo", "run", "--bin", "ty", "--", "check", f.name],
                cwd=REPO,
                capture_output=True,
                text=True,
                timeout=timeout,
                env=CARGO_ENV,
            )
            return r
        finally:
            os.unlink(f.name)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — compilation check
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_compiles():
    """Modified ty_python_semantic crate compiles successfully."""
    r = subprocess.run(
        ["cargo", "check", "-p", "ty_python_semantic"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
        env=CARGO_ENV,
    )
    assert r.returncode == 0, f"Compilation failed:\n{r.stderr}"


# ---------------------------------------------------------------------------
# Repo CI/CD pass_to_pass gates
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_cargo_fmt():
    """Repo code formatting passes cargo fmt check (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "fmt", "--all", "--check"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
        env=CARGO_ENV,
    )
    assert r.returncode == 0, f"cargo fmt check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_cargo_clippy():
    """Repo ty_python_semantic passes cargo clippy (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "clippy", "-p", "ty_python_semantic"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
        env=CARGO_ENV,
    )
    assert r.returncode == 0, f"cargo clippy failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_mdtest_literal():
    """Literal mdtests pass (pass_to_pass) - related to PR."""
    r = subprocess.run(
        ["cargo", "test", "-p", "ty_python_semantic", "--test", "mdtest", "literal"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
        env=CARGO_ENV,
    )
    assert r.returncode == 0, f"mdtest literal failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_mdtest_pep613():
    """PEP 613 type alias mdtests pass (pass_to_pass) - related to PR."""
    r = subprocess.run(
        ["cargo", "test", "-p", "ty_python_semantic", "--test", "mdtest", "pep613"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
        env=CARGO_ENV,
    )
    assert r.returncode == 0, f"mdtest pep613 failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_mdtest_all():
    """Full ty_python_semantic mdtest suite passes (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "test", "-p", "ty_python_semantic", "--test", "mdtest"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
        env=CARGO_ENV,
    )
    assert r.returncode == 0, f"mdtest suite failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_unit_tests():
    """ty_python_semantic library unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "test", "-p", "ty_python_semantic", "--lib"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
        env=CARGO_ENV,
    )
    assert r.returncode == 0, f"Unit tests failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_cargo_doc():
    """ty_python_semantic documentation builds without errors (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "doc", "--no-deps", "-p", "ty_python_semantic"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        env=CARGO_ENV,
    )
    assert r.returncode == 0, f"cargo doc failed:\n{r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_literal_negative_float_invalid():
    """Literal[-3.14] must be flagged as invalid-type-form."""
    code = """from typing import Literal

x: Literal[-3.14]
y: Literal[-2.718]
"""
    r = _run_ty_check(code)
    output = r.stdout + r.stderr
    assert "invalid-type-form" in output, (
        f"Expected invalid-type-form for Literal[-3.14] but got:\n{output[-2000:]}"
    )
    # Both lines should be flagged
    count = output.count("invalid-type-form")
    assert count >= 2, (
        f"Expected at least 2 invalid-type-form errors (for -3.14 and -2.718), got {count}"
    )


# [pr_diff] fail_to_pass
def test_literal_negative_complex_invalid():
    """Literal[-3j] must be flagged as invalid-type-form."""
    code = """from typing import Literal

z: Literal[-3j]
w: Literal[-1.5j]
"""
    r = _run_ty_check(code)
    output = r.stdout + r.stderr
    assert "invalid-type-form" in output, (
        f"Expected invalid-type-form for Literal[-3j] but got:\n{output[-2000:]}"
    )


# [pr_diff] fail_to_pass
def test_type_alias_variable_ref_invalid():
    """TypeAlias = var1 (where var1 is an int) must be flagged as invalid-type-form."""
    code = """from typing_extensions import TypeAlias

var1 = 3
Bad: TypeAlias = var1
"""
    r = _run_ty_check(code)
    output = r.stdout + r.stderr
    assert "invalid-type-form" in output, (
        f"Expected invalid-type-form for TypeAlias = var1 but got:\n{output[-2000:]}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — valid cases must NOT be flagged
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_literal_negative_int_valid():
    """Literal[-3] (integer) must NOT be flagged — negative ints are valid in Literal."""
    code = """from typing import Literal

a: Literal[-3]
b: Literal[-42]
c: Literal[+7]
"""
    r = _run_ty_check(code)
    output = r.stdout + r.stderr
    assert "invalid-type-form" not in output, (
        f"Literal[-3] should be valid but got error:\n{output[-2000:]}"
    )


# [pr_diff] pass_to_pass
def test_valid_type_alias_not_flagged():
    """Valid PEP-613 type aliases must not produce invalid-type-form errors."""
    code = """from typing_extensions import TypeAlias

Good1: TypeAlias = int
Good2: TypeAlias = int | str
Good3: TypeAlias = list[int]
Good4: TypeAlias = tuple[int, str]
"""
    r = _run_ty_check(code)
    output = r.stdout + r.stderr
    assert "invalid-type-form" not in output, (
        f"Valid type aliases should not be flagged:\n{output[-2000:]}"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:79 @ 50ee3c2e70ccd8b945b1280cc1a1bf92612744db
def test_no_panic_unwrap_in_new_module():
    """No panic!/unwrap in the new pep_613_alias module (AGENTS.md:79)."""
    assert PEP613_ALIAS_RS.exists(), "pep_613_alias.rs not found"
    content = PEP613_ALIAS_RS.read_text()
    for i, line in enumerate(content.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("//"):
            continue
        assert "panic!(" not in stripped, f"panic! at line {i}: {stripped}"
        assert ".unwrap()" not in stripped, f".unwrap() at line {i}: {stripped}"
        assert "unreachable!(" not in stripped, f"unreachable! at line {i}: {stripped}"


# [agent_config] pass_to_pass — AGENTS.md:76 @ 50ee3c2e70ccd8b945b1280cc1a1bf92612744db
def test_no_local_imports_in_new_module():
    """Rust imports at top of file, never locally in functions (AGENTS.md:76)."""
    assert PEP613_ALIAS_RS.exists(), "pep_613_alias.rs not found"
    content = PEP613_ALIAS_RS.read_text()
    in_fn = False
    for i, line in enumerate(content.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("pub(crate) fn ") or stripped.startswith("fn "):
            in_fn = True
        if in_fn and stripped.startswith("use "):
            assert False, f"Local import inside function at line {i}: {stripped}"

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

def test_ci_cargo_fuzz_build_cargo():
    """pass_to_pass | CI job 'cargo fuzz build' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'cargo fuzz build -s none'], cwd=REPO,
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

