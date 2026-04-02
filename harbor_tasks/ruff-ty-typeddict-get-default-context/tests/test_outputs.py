"""
Task: ruff-ty-typeddict-get-default-context
Repo: astral-sh/ruff @ c37535dd792bf8a46fb0be1b6a70a6483d0c6833
PR:   #24231

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
import tempfile
from pathlib import Path

REPO = "/workspace/ruff"
TYPED_DICT_RS = "crates/ty_python_semantic/src/types/class/typed_dict.rs"


def _build_ty():
    """Build the ty binary (incremental, should be fast)."""
    r = subprocess.run(
        ["cargo", "build", "--bin", "ty", "--quiet"],
        cwd=REPO, capture_output=True, timeout=600,
    )
    assert r.returncode == 0, f"Failed to build ty:\n{r.stderr.decode()[-2000:]}"
    return str(Path(REPO) / "target/debug/ty")


def _ty_check(code: str) -> subprocess.CompletedProcess:
    """Write code to a temp file and run ty check on it."""
    ty = _build_ty()
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
        f.write(code)
        f.flush()
        return subprocess.run(
            [ty, "check", f.name],
            capture_output=True, timeout=120, text=True,
        )


def _has_type_error(result: subprocess.CompletedProcess) -> bool:
    """Check if ty reported a type error."""
    combined = result.stdout + result.stderr
    return any(kw in combined.lower() for kw in ["invalid-argument", "invalid-assignment", "error"])


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) -- compilation check
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_cargo_check():
    """ty_python_semantic crate must compile."""
    r = subprocess.run(
        ["cargo", "check", "-p", "ty_python_semantic", "--quiet"],
        cwd=REPO, capture_output=True, timeout=600,
    )
    assert r.returncode == 0, f"cargo check failed:\n{r.stderr.decode()[-2000:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) -- core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_get_nonrequired_dict_default():
    """payload.get("resolved", {}) on non-required TypedDict field infers field type, not union."""
    result = _ty_check("""\
from typing import TypedDict

class ResolvedData(TypedDict, total=False):
    x: int

class Payload(TypedDict, total=False):
    resolved: ResolvedData

def takes_resolved(value: ResolvedData) -> None: ...

def f(payload: Payload) -> None:
    result = payload.get("resolved", {})
    takes_resolved(result)
""")
    assert not _has_type_error(result), (
        f"ty incorrectly reports error for .get() with dict default on non-required field:\n"
        f"{result.stdout}\n{result.stderr}"
    )


# [pr_diff] fail_to_pass
def test_get_union_typeddict_dict_default():
    """Union[Payload, Payload2].get("resolved", {}) also infers field type correctly."""
    result = _ty_check("""\
from typing import TypedDict

class ResolvedData(TypedDict, total=False):
    x: int

class Payload(TypedDict, total=False):
    resolved: ResolvedData

class Payload2(TypedDict, total=False):
    resolved: ResolvedData

def takes_resolved(value: ResolvedData) -> None: ...

def f(payload: Payload | Payload2) -> None:
    result = payload.get("resolved", {})
    takes_resolved(result)
""")
    assert not _has_type_error(result), (
        f"ty incorrectly reports error for union TypedDict .get() with dict default:\n"
        f"{result.stdout}\n{result.stderr}"
    )


# [pr_diff] fail_to_pass
def test_get_nonrequired_list_default():
    """cfg.get("tags", []) on non-required list[str] field infers list[str], not union."""
    result = _ty_check("""\
from typing import TypedDict

class Config(TypedDict, total=False):
    tags: list[str]

def takes_tags(value: list[str]) -> None: ...

def f(cfg: Config) -> None:
    result = cfg.get("tags", [])
    takes_tags(result)
""")
    assert not _has_type_error(result), (
        f"ty incorrectly reports error for .get() with list default on non-required field:\n"
        f"{result.stdout}\n{result.stderr}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass -- regression / negative tests
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_wrong_default_type_still_errors():
    """payload.get("resolved", 42) with incompatible default should still produce error."""
    result = _ty_check("""\
