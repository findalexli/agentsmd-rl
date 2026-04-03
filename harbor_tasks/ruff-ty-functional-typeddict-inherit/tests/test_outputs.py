"""
Task: ruff-ty-functional-typeddict-inherit
Repo: astral-sh/ruff @ 3465d7f1a2ed13c03aeca5f9b2d764b00ab0ab32
PR:   24227

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import os
import subprocess
import tempfile
from pathlib import Path

import pytest

REPO = "/workspace/ruff"
TY_BIN = os.path.join(REPO, "target", "debug", "ty")


@pytest.fixture(scope="session", autouse=True)
def build_ty():
    """Build ty binary once; all tests reuse it."""
    r = subprocess.run(
        ["cargo", "build", "--bin", "ty"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, f"Failed to build ty:\n{r.stderr[-2000:]}"


def _ty_check(code: str, timeout: int = 60) -> str:
    """Write code to a temp file, run ty check, return combined output."""
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
        f.write(code)
        f.flush()
        try:
            r = subprocess.run(
                [TY_BIN, "check", f.name],
                cwd=REPO,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
        finally:
            os.unlink(f.name)
    return r.stdout + r.stderr


def _error_lines(output: str) -> list[str]:
    """Extract error diagnostic lines (excluding reveal_type info lines)."""
    return [
        l for l in output.splitlines()
        if "error" in l.lower() and "revealed" not in l.lower()
    ]


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — compilation check
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_cargo_check():
    """Modified Rust code must compile."""
    r = subprocess.run(
        ["cargo", "check", "-p", "ty_python_semantic", "--quiet"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, f"cargo check failed:\n{r.stderr[-2000:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_functional_typeddict_fields_inherited():
    """Child class inherits fields from functional TypedDict parent."""
    output = _ty_check("""\
from typing import TypedDict

Base = TypedDict("Base", {"a": int}, total=False)

class Child(Base):
    b: str
    c: list[int]

child1 = Child(b="hello", c=[1, 2, 3])
child2 = Child(a=1, b="world", c=[])

reveal_type(child1["a"])
reveal_type(child1["b"])
reveal_type(child1["c"])
""")
    assert output.count("revealed: int") >= 1, f"Missing reveal for 'a' field:\n{output}"
    assert "revealed: str" in output, f"Missing reveal for 'b' field:\n{output}"
    assert "revealed: list[int]" in output, f"Missing reveal for 'c' field:\n{output}"
    errors = _error_lines(output)
    assert len(errors) == 0, f"Unexpected error diagnostics:\n" + "\n".join(errors)


# [pr_diff] fail_to_pass
def test_required_field_enforced_from_functional_parent():
    """Required fields from functional TypedDict parent are enforced in child constructor."""
    # Case 1: missing required field 'x' from functional parent
    output1 = _ty_check("""\
from typing import TypedDict

ReqBase = TypedDict("ReqBase", {"x": int})

class ReqChild(ReqBase):
    y: str

bad = ReqChild(y="hello")
good = ReqChild(x=1, y="hello")
reveal_type(good["x"])
""")
    assert "missing" in output1.lower() or "missing-typed-dict-key" in output1.lower(), \
        f"Expected missing required key error for 'x':\n{output1}"
    assert "revealed: int" in output1, f"reveal_type for good['x'] should be int:\n{output1}"

    # Case 2: missing required field 'b' from child (parent optional, child required)
    output2 = _ty_check("""\
from typing import TypedDict

Base = TypedDict("Base", {"a": int}, total=False)

class Child(Base):
    b: str
    c: list[int]

bad_child1 = Child(c=[1])
bad_child2 = Child(b="test")
""")
    # Both should produce missing-key errors
    missing_count = output2.lower().count("missing")
    assert missing_count >= 2, \
        f"Expected 2 missing-key errors (for 'b' and 'c'), got {missing_count}:\n{output2}"


# [pr_diff] fail_to_pass
def test_functional_subclass_with_not_required():
    """Functional TypedDict subclass with NotRequired qualifier compiles cleanly."""
    output = _ty_check("""\
from typing import TypedDict, NotRequired

MyTD = TypedDict("MyTD", {"x": int})

class SubTD(MyTD):
    y: NotRequired[int]

