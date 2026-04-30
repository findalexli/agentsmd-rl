"""
Task: ruff-ty-requires-python-lower-bound
Repo: ruff @ af9ae49e84daf09f74e654ba3e6d87fe94f6d1ca
PR:   24401

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import os
import subprocess
import tempfile
from pathlib import Path

import pytest

REPO = "/workspace/ruff"
PYPROJECT_RS = Path(REPO) / "crates/ty_project/src/metadata/pyproject.rs"

_ty_bin_cache = None


def _ty_bin():
    """Find the pre-built ty binary."""
    global _ty_bin_cache
    if _ty_bin_cache is not None:
        return _ty_bin_cache

    for profile in ["debug", "release"]:
        p = Path(REPO) / "target" / profile / "ty"
        if p.exists():
            _ty_bin_cache = str(p)
            return _ty_bin_cache

    raise RuntimeError(
        "ty binary not found — it should be pre-built in the Docker image. "
        "Run 'cargo build --bin ty' in /workspace/ruff."
    )


def _run_ty_check(pyproject_content: str, python_code: str = "x: int = 1\n"):
    """Create a temp project and run ty check, returning CompletedProcess."""
    with tempfile.TemporaryDirectory() as tmpdir:
        pyproject_path = os.path.join(tmpdir, "pyproject.toml")
        with open(pyproject_path, "w") as f:
            f.write(pyproject_content)

        test_py = os.path.join(tmpdir, "test.py")
        with open(test_py, "w") as f:
            f.write(python_code)

        r = subprocess.run(
            [_ty_bin(), "check", test_py],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=tmpdir,
        )
        return r


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_ty_binary_exists():
    """ty binary was built successfully during Docker build."""
    ty = Path(_ty_bin())
    assert ty.exists(), f"ty binary not found at {ty}"
    assert os.access(ty, os.X_OK), f"ty binary not executable at {ty}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_requires_python_27_no_panic():
    """ty handles requires-python='==2.7' gracefully instead of panicking.

    Before the fix, ty would try to use PythonVersion(2, 7) directly,
    causing panics downstream. After the fix, it finds the first supported
    version >= 2.7 (i.e., 3.7).
    """
    r = _run_ty_check(
        pyproject_content='[project]\nrequires-python = "==2.7"\n',
    )
    output = r.stdout + r.stderr
    # Rust panic exit code is 101; normal error exit codes are 1-2
    assert r.returncode != 101, f"ty panicked with exit 101:\n{output}"
    assert "panic" not in output.lower(), (
        f"ty panicked (panic message in output):\n{output}"
    )


# [pr_diff] fail_to_pass
def test_requires_python_future_version_error():
    """ty gives a clear error for requires-python with an unsupported future version.

    Before the fix, requires-python='==44.44' would cause a panic or
    unexpected behavior. After the fix, it returns a proper error message.
    """
    r = _run_ty_check(
        pyproject_content='[project]\nrequires-python = "==44.44"\n',
    )
    output = r.stdout + r.stderr
    # Should fail (non-zero) but NOT panic
    assert r.returncode != 0, (
        f"ty should reject unsupported requires-python '==44.44':\n{output}"
    )
    assert "panic" not in output.lower(), (
        f"ty panicked instead of giving a clean error:\n{output}"
    )
    # Should mention that no supported version is included
    assert "supported" in output.lower() or "does not include" in output.lower(), (
        f"Expected error about unsupported version, got:\n{output}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression + valid cases
# ---------------------------------------------------------------------------


# [pr_diff] pass_to_pass
def test_requires_python_normal_version():
    """ty works normally with a standard requires-python specifier."""
    r = _run_ty_check(
        pyproject_content='[project]\nrequires-python = ">=3.10"\n',
        python_code="x: int = 1\nprint(x)\n",
    )
    output = r.stdout + r.stderr
    assert "panic" not in output.lower(), f"ty panicked:\n{output}"
    assert "Invalid" not in output or "requires-python" not in output, (
        f"ty reported requires-python error for valid specifier:\n{output}"
    )


# [pr_diff] pass_to_pass
def test_requires_python_310_exact():
    """ty works with exact-version requires-python for a supported version."""
    r = _run_ty_check(
        pyproject_content='[project]\nrequires-python = "==3.10"\n',
        python_code="from typing import TypeAlias\nMyInt: TypeAlias = int\n",
    )
    output = r.stdout + r.stderr
    assert "panic" not in output.lower(), f"ty panicked:\n{output}"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------


# [agent_config] pass_to_pass — AGENTS.md:79 @ af9ae49e84daf09f74e654ba3e6d87fe94f6d1ca
def test_no_unwrap_in_resolve_requires_python():
    """resolve_requires_python avoids .unwrap() and panic! per AGENTS.md guidelines.

    AGENTS.md says: 'Try hard to avoid patterns that require panic!,
    unreachable!, or .unwrap().'
    """
    source = PYPROJECT_RS.read_text()
    marker = "fn resolve_requires_python"
    start = source.find(marker)
    assert start != -1, f"Function resolve_requires_python not found in {PYPROJECT_RS}"

    # Find the function body by tracking brace depth
    rest = source[start:]
    depth = 0
    end = 0
    for i, ch in enumerate(rest):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    func_body = rest[:end]

    for i, line in enumerate(func_body.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("//"):
            continue
        assert ".unwrap()" not in stripped, (
            f".unwrap() found in resolve_requires_python at line {i}: {stripped}"
        )
        assert "panic!(" not in stripped, (
            f"panic! found in resolve_requires_python at line {i}: {stripped}"
        )
        assert "unreachable!(" not in stripped, (
            f"unreachable! found in resolve_requires_python at line {i}: {stripped}"
        )


# [agent_config] pass_to_pass — AGENTS.md:76 @ af9ae49e84daf09f74e654ba3e6d87fe94f6d1ca
def test_no_local_imports_in_resolve():
    """No local use/import statements inside functions (AGENTS.md:76).

    AGENTS.md says: 'Rust imports should always go at the top of the file,
    never locally in functions.'
    """
    source = PYPROJECT_RS.read_text()
    marker = "fn resolve_requires_python"
    start = source.find(marker)
    assert start != -1, f"Function resolve_requires_python not found in {PYPROJECT_RS}"

    rest = source[start:]
    depth = 0
    end = 0
    for i, ch in enumerate(rest):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    func_body = rest[:end]

    for i, line in enumerate(func_body.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("//"):
            continue
        assert not stripped.startswith("use "), (
            f"Local import in resolve_requires_python at line {i}: {stripped}"
        )


# ---------------------------------------------------------------------------
# Repo CI/CD pass_to_pass gates
# ---------------------------------------------------------------------------

# NOTE: These are lightweight CI commands that work within container constraints:
# - cargo fmt --check: Validates code formatting
# - cargo check -p ty_project: Type-checks the modified crate
# - cargo clippy -p ty_project: Runs clippy lints on the modified crate
#
# Heavier tests (cargo test -p ty_project) are skipped due to disk space limits.


# [repo_tests] pass_to_pass
def test_repo_cargo_fmt():
    """cargo fmt --check passes (repo CI pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "fmt", "--check"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert r.returncode == 0, f"cargo fmt --check failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_cargo_check_ty_project():
    """cargo check -p ty_project passes (repo CI pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "check", "-p", "ty_project"],
        capture_output=True,
        text=True,
        timeout=600,
        cwd=REPO,
    )
    assert r.returncode == 0, f"cargo check -p ty_project failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_cargo_clippy_ty_project():
    """cargo clippy -p ty_project --all-targets --all-features passes (repo CI pass_to_pass)."""
    skip_tests = os.environ.get("SKIP", "").split(",")
    if "repo_cargo_clippy" in skip_tests or "repo_cargo_clippy_ty_project" in skip_tests:
        pytest.skip("Skipped due to SKIP environment variable")

    r = subprocess.run(
        ["cargo", "clippy", "-p", "ty_project", "--all-targets", "--all-features"],
        capture_output=True,
        text=True,
        timeout=600,
        cwd=REPO,
    )
    assert r.returncode == 0, f"cargo clippy -p ty_project failed:\n{r.stderr[-500:]}"

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_cargo_fuzz_build_cargo():
    """pass_to_pass | CI job 'cargo fuzz build' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'cargo fuzz build -s none'], cwd=REPO,
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

def test_ci_benchmarks_walltime_build_benchmarks():
    """pass_to_pass | CI job 'benchmarks walltime' → step 'Build benchmarks'"""
    r = subprocess.run(
        ["bash", "-lc", 'cargo codspeed build -m walltime --features "codspeed,ty_walltime" --profile profiling --no-default-features -p ruff_benchmark'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build benchmarks' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_benchmarks_instrumented_ty_build_benchmarks():
    """pass_to_pass | CI job 'benchmarks instrumented ty' → step 'Build benchmarks'"""
    r = subprocess.run(
        ["bash", "-lc", 'cargo codspeed build -m simulation -m memory --features "codspeed,ty_instrumented" --profile profiling --no-default-features -p ruff_benchmark --bench ty'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build benchmarks' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_scripts_python():
    """pass_to_pass | CI job 'test scripts' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'python crates/ruff_python_ast/generate.py'], cwd=REPO,
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

