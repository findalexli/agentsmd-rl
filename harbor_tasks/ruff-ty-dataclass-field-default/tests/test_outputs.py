"""
Task: ruff-ty-dataclass-field-default
Repo: astral-sh/ruff @ ee9084695ec4d70bc66083ac2b3cf598cc45101a
PR:   24397

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import textwrap
from pathlib import Path

import pytest

REPO = "/workspace/ruff"
TY_BIN = f"{REPO}/target/debug/ty"


def ty_check(source: str) -> subprocess.CompletedProcess:
    """Write source to a temp file, run `ty check`, return the result."""
    tmp = Path("/tmp/_ty_test_input.py")
    tmp.write_text(textwrap.dedent(source))
    return subprocess.run(
        [TY_BIN, "check", str(tmp)],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_field_default_without_specifiers():
    """dataclass_transform without field_specifiers: field(init=False) is a default value.

    When a class uses @dataclass_transform() without specifying field_specifiers,
    dataclasses.field() should NOT be treated as a special field specifier.
    The expression `field(init=False)` should be treated as an ordinary default value,
    so calling A() without arguments should NOT produce a type error.
    """
    result = ty_check(
        """\
        from typing_extensions import dataclass_transform
        from dataclasses import field

        @dataclass_transform()
        def create_model(*, init: bool = True):
            def deco(cls):
                return cls
            return deco

        @create_model()
        class A:
            name: str = field(init=False)

        a1 = A()
        a2 = A(name="hello")
        """
    )
    # On the base commit, A() errors because name is (wrongly) required.
    # On the fix, A() is fine because name has a default.
    combined = result.stdout + result.stderr
    assert result.returncode == 0, (
        f"ty check reported errors (should pass after fix):\n{combined}"
    )


# [pr_diff] fail_to_pass
def test_field_default_with_other_specifiers():
    """dataclass_transform with different field_specifiers: field() is still a default.

    When a class uses @dataclass_transform(field_specifiers=(other_field,)) where
    dataclasses.field is NOT listed, field(init=False) should be treated as a regular
    default value, not a special field specifier.
    """
    result = ty_check(
        """\
        from typing_extensions import dataclass_transform
        from dataclasses import field
        from typing import Any

        class OtherFieldInfo:
            def __init__(self, default: Any = None, **kwargs: Any) -> None: ...

        def other_field(default: Any = None, **kwargs: Any) -> OtherFieldInfo:
            return OtherFieldInfo(default=default, **kwargs)

        @dataclass_transform(field_specifiers=(other_field, OtherFieldInfo))
        def create_model_other(*, init: bool = True):
            def deco(cls):
                return cls
            return deco

        @create_model_other()
        class C:
            name: str = field(init=False)

        c1 = C()
        c2 = C(name="world")
        """
    )
    combined = result.stdout + result.stderr
    assert result.returncode == 0, (
        f"ty check reported errors (should pass after fix):\n{combined}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression checks
# ---------------------------------------------------------------------------


# [repo_tests] pass_to_pass
def test_stdlib_dataclass_field_init_false_still_respected():
    """stdlib @dataclass still respects field(init=False) as a field specifier.

    The fix should NOT change behavior for the stdlib @dataclass decorator,
    which has dataclasses.field in its field_specifiers. B(name="foo") should
    still produce an error since field(init=False) removes name from __init__.
    """
    result = ty_check(
        """\
        from dataclasses import dataclass, field

        @dataclass
        class B:
            name: str = field(init=False)

        b = B(name="foo")
        """
    )
    combined = result.stdout + result.stderr
    # Should error: name is not an __init__ parameter (init=False)
    assert result.returncode != 0, (
        f"ty check should have errored for B(name='foo') but passed:\n{combined}"
    )


# [repo_tests] pass_to_pass
def test_named_args_without_specifiers():
    """Calling A(name=value) should work on both base and fix.

    With @dataclass_transform() (no field_specifiers), passing name as a
    keyword argument should always work regardless of the fix.
    """
    result = ty_check(
        """\
        from typing_extensions import dataclass_transform
        from dataclasses import field

        @dataclass_transform()
        def create_model(*, init: bool = True):
            def deco(cls):
                return cls
            return deco

        @create_model()
        class A:
            name: str = field(init=False)

        a = A(name="hello")
        """
    )
    combined = result.stdout + result.stderr
    assert result.returncode == 0, (
        f"ty check should pass for A(name='hello'):\n{combined}"
    )


# [static] pass_to_pass
def test_cargo_check():
    """ty_python_semantic crate compiles without errors after the fix."""
    r = subprocess.run(
        ["cargo", "check", "-p", "ty_python_semantic"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"cargo check failed:\n{r.stderr}"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------


# [agent_config] pass_to_pass — AGENTS.md:79 @ ee9084695ec4d70bc66083ac2b3cf598cc45101a
def test_no_unsafe_unwrap_in_changes():
    """Avoid panic!/unreachable!/unwrap() in new code (AGENTS.md:79)."""
    result = subprocess.run(
        ["git", "diff", "HEAD"],
        capture_output=True,
        text=True,
        cwd=REPO,
    )
    diff = result.stdout
    if not diff:
        result = subprocess.run(
            ["git", "diff", "--cached"],
            capture_output=True,
            text=True,
            cwd=REPO,
        )
        diff = result.stdout
    if not diff:
        return  # No changes = no violations possible

    added_lines = [
        l[1:]
        for l in diff.split("\n")
        if l.startswith("+") and not l.startswith("+++")
    ]
    forbidden = [".unwrap()", "panic!(", "unreachable!("]
    for line in added_lines:
        for f in forbidden:
            assert f not in line, f"Prohibited {f} in added code: {line.strip()}"
