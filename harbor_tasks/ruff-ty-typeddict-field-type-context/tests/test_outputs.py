"""
Task: ruff-ty-typeddict-field-type-context
Repo: ruff @ b6c69c288fe9e5b63d70d1743aabdfa40523e344
PR:   24422

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import os
import subprocess
import tempfile
import textwrap
from pathlib import Path

REPO = "/workspace/ruff"
TYPED_DICT_RS = Path(REPO) / "crates/ty_python_semantic/src/types/typed_dict.rs"
BUILDER_RS = Path(REPO) / "crates/ty_python_semantic/src/types/infer/builder.rs"

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
# Pass-to-pass (repo_tests) — CI/CD checks that must pass on base and after fix
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_build_ty():
    """Repo's ty binary builds successfully (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "build", "--bin", "ty"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"ty build failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_clippy_ty_python_semantic():
    """Repo's clippy checks pass for ty_python_semantic (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "clippy", "-p", "ty_python_semantic", "--", "-D", "warnings"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"clippy failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_fmt_check():
    """Repo's code formatting is valid (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "fmt", "--", "--check"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"fmt check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_ty_check_works():
    """Repo's ty binary can check a simple Python file (pass_to_pass)."""
    # Create a simple test file
    test_code = "x: int = 1\n"
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False, dir="/tmp") as f:
        f.write(test_code)
        tmp = f.name
    try:
        r = subprocess.run(
            [_ty_bin(), "check", tmp],
            capture_output=True, text=True, timeout=30, cwd=REPO,
        )
        assert r.returncode == 0, f"ty check failed:\n{r.stderr[-500:]}"
    finally:
        os.unlink(tmp)