sub1 = SubTD(x=1)
sub2 = SubTD(x=42, y=99)
reveal_type(sub1["x"])
reveal_type(sub2["y"])
""")
    errors = _error_lines(output)
    assert len(errors) == 0, f"Unexpected errors:\n" + "\n".join(errors)
    assert output.count("revealed: int") >= 2, f"reveal_type should show int:\n{output}"


# [pr_diff] fail_to_pass
def test_total_false_optional_field_accessible():
    """Optional fields from functional parent (total=False) can be provided and typed correctly."""
    output = _ty_check("""\
from typing import TypedDict

OptBase = TypedDict("OptBase", {"a": int, "b": str}, total=False)

class OptChild(OptBase):
    c: float

# All these should be valid — 'a' and 'b' are optional from parent
with_all = OptChild(a=42, b="hi", c=3.14)
with_some = OptChild(a=10, c=2.71)
minimal = OptChild(c=1.0)

reveal_type(with_all["a"])
reveal_type(with_all["b"])
reveal_type(minimal["c"])
""")
    errors = _error_lines(output)
    assert len(errors) == 0, f"Unexpected errors:\n" + "\n".join(errors)
    assert "revealed: int" in output, f"Missing reveal for 'a':\n{output}"
    assert "revealed: str" in output, f"Missing reveal for 'b':\n{output}"
    assert "revealed: float" in output, f"Missing reveal for 'c':\n{output}"


# [pr_diff] fail_to_pass
def test_dataclass_inherits_functional_typeddict():
    """@dataclass on a class inheriting from functional TypedDict triggers invalid-dataclass."""
    output = _ty_check("""\
from dataclasses import dataclass
from typing import TypedDict

@dataclass
class Foo(TypedDict("Foo", {"x": int, "y": str})):
    pass
""")
    assert "invalid-dataclass" in output.lower(), \
        f"Expected invalid-dataclass error:\n{output}"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — regression checks
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_class_based_typeddict_inheritance_baseline():
    """Existing class-based TypedDict inheritance must not regress."""
    output = _ty_check("""\
from typing import TypedDict

class Base(TypedDict):
    a: int

class Child(Base):
    b: str

child = Child(a=1, b="hello")
reveal_type(child["a"])
reveal_type(child["b"])

# Also test multi-level inheritance
class GrandChild(Child):
    c: float

gc = GrandChild(a=2, b="world", c=3.14)
reveal_type(gc["c"])
""")
    errors = _error_lines(output)
    assert len(errors) == 0, f"Class-based inheritance regressed:\n" + "\n".join(errors)


# [repo_tests] pass_to_pass
def test_existing_typed_dict_mdtests():
    """Upstream TypedDict mdtests must still pass."""
    r = subprocess.run(
        ["cargo", "test", "-p", "ty_python_semantic",
         "--", "mdtest::typed_dict", "--no-fail-fast"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
        env={
            **os.environ,
            "CARGO_PROFILE_DEV_OPT_LEVEL": "1",
            "INSTA_FORCE_PASS": "1",
            "INSTA_UPDATE": "always",
        },
    )
    assert r.returncode == 0, f"TypedDict mdtests failed:\n{r.stdout[-2000:]}\n{r.stderr[-2000:]}"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:79 @ 3465d7f1
def test_no_unwrap_in_new_code():
    """No .unwrap() in newly added Rust code (AGENTS.md:79)."""
    r = subprocess.run(
        ["git", "diff", "HEAD", "--", "*.rs"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30,
    )
    added_lines = [l for l in r.stdout.splitlines() if l.startswith("+") and not l.startswith("+++")]
    unwrap_lines = [l for l in added_lines if ".unwrap()" in l]
    assert len(unwrap_lines) == 0, \
        f"Found .unwrap() in new code (AGENTS.md:79 forbids this):\n" + "\n".join(unwrap_lines)


# [agent_config] pass_to_pass — AGENTS.md:76 @ 3465d7f1
def test_no_local_rust_imports():
    """Rust imports must be at the top of the file, not locally in functions (AGENTS.md:76)."""
    import re
    r = subprocess.run(
        ["git", "diff", "HEAD", "--", "*.rs"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30,
    )
    # Look for added lines that are `use` statements inside function bodies
    # (indented use statements indicate local imports)
    added_lines = [l for l in r.stdout.splitlines() if l.startswith("+") and not l.startswith("+++")]
    # Local imports are indented `use` statements (4+ spaces of indentation)
    local_imports = [l for l in added_lines if re.match(r"^\+\s{4,}use\s", l)]
    assert len(local_imports) == 0, \
        f"Found local imports in functions (AGENTS.md:76 requires top-level imports):\n" + "\n".join(local_imports)
