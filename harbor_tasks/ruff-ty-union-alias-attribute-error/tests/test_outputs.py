"""
Task: ruff-ty-union-alias-attribute-error
Repo: astral-sh/ruff @ 6e76b4cd8a27c2b22263204b83372c4f3720bf79
PR:   24263

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import subprocess
import tempfile
import textwrap
from pathlib import Path

REPO = "/repo"


def _ty_bin() -> str:
    """Return path to the ty binary."""
    try:
        r = subprocess.run(
            ["cargo", "metadata", "--format-version=1", "--no-deps"],
            cwd=REPO, capture_output=True, timeout=30,
        )
        if r.returncode == 0:
            target_dir = json.loads(r.stdout)["target_directory"]
            candidate = Path(target_dir) / "debug" / "ty"
            if candidate.is_file():
                return str(candidate)
    except Exception:
        pass
    return str(Path(REPO) / "target" / "debug" / "ty")


def _ty_check(python_code: str, python_version: str = "3.12") -> str:
    """Run ty check on a snippet and return combined stdout+stderr."""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / "test_input.py"
        test_file.write_text(python_code)
        r = subprocess.run(
            [_ty_bin(), "check", "--python-version", python_version, str(test_file)],
            capture_output=True, timeout=120, cwd=REPO,
        )
        return r.stdout.decode() + r.stderr.decode()


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_ty_compiles():
    """ty binary must compile successfully."""
    r = subprocess.run(
        ["cargo", "build", "--bin", "ty"],
        cwd=REPO, capture_output=True, timeout=600,
    )
    assert r.returncode == 0, f"cargo build --bin ty failed:\n{r.stderr.decode()[-2000:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_aliased_union_emits_unresolved_attribute():
    """ty emits unresolved-attribute when accessing an attr missing from one member of a type-aliased union."""
    output = _ty_check(textwrap.dedent("""\
        class A:
            pass

        class B:
            def do_b_thing(self) -> None:
                pass

        type U = A | B

        class C:
            def __init__(self, values: list[U]) -> None:
                self.values = values

            def f(self) -> None:
                for item in self.values:
                    item.do_b_thing()
    """))
    assert "unresolved-attribute" in output, (
        f"Expected unresolved-attribute diagnostic for aliased union, got:\n{output}"
    )


# [pr_diff] fail_to_pass
def test_aliased_union_identifies_missing_type():
    """Error message identifies which concrete type lacks the attribute."""
    output = _ty_check(textwrap.dedent("""\
        class Foo:
            pass

        class Bar:
            def method(self) -> None:
                pass

        type FooBar = Foo | Bar

        def check(val: FooBar) -> None:
            val.method()
    """))
    assert "unresolved-attribute" in output, f"No unresolved-attribute diagnostic:\n{output}"
    assert "`Foo`" in output, f"Diagnostic doesn't identify Foo as the missing type:\n{output}"


# [pr_diff] fail_to_pass
def test_nested_aliased_union():
    """ty recurses into nested type aliases that resolve to unions."""
    output = _ty_check(textwrap.dedent("""\
        class Alpha:
            pass

        class Beta:
            def greet(self) -> str:
                return "hi"

        class Gamma:
            def greet(self) -> str:
                return "hello"

        type Inner = Alpha | Beta
        type Outer = Inner | Gamma

        def process(val: Outer) -> None:
            val.greet()
    """))
    assert "unresolved-attribute" in output, (
        f"Expected unresolved-attribute for nested aliased union, got:\n{output}"
    )
    assert "`Alpha`" in output, f"Diagnostic doesn't identify Alpha:\n{output}"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression checks
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_explicit_union_still_reports():
    """Explicit (non-aliased) union attribute errors still work."""
    output = _ty_check(textwrap.dedent("""\
        class X:
            pass

        class Y:
            def only_on_y(self) -> None:
                pass

        def check(val: X | Y) -> None:
            val.only_on_y()
    """))
    assert "unresolved-attribute" in output, (
        f"Explicit union should still emit unresolved-attribute:\n{output}"
    )


# [pr_diff] pass_to_pass
def test_no_false_positive_aliased_union():
    """No diagnostic when all members of aliased union have the attribute."""
    output = _ty_check(textwrap.dedent("""\
        class P:
            def shared(self) -> None:
                pass

        class Q:
            def shared(self) -> None:
                pass

        type PQ = P | Q

        def check(val: PQ) -> None:
            val.shared()
    """))
    assert "unresolved-attribute" not in output, (
        f"False positive unresolved-attribute on valid aliased union:\n{output}"
    )


# [static] pass_to_pass
def test_not_stub():
    """Modified file has meaningful content (not gutted/stubbed)."""
    target = Path(REPO) / "crates/ty_python_semantic/src/types/infer/builder.rs"
    assert target.exists(), f"{target} not found"
    line_count = len(target.read_text().splitlines())
    assert line_count >= 5000, f"File appears stubbed ({line_count} lines, expected >= 5000)"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

BASE_COMMIT = "6e76b4cd8a27c2b22263204b83372c4f3720bf79"
TARGET_FILE = "crates/ty_python_semantic/src/types/infer/builder.rs"


def _added_lines() -> list[str]:
    """Return only the '+' lines from the agent's diff against the base commit."""
    r = subprocess.run(
        ["git", "diff", BASE_COMMIT, "--", TARGET_FILE],
        cwd=REPO, capture_output=True, timeout=30,
    )
    return [
        line[1:]
        for line in r.stdout.decode().splitlines()
        if line.startswith("+") and not line.startswith("+++")
    ]


# [agent_config] pass_to_pass — AGENTS.md:79 @ 6e76b4cd
def test_no_unwrap_panic_unreachable():
    """New code must not use .unwrap(), panic!, or unreachable!."""
    for line in _added_lines():
        stripped = line.strip()
        # Skip comments
        if stripped.startswith("//"):
            continue
        assert ".unwrap()" not in line, f"Found .unwrap() in added code: {stripped}"
        assert "panic!" not in line, f"Found panic! in added code: {stripped}"
        assert "unreachable!" not in line, f"Found unreachable! in added code: {stripped}"


# [agent_config] pass_to_pass — AGENTS.md:81 @ 6e76b4cd
def test_prefer_expect_over_allow():
    """Use #[expect()] over #[allow()] for Clippy lint suppression."""
    for line in _added_lines():
        stripped = line.strip()
        assert "#[allow(" not in stripped, (
            f"Use #[expect()] instead of #[allow()]: {stripped}"
        )