# [repo_tests] pass_to_pass
def test_repo_check_ty_crate():
    """Repo's ty crate compiles without errors (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "check", "--bin", "ty"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"cargo check --bin ty failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_check_ty_python_semantic():
    """Modified crate ty_python_semantic compiles without errors (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "check", "-p", "ty_python_semantic"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"cargo check -p ty_python_semantic failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_typed_dict_mdtest():
    """Repo's mdtest for typed_dict.md passes (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "test", "-p", "ty_python_semantic", "--", "mdtest::typed_dict.md", "--test-threads=1"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"typed_dict mdtest failed:\n{r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_dict_keyword_values_with_type_context():
    """dict() keyword values should be re-inferred with the field's TypedDict type context.

    On the base commit, validate_typed_dict_constructor reads already-inferred types
    without field type context. dict(field="a", value="b") is inferred as a generic
    dict[str, str], not as a Comparison TypedDict. After the fix, keyword values are
    re-inferred with the destination field's declared type as context via speculative
    inference, so dict() calls are recognized as TypedDict constructors.
    """
    code = textwrap.dedent("""\
        from typing import TypedDict

        class Comparison(TypedDict):
            field: str
            value: object

        class Logical(TypedDict):
            primary: Comparison
            conditions: list[Comparison]

        logical = Logical(
            primary=dict(field="a", value="b"),
            conditions=[dict(field="c", value="d")],
        )
    """)
    diags = _ty_diagnostics(code)
    errors = [l for l in diags if "error[" in l]
    assert len(errors) == 0, (
        f"Expected no errors for dict() keyword values with type context, got:\n"
        + "\n".join(errors)
    )

    # Vary field names and types to prevent hardcoding
    code2 = textwrap.dedent("""\
        from typing import TypedDict

        class Address(TypedDict):
            street: str
            zip_code: int

        class Contact(TypedDict):
            name: str
            home: Address
            work: Address

        contact = Contact(
            name="Alice",
            home=dict(street="Main St", zip_code=12345),
            work=dict(street="Oak Ave", zip_code=67890),
        )
    """)
    diags2 = _ty_diagnostics(code2)
    errors2 = [l for l in diags2 if "error[" in l]
    assert len(errors2) == 0, (
        f"Expected no errors for Contact dict() construction, got:\n"
        + "\n".join(errors2)
    )


# [pr_diff] fail_to_pass
def test_dict_call_as_typeddict_positional():
    """dict() call as single positional arg should use TypedDict type context.

    On the base commit, dict() in `Outer(dict(...))` is inferred without the
    target TypedDict type context, so it resolves to a generic dict rather than
    a TypedDict. After the fix, the positional arg gets TypeContext with the
    target TypedDict type, enabling correct inference.
    """
    code = textwrap.dedent("""\
        from typing import TypedDict

        class Comparison(TypedDict):
            field: str
            value: object

        class Logical(TypedDict):
            primary: Comparison
            conditions: list[Comparison]

        logical = Logical(dict(
            primary=dict(field="a", value="b"),
            conditions=[dict(field="c", value="d")],
        ))
    """)
    diags = _ty_diagnostics(code)
    errors = [l for l in diags if "error[" in l]
    assert len(errors) == 0, (
        f"Expected no errors for dict() positional TypedDict construction, got:\n"
        + "\n".join(errors)
    )

    # Different TypedDict structure to prevent hardcoding
    code2 = textwrap.dedent("""\
        from typing import TypedDict

        class Item(TypedDict):
            name: str
            count: int

        class Order(TypedDict):
            customer: str
            item: Item

        order = Order(dict(customer="Bob", item=dict(name="Widget", count=5)))
    """)
    diags2 = _ty_diagnostics(code2)
    errors2 = [l for l in diags2 if "error[" in l]
    assert len(errors2) == 0, (
        f"Expected no errors for Order dict() positional, got:\n"
        + "\n".join(errors2)
    )


# [pr_diff] fail_to_pass
def test_missing_key_detected_via_type_context():
    """After fix, dict() with missing keys should be caught via TypedDict type context.

    On the base commit, dict(field="a") is inferred as dict[str, str] without
    type context, so the missing-typed-dict-key diagnostic is NOT emitted (instead
    a generic type incompatibility may be reported). After the fix, dict(field="a")
    is re-inferred with type context Comparison, producing a missing-typed-dict-key
    diagnostic for the missing 'value' field.
    """
    code = textwrap.dedent("""\
        from typing import TypedDict

        class Comparison(TypedDict):
            field: str
            value: object

        class Logical(TypedDict):
            primary: Comparison
            conditions: list[Comparison]

        missing_key = Logical(
            primary=dict(field="a"),
            conditions=[dict(field="c", value="d")],
        )
    """)
    diags = _ty_diagnostics(code)
    missing = [l for l in diags if "missing-typed-dict-key" in l]
    assert len(missing) >= 1, (
        f"Expected missing-typed-dict-key for dict(field='a') missing 'value', got:\n"
        + "\n".join(diags)
    )

    # Same pattern with different field names
    code2 = textwrap.dedent("""\
        from typing import TypedDict

        class Config(TypedDict):
            host: str
            port: int

        class Env(TypedDict):
            name: str
            config: Config

        incomplete = Env(name="prod", config=dict(host="localhost"))
    """)
    diags2 = _ty_diagnostics(code2)
    missing2 = [l for l in diags2 if "missing-typed-dict-key" in l]
    assert len(missing2) >= 1, (
        f"Expected missing-typed-dict-key for config=dict(host='localhost') missing 'port', got:\n"
        + "\n".join(diags2)
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — existing behavior preserved
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_existing_typeddict_validation():
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

    # Wrong type — should still detect invalid-argument-type
    code_wrong = textwrap.dedent("""\
        from typing import TypedDict

        class Person(TypedDict):
            name: str
            age: int

        Person(name="Alice", age="not_an_int")
    """)
    diags_wrong = _ty_diagnostics(code_wrong)
    invalid = [l for l in diags_wrong if "invalid-argument-type" in l]
    assert len(invalid) >= 1, (
        f"Expected invalid-argument-type for wrong type, got:\n" + "\n".join(diags_wrong)
    )

    # Missing required key — should still detect
    code_missing = textwrap.dedent("""\
        from typing import TypedDict

        class Person(TypedDict):
            name: str
            age: int

        Person(name="Alice")
    """)
    diags_missing = _ty_diagnostics(code_missing)
    missing = [l for l in diags_missing if "missing-typed-dict-key" in l]
    assert len(missing) >= 1, (
        f"Expected missing-typed-dict-key, got:\n" + "\n".join(diags_missing)
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:79 @ b6c69c288fe9e5b63d70d1743aabdfa40523e344
def test_no_panic_unwrap_in_modified_functions():
    """No panic!/unwrap in validate_typed_dict_constructor and related functions (AGENTS.md:79)."""
    target_functions = [
        (TYPED_DICT_RS, "validate_typed_dict_constructor"),
        (TYPED_DICT_RS, "validate_from_dict_literal"),
        (TYPED_DICT_RS, "validate_from_keywords"),
    ]
    for filepath, func_name in target_functions:
        body = _extract_function(filepath, func_name)
        if body is None:
            continue
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


# [agent_config] pass_to_pass — AGENTS.md:76 @ b6c69c288fe9e5b63d70d1743aabdfa40523e344
def test_no_local_imports_in_modified_functions():
    """No local use statements inside TypedDict validation functions (AGENTS.md:76)."""
    target_functions = [
        (TYPED_DICT_RS, "validate_typed_dict_constructor"),
        (TYPED_DICT_RS, "validate_from_dict_literal"),
        (TYPED_DICT_RS, "validate_from_keywords"),
    ]
    for filepath, func_name in target_functions:
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
