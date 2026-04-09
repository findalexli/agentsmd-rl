"""
Task: ruff-ty-paramspec-concatenate-prefix
Repo: ruff @ 9311680c97e2ab9db027303671d2da9fa4b0de0b
PR:   24474

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import os
import subprocess
import tempfile
from pathlib import Path

REPO = "/workspace/ruff"

SUBSCRIPT_RS = Path(REPO) / "crates/ty_python_semantic/src/types/infer/builder/subscript.rs"
TYPE_EXPR_RS = Path(REPO) / "crates/ty_python_semantic/src/types/infer/builder/type_expression.rs"
TYPEVAR_RS = Path(REPO) / "crates/ty_python_semantic/src/types/infer/builder/typevar.rs"

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


def _ty_check(code: str) -> str:
    """Run ty check on a code snippet, return combined stdout+stderr."""
    with tempfile.NamedTemporaryFile(
        suffix=".py", mode="w", dir="/tmp", delete=False
    ) as f:
        f.write(code)
        tmp = f.name
    try:
        r = subprocess.run(
            [_ty_bin(), "check", tmp],
            capture_output=True,
            text=True,
            timeout=60,
        )
        return r.stdout + r.stderr
    finally:
        os.unlink(tmp)


def _has_invalid_type_form(output: str, paramspec_name: str) -> bool:
    """Check if output contains invalid-type-form error for a specific bare ParamSpec."""
    return (
        "invalid-type-form" in output
        and "Bare ParamSpec" in output
        and f"`{paramspec_name}`" in output
    )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — compilation check
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_cargo_check():
    """ty binary exists (compilation succeeded)."""
    assert Path(_ty_bin()).exists(), "ty binary not found after build"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_paramspec_in_concatenate_prefix_pep695():
    """ty reports error for bare ParamSpec in Concatenate prefix inside subscript (PEP 695)."""
    output = _ty_check(
        """\
from typing import Concatenate, Callable

class Foo[**P]:
    attr: Callable[P, None]

def func[**P2](c: Callable[Concatenate[P2, ...], bool]):
    reveal_type(Foo[Concatenate[P2, ...]].attr)
"""
    )
    # Before fix: P2 is incorrectly accepted as prefix arg in Concatenate inside Foo[...]
    # After fix: invalid-type-form error for bare ParamSpec P2
    assert _has_invalid_type_form(output, "P2"), (
        f"Expected invalid-type-form for bare P2 in Concatenate prefix, got:\n{output}"
    )


# [pr_diff] fail_to_pass
def test_paramspec_in_list_specialization_pep695():
    """ty reports error for bare ParamSpec in list/tuple inside subscript specialization."""
    output = _ty_check(
        """\
from typing import Callable
from typing_extensions import ParamSpec

P = ParamSpec("P")
Q = ParamSpec("Q")

class InvalidSpecializationTarget[**P]:
    attr: Callable[P, None]

def invalid_specialization[**Q](
    a: InvalidSpecializationTarget[[Q]],
    b: InvalidSpecializationTarget[Q,],
) -> None: ...
"""
    )
    # Before fix: bare Q in [Q] and [Q,] inside subscript is incorrectly accepted
    # After fix: invalid-type-form for bare Q
    assert _has_invalid_type_form(output, "Q"), (
        f"Expected invalid-type-form for bare Q in specialization, got:\n{output}"
    )


# [pr_diff] fail_to_pass
def test_paramspec_in_concatenate_prefix_legacy():
    """ty reports error for bare ParamSpec in Concatenate prefix (legacy typing)."""
    output = _ty_check(
        """\
from typing import Callable, Concatenate, Generic, ParamSpec

P = ParamSpec("P")
Q = ParamSpec("Q")

class InvalidSpecializationTarget(Generic[P]):
    attr: Callable[P, None]

def invalid_specialization(
    a: InvalidSpecializationTarget[[Q]],
    b: InvalidSpecializationTarget[Q,],
) -> None: ...
"""
    )
    # Before fix: bare Q in subscript position incorrectly accepted
    # After fix: invalid-type-form for bare Q
    assert _has_invalid_type_form(output, "Q"), (
        f"Expected invalid-type-form for bare Q in legacy specialization, got:\n{output}"
    )


# [pr_diff] fail_to_pass
def test_paramspec_in_default_list():
    """ty reports error for bare ParamSpec in default list for another ParamSpec."""
    output = _ty_check(
        """\
from typing import ParamSpec

Q = ParamSpec("Q")