from typing import TypedDict

class ResolvedData(TypedDict, total=False):
    x: int

class Payload(TypedDict, total=False):
    resolved: ResolvedData

def takes_resolved(value: ResolvedData) -> None: ...

def f(payload: Payload) -> None:
    result = payload.get("resolved", 42)
    takes_resolved(result)
""")
    assert _has_type_error(result), (
        "ty should report error when passing int default where ResolvedData expected"
    )


# [pr_diff] pass_to_pass
def test_wrong_assignment_still_errors():
    """d.get("x", 0) assigned to str should still produce a type error."""
    result = _ty_check("""\
from typing import TypedDict

class Data(TypedDict, total=False):
    x: int

def f(d: Data) -> None:
    val: str = d.get("x", 0)
""")
    assert _has_type_error(result), (
        "ty should report error when assigning int to str"
    )


# [pr_diff] pass_to_pass
def test_required_field_get_with_default():
    """Required field .get() with non-matching default still works (union type)."""
    result = _ty_check("""\
from typing import TypedDict

class Person(TypedDict):
    name: str
    age: int

def f(p: Person) -> None:
    val: str | int = p.get("name", 0)
""")
    assert not _has_type_error(result), (
        f"Required field .get() with default regressed:\n{result.stdout}\n{result.stderr}"
    )


# [pr_diff] pass_to_pass
def test_nonrequired_get_no_default_returns_optional():
    """Non-required field .get() without default returns Optional type."""
    result = _ty_check("""\
from typing import TypedDict

class Data(TypedDict, total=False):
    x: int

def f(d: Data) -> None:
    val: int | None = d.get("x")
""")
    assert not _has_type_error(result), (
        f"Non-required .get() without default regressed:\n{result.stdout}\n{result.stderr}"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) -- rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass -- AGENTS.md:79 @ c37535dd792bf8a46fb0be1b6a70a6483d0c6833
def test_no_new_panic_patterns():
    """No new .unwrap(), panic!(), or unreachable!() calls in typed_dict.rs.
    AGENTS.md:79: 'Try hard to avoid patterns that require panic!, unreachable!, or .unwrap().'
    """
    td_file = Path(REPO) / TYPED_DICT_RS
    if not td_file.exists():
        return  # file not found, skip (fix may be in different file)

    current_text = td_file.read_text()
    base_result = subprocess.run(
        ["git", "show", f"HEAD:{TYPED_DICT_RS}"],
        cwd=REPO, capture_output=True, text=True,
    )
    base_text = base_result.stdout if base_result.returncode == 0 else ""

    for pattern in [".unwrap()", "panic!(", "unreachable!("]:
        current_count = current_text.count(pattern)
        base_count = base_text.count(pattern)
        assert current_count <= base_count, (
            f"New {pattern} added to typed_dict.rs: {base_count} -> {current_count}"
        )


# [agent_config] pass_to_pass -- AGENTS.md:76 @ c37535dd792bf8a46fb0be1b6a70a6483d0c6833
def test_no_local_rust_imports():
    """No new `use` statements inside function bodies in typed_dict.rs.
    AGENTS.md:76: 'Rust imports should always go at the top of the file, never locally in functions.'
    """
    td_file = Path(REPO) / TYPED_DICT_RS
    if not td_file.exists():
        return

    current_text = td_file.read_text()
    base_result = subprocess.run(
        ["git", "show", f"HEAD:{TYPED_DICT_RS}"],
        cwd=REPO, capture_output=True, text=True,
    )
    base_text = base_result.stdout if base_result.returncode == 0 else ""

    # Count `use` statements with leading whitespace (inside blocks, not top-level)
    local_use_re = re.compile(r"^    +use ", re.MULTILINE)
    current_local = len(local_use_re.findall(current_text))
    base_local = len(local_use_re.findall(base_text))
    assert current_local <= base_local, (
        f"New local `use` imports added inside function bodies in typed_dict.rs: "
        f"{base_local} -> {current_local}"
    )
