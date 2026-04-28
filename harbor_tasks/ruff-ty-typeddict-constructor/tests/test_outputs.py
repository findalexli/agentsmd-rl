"""
Task: ruff-ty-typeddict-constructor
Repo: ruff @ 6ad36f8be239475137b5cccf5e8463adb4639418
PR:   24480

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import os
import subprocess
import tempfile
import textwrap
from pathlib import Path

REPO = "/workspace/ruff"
BUILDER_RS = Path(REPO) / "crates/ty_python_semantic/src/types/infer/builder.rs"
TYPED_DICT_RS = Path(REPO) / "crates/ty_python_semantic/src/types/typed_dict.rs"

_ty_bin_cache = None


def _ty_bin():
    """Find the pre-built ty binary (built in Dockerfile or by solve.sh)."""
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


def _ty_diagnostics(code: str) -> list[str]:
    """Run ty check on a Python snippet, return all output lines."""
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False, dir="/tmp") as f:
        f.write(code)
        tmp = f.name
    try:
        r = subprocess.run(
            [_ty_bin(), "check", tmp],
            capture_output=True, text=True, timeout=60,
        )
        output = r.stdout + "\n" + r.stderr
        return [l for l in output.splitlines() if l.strip()]
    finally:
        os.unlink(tmp)


def _extract_function(filepath, func_name):
    """Extract a Rust function body by matching 'fn func_name' and counting braces."""
    source = filepath.read_text()
    pattern = f"fn {func_name}"
    start = source.find(pattern)
    if start == -1:
        return None
    brace_pos = source.find("{", start)
    if brace_pos == -1:
        return None
    depth = 0
    for i in range(brace_pos, len(source)):
        if source[i] == "{":
            depth += 1
        elif source[i] == "}":
            depth -= 1
            if depth == 0:
                return source[start:i + 1]
    return None


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_compiles():
    """ty binary exists and is executable."""
    p = Path(_ty_bin())
    assert p.exists(), f"ty binary not found at {p}"
    r = subprocess.run([str(p), "--version"], capture_output=True, timeout=10)
    assert r.returncode == 0, f"ty --version failed: {r.stderr.decode()}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_no_duplicate_diagnostics():
    """TypedDict constructor should not emit duplicate diagnostics for errors.

    On the base commit, speculative inference causes unresolved-reference
    to be emitted twice for TD(x=missing). After the fix, exactly one
    diagnostic should be emitted.
    """
    code = textwrap.dedent("""\
        from typing import TypedDict

        class TD(TypedDict):
            x: int

        TD(x=missing)
    """)
    diags = _ty_diagnostics(code)
    unresolved = [l for l in diags if "unresolved-reference" in l]
    assert len(unresolved) == 1, (
        f"Expected exactly 1 unresolved-reference diagnostic, got {len(unresolved)}:\n"
        + "\n".join(unresolved)
    )

    # Verify with a different undefined name to prevent hardcoding
    code2 = textwrap.dedent("""\
        from typing import TypedDict

        class Record(TypedDict):
            name: str

        Record(name=nonexistent_var)
    """)
    diags2 = _ty_diagnostics(code2)
    unresolved2 = [l for l in diags2 if "unresolved-reference" in l]
    assert len(unresolved2) == 1, (
        f"Expected exactly 1 unresolved-reference for nonexistent_var, got {len(unresolved2)}:\n"
        + "\n".join(unresolved2)
    )


# [pr_diff] fail_to_pass
def test_constant_key_in_dict_literal():
    """TypedDict constructor should accept Final string constants as dict literal keys.

    On the base commit, only ast::ExprStringLiteral keys are recognized.
    After the fix, expression_type_fn resolves constants to their string values.
    """
    code = textwrap.dedent("""\
        from typing import Final, TypedDict

        VALUE_KEY: Final = "value"

        class Record(TypedDict):
            value: str

        Record({VALUE_KEY: "hello"})
    """)
    diags = _ty_diagnostics(code)
    errors = [l for l in diags if "error[" in l]
    assert len(errors) == 0, (
        f"Expected no errors for constant key dict literal, got:\n" + "\n".join(errors)
    )

    # Different constant name and value to prevent hardcoding
    code2 = textwrap.dedent("""\
        from typing import Final, TypedDict

        NAME_KEY: Final = "name"

        class Person(TypedDict):
            name: str

        Person({NAME_KEY: "Alice"})
    """)
    diags2 = _ty_diagnostics(code2)
    errors2 = [l for l in diags2 if "error[" in l]
    assert len(errors2) == 0, (
        f"Expected no errors for Person constant key, got:\n" + "\n".join(errors2)
    )


# [pr_diff] fail_to_pass
def test_mixed_dict_keyword_valid():
    """TypedDict constructor with mixed dict literal + keyword args should validate both.

    On the base commit, keyword arguments in mixed calls are not validated
    and their keys are not counted as provided, causing false missing-key errors.
    """
    code = textwrap.dedent("""\
        from typing import TypedDict

        class TD(TypedDict):
            x: int
            y: str

        TD({"x": 1}, y="bar")
    """)
    diags = _ty_diagnostics(code)
    errors = [l for l in diags if "error[" in l]
    assert len(errors) == 0, (
        f"Expected no errors for valid mixed dict+keyword call, got:\n" + "\n".join(errors)
    )

    # Different field types to prevent hardcoding
    code2 = textwrap.dedent("""\
        from typing import TypedDict

        class Config(TypedDict):
            host: str
            port: int

        Config({"host": "localhost"}, port=8080)
    """)
    diags2 = _ty_diagnostics(code2)
    errors2 = [l for l in diags2 if "error[" in l]
    assert len(errors2) == 0, (
        f"Expected no errors for valid Config mixed call, got:\n" + "\n".join(errors2)
    )


# [pr_diff] fail_to_pass
def test_constant_key_type_error():
    """TypedDict constructor should detect type errors through string constant keys.

    On the base commit, constant keys are not resolved, so type mismatches
    are not detected through the constant. After the fix, the constant is
    resolved and the type mismatch is correctly flagged as invalid-argument-type.
    """
    code = textwrap.dedent("""\
        from typing import Final, TypedDict

        VALUE_KEY: Final = "value"

        class Record(TypedDict):
            value: str
            count: int

        Record({VALUE_KEY: 1}, count=1)
    """)
    diags = _ty_diagnostics(code)
    invalid_arg = [l for l in diags if "invalid-argument-type" in l]
    assert len(invalid_arg) >= 1, (
        f"Expected invalid-argument-type for int vs str through constant key, got:\n"
        + "\n".join(diags)
    )

    # Verify a different constant resolves correctly too
    code2 = textwrap.dedent("""\
        from typing import Final, TypedDict

        AGE_KEY: Final = "age"

        class Person(TypedDict):
            name: str
            age: int

        Person({AGE_KEY: "not_an_int"}, name="Alice")
    """)
    diags2 = _ty_diagnostics(code2)
    invalid_arg2 = [l for l in diags2 if "invalid-argument-type" in l]
    assert len(invalid_arg2) >= 1, (
        f"Expected invalid-argument-type for str vs int through AGE_KEY, got:\n"
        + "\n".join(diags2)
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — existing behavior preserved
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_existing_typed_dict_behavior():
    """Basic TypedDict constructor validation still works correctly."""
    # Valid construction — no errors expected
    code_valid = textwrap.dedent("""\
        from typing import TypedDict

        class Person(TypedDict):
            name: str
            age: int

        Person(name="Alice", age=30)
    """)
    diags = _ty_diagnostics(code_valid)
    errors = [l for l in diags if "error[" in l]
    assert len(errors) == 0, f"Valid TypedDict call should have no errors:\n" + "\n".join(errors)

    # Wrong type — should detect invalid-argument-type
    code_wrong_type = textwrap.dedent("""\
        from typing import TypedDict

        class Person(TypedDict):
            name: str
            age: int

        Person(name="Alice", age="not_an_int")
    """)
    diags_wrong = _ty_diagnostics(code_wrong_type)
    invalid = [l for l in diags_wrong if "invalid-argument-type" in l]
    assert len(invalid) >= 1, (
        f"Expected invalid-argument-type for wrong type, got:\n" + "\n".join(diags_wrong)
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — repo CI/CD tests
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass — cargo clippy with warnings as errors
def test_repo_clippy_ty_python_semantic():
    """Repo's clippy linting passes for ty_python_semantic (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "clippy", "-p", "ty_python_semantic", "--", "-D", "warnings"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"Clippy failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — cargo fmt
