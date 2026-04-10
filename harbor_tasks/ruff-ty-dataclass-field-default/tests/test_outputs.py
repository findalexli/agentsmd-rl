"""
Task: ruff-ty-dataclass-field-default
Repo: astral-sh/ruff @ ee9084695ec4d70bc66083ac2b3cf598cc45101a
PR:   24397
"""

import subprocess
import textwrap
from pathlib import Path

REPO = "/workspace/ruff"
TY_BIN = f"{REPO}/target/debug/ty"


def ty_check(source: str, timeout: int = 60) -> subprocess.CompletedProcess:
    """Run ty check on a Python source string."""
    tmp = Path("/tmp/_ty_test_input.py")
    tmp.write_text(textwrap.dedent(source))
    try:
        return subprocess.run(
            [TY_BIN, "check", str(tmp)],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=REPO,
        )
    finally:
        tmp.unlink(missing_ok=True)


def test_field_default_without_specifiers():
    """
    dataclass_transform without field_specifiers treats field() as a default.
    Before fix: A() fails because field(init=False) is wrongly treated as special.
    After fix: A() passes because field(init=False) is treated as a default value.
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
    combined = result.stdout + result.stderr
    assert result.returncode == 0, (
        f"ty check reported errors (should pass after fix):\n{combined}"
    )


def test_field_default_with_other_specifiers():
    """
    dataclass_transform with other field_specifiers still treats field() as default.
    Before fix: C() fails because field(init=False) is wrongly treated as special.
    After fix: C() passes because field(init=False) is treated as a default value.
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


def test_stdlib_dataclass_field_init_false_still_respected():
    """
    stdlib @dataclass should still respect field(init=False) after the fix.
    This test should PASS on both base and fix (B(name=\"foo\") should error).
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
    assert result.returncode != 0, (
        f"ty check should have errored for B(name=\"foo\") but passed:\n{combined}"
    )


def test_named_args_without_specifiers():
    """
    A(name=\"hello\") should work on both base and fix.
    Before fix: A(name=\"hello\") passes (field wrongly treated as special).
    After fix: A(name=\"hello\") passes (field treated as default, name has value).
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
        f"ty check should pass for A(name=\"hello\"):\n{combined}"
    )


def test_cargo_check():
    """ty_python_semantic crate compiles without errors (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "check", "-p", "ty_python_semantic"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"cargo check failed:\n{r.stderr}"


def test_cargo_fmt():
    """Repo code is formatted correctly (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "fmt", "--all", "--check"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"cargo fmt --check failed:\n{r.stderr}"


def test_cargo_clippy_ty_python_semantic():
    """ty_python_semantic passes clippy lints (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "clippy", "-p", "ty_python_semantic", "--all-targets", "--all-features", "--", "-D", "warnings"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"cargo clippy failed:\n{r.stderr[-500:]}"


def test_cargo_doc_ty_python_semantic():
    """ty_python_semantic docs build without warnings (pass_to_pass)."""
    env = {**subprocess.os.environ, "RUSTDOCFLAGS": "-D warnings"}
    r = subprocess.run(
        ["cargo", "doc", "-p", "ty_python_semantic", "--no-deps"],
        capture_output=True,
        text=True,
        timeout=180,
        cwd=REPO,
        env=env,
    )
    assert r.returncode == 0, f"cargo doc failed:\n{r.stderr[-500:]}"


def test_no_unsafe_unwrap_in_changes():
    """No panic!/unreachable!/unwrap() in added code (pass_to_pass)."""
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
        return

    added_lines = [
        l[1:]
        for l in diff.split("\n")
        if l.startswith("+") and not l.startswith("+++")
    ]
    forbidden = [".unwrap()", "panic!(", "unreachable!(",]
    for line in added_lines:
        for f in forbidden:
            assert f not in line, f"Prohibited {f} in added code: {line.strip()}"