# Bare Q in default list should be invalid
P5 = ParamSpec("P5", default=[Q])
"""
    )
    # Before fix: bare Q inside [Q] default list is incorrectly accepted
    # After fix: invalid-type-form for bare Q
    assert _has_invalid_type_form(output, "Q"), (
        f"Expected invalid-type-form for bare Q in default list, got:\n{output}"
    )


# [pr_diff] fail_to_pass
def test_paramspec_in_concatenate_nonlast_prefix():
    """ty reports error for bare ParamSpec in non-last position of Concatenate inside subscript."""
    output = _ty_check(
        """\
from typing import Callable, Concatenate

class Foo[**P1]:
    attr: Callable[P1, None]

type Alias[**P1] = int

def func[**P2, **P3](
    x: Foo[Concatenate[P2, P3]],
    y: Alias[Concatenate[P2, P3]],
):
    pass
"""
    )
    # Before fix: bare P2 in Concatenate prefix position inside Foo[...] accepted
    # After fix: invalid-type-form for bare P2 (not last arg of Concatenate)
    assert _has_invalid_type_form(output, "P2"), (
        f"Expected invalid-type-form for bare P2 in Concatenate non-last, got:\n{output}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / repo_tests) — regression + valid cases
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_valid_callable_paramspec():
    """Valid Callable[P, int] still works — no false positive errors."""
    output = _ty_check(
        """\
from typing import Callable, ParamSpec

P = ParamSpec("P")

def valid(
    a1: Callable[P, int],
    a2: Callable["P", int],
) -> None: ...
"""
    )
    # Valid uses of bare ParamSpec as first arg of Callable should NOT error
    assert "invalid-type-form" not in output or "Bare ParamSpec" not in output, (
        f"False positive: valid Callable[P, int] incorrectly flagged:\n{output}"
    )


# [pr_diff] pass_to_pass
def test_valid_concatenate_tail():
    """Valid Concatenate[int, P] still works — no false positive errors."""
    output = _ty_check(
        """\
from typing import Callable, Concatenate, ParamSpec

P = ParamSpec("P")

def valid(c: Callable[Concatenate[int, P], bool]):
    pass
"""
    )
    # Valid Concatenate with ParamSpec as LAST arg should NOT error
    assert "invalid-type-form" not in output or "Bare ParamSpec" not in output, (
        f"False positive: valid Concatenate[int, P] incorrectly flagged:\n{output}"
    )


# [pr_diff] pass_to_pass
def test_valid_pep695_concatenate():
    """Valid PEP 695 Concatenate[int, P] inside subscript still works."""
    output = _ty_check(
        """\
from typing import Callable, Concatenate

class Foo[**P1]:
    attr: Callable[P1, None]

def valid[**P2](c: Callable[Concatenate[int, P2], bool]):
    reveal_type(c)
    reveal_type(Foo[Concatenate[int, P2]].attr)
"""
    )
    # Valid Concatenate with P2 as LAST arg should NOT error
    assert "invalid-type-form" not in output or "Bare ParamSpec" not in output, (
        f"False positive: valid Foo[Concatenate[int, P2]] incorrectly flagged:\n{output}"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:79 @ 9311680c97e2ab9db027303671d2da9fa4b0de0b
def test_no_panic_unwrap():
    """No panic!/unreachable!/unwrap in modified files (AGENTS.md:79)."""
    for filepath in [SUBSCRIPT_RS, TYPE_EXPR_RS, TYPEVAR_RS]:
        source = filepath.read_text()
        for i, line in enumerate(source.splitlines(), 1):
            stripped = line.strip()
            if stripped.startswith("//"):
                continue
            assert "panic!(" not in stripped, (
                f"panic! at {filepath.name}:{i}: {stripped}"
            )
            assert ".unwrap()" not in stripped, (
                f".unwrap() at {filepath.name}:{i}: {stripped}"
            )
            assert "unreachable!(" not in stripped, (
                f"unreachable! at {filepath.name}:{i}: {stripped}"
            )


# [agent_config] pass_to_pass — AGENTS.md:76 @ 9311680c97e2ab9db027303671d2da9fa4b0de0b
def test_no_local_imports():
    """No local use/import statements inside functions (AGENTS.md:76)."""
    for filepath in [SUBSCRIPT_RS, TYPE_EXPR_RS, TYPEVAR_RS]:
        source = filepath.read_text()
        in_fn = False
        brace_depth = 0
        for i, line in enumerate(source.splitlines(), 1):
            stripped = line.strip()
            if stripped.startswith("//"):
                continue
            if "fn " in stripped and "{" in stripped:
                in_fn = True
                brace_depth += stripped.count("{") - stripped.count("}")
                continue
            if in_fn:
                brace_depth += stripped.count("{") - stripped.count("}")
                if brace_depth <= 0:
                    in_fn = False
                    continue
                assert not stripped.startswith("use "), (
                    f"Local import at {filepath.name}:{i}: {stripped}"
                )