def test_repo_fmt_ty_python_semantic():
    """Repo's formatting check passes for ty_python_semantic (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "fmt", "--check", "-p", "ty_python_semantic"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Format check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — cargo check
def test_repo_check_ty_python_semantic():
    """Repo's type check passes for ty_python_semantic (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "check", "-p", "ty_python_semantic", "--all-targets"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"Cargo check failed:\n{r.stderr[-500:]}"



# [repo_tests] pass_to_pass — cargo doc
def test_repo_doc_ty_python_semantic():
    """Repo's documentation builds without warnings for ty_python_semantic (pass_to_pass)."""
    env = os.environ.copy()
    env["RUSTDOCFLAGS"] = "-D warnings"
    r = subprocess.run(
        ["cargo", "doc", "--no-deps", "-p", "ty_python_semantic"],
        capture_output=True, text=True, timeout=180, cwd=REPO, env=env,
    )
    assert r.returncode == 0, f"Documentation build failed:\n{r.stderr[-500:]}"

# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:79 @ 6ad36f8be239475137b5cccf5e8463adb4639418
def test_no_panic_unwrap_in_modified_functions():
    """No panic!/unwrap in TypedDict constructor inference functions (AGENTS.md:79)."""
    new_functions = [
        (BUILDER_RS, "get_or_infer_expression"),
        (BUILDER_RS, "infer_typed_dict_constructor_values"),
        (BUILDER_RS, "infer_typed_dict_constructor_dict_literal_values"),
    ]
    for filepath, func_name in new_functions:
        body = _extract_function(filepath, func_name)
        if body is None:
            continue  # Function may not exist on base commit
        for i, line in enumerate(body.splitlines(), 1):
            stripped = line.strip()
            if stripped.startswith("//"):
                continue
            assert "panic!(" not in stripped, (
                f"panic! in {func_name} line {i}: {stripped}"
            )
            assert ".unwrap()" not in stripped, (
                f".unwrap() in {func_name} line {i}: {stripped}"
            )


# [agent_config] pass_to_pass — AGENTS.md:76 @ 6ad36f8be239475137b5cccf5e8463adb4639418
def test_no_local_imports_in_modified_functions():
    """No local use statements inside TypedDict functions (AGENTS.md:76)."""
    new_functions = [
        (BUILDER_RS, "get_or_infer_expression"),
        (BUILDER_RS, "infer_typed_dict_constructor_values"),
        (BUILDER_RS, "infer_typed_dict_constructor_dict_literal_values"),
    ]
    for filepath, func_name in new_functions:
        body = _extract_function(filepath, func_name)
        if body is None:
            continue
        for i, line in enumerate(body.splitlines(), 1):
            stripped = line.strip()
            if stripped.startswith("//"):
                continue
            assert not stripped.startswith("use "), (
                f"Local import in {func_name} line {i}: {stripped}"
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