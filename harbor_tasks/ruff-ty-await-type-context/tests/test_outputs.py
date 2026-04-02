"""
Task: ruff-ty-await-type-context
Repo: astral-sh/ruff @ f283ddc382bf2d2825d21d4a59f2610ed97e5302
PR:   #24256

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import textwrap
from pathlib import Path

REPO = "/workspace/ruff"

# Files modified by the PR (where agent changes are expected)
CHANGED_FILES = [
    "crates/ty_python_semantic/src/types/infer/builder.rs",
    "crates/ty_python_semantic/src/types/infer/builder/type_expression.rs",
]


def _build_ty():
    """Build the ty binary once (cached by file existence)."""
    bin_path = Path(REPO) / "target" / "debug" / "ty"
    if not bin_path.exists():
        r = subprocess.run(
            ["cargo", "build", "--bin", "ty"],
            cwd=REPO, capture_output=True, timeout=600,
        )
        assert r.returncode == 0, f"cargo build --bin ty failed:\n{r.stderr.decode()[-3000:]}"
    assert bin_path.exists(), "ty binary not found after build"
    return str(bin_path)


def _run_ty(code: str) -> str:
    """Write code to a temp file, run ty check, return combined output."""
    ty = _build_ty()
    tmp = Path("/tmp/ty_test")
    tmp.mkdir(exist_ok=True)
    test_file = tmp / "test_input.py"
    test_file.write_text(textwrap.dedent(code))
    r = subprocess.run(
        [ty, "check", str(test_file)],
        cwd=REPO, capture_output=True, timeout=120,
    )
    return r.stdout.decode() + r.stderr.decode()


def _get_added_lines() -> str:
    """Return only the '+' lines from git diff for changed files."""
    r = subprocess.run(
        ["git", "diff", "HEAD", "--unified=0", "--"] + CHANGED_FILES,
        cwd=REPO, capture_output=True, timeout=30,
    )
    diff = r.stdout.decode()
    added = []
    for line in diff.splitlines():
        if line.startswith("+") and not line.startswith("+++"):
            added.append(line[1:])  # strip leading +
    return "\n".join(added)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — compilation check
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_cargo_check():
    """ty_python_semantic crate must compile."""
    r = subprocess.run(
        ["cargo", "check", "-p", "ty_python_semantic"],
        cwd=REPO, capture_output=True, timeout=600,
    )
    assert r.returncode == 0, f"cargo check failed:\n{r.stderr.decode()[-3000:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_await_literal_type_context():
    """list[Literal[1]] annotation must propagate through await — no false positive."""
    output = _run_ty("""\
        from typing import Literal

        async def make_lst[T](x: T) -> list[T]:
            return [x]

        async def _():
            x: list[Literal[1]] = await make_lst(1)
    """)
    assert "invalid-assignment" not in output.lower(), (
        f"False positive: invalid-assignment on Literal await:\n{output}"
    )


# [pr_diff] fail_to_pass
def test_await_self_type_context():
    """list[Self] annotation must propagate through await — no false positive."""
    output = _run_ty("""\
        from typing import Self

        class Parent:
            async def get_list(self) -> list[Self]:
                return [self]

            async def test(self):
                my_list: list[Parent] = await self.get_list()

        class Child(Parent):
            async def func2(self):
                childs: list[Child] = await self.get_list()
    """)
    assert "invalid-assignment" not in output.lower(), (
        f"False positive: invalid-assignment on Self await:\n{output}"
    )


# [pr_diff] fail_to_pass
def test_await_union_type_context():
    """list[int | None] annotation must propagate through await — no false positive."""
    output = _run_ty("""\
        async def make_lst[T](x: T) -> list[T]:
            return [x]

        async def _():
            x: list[int | None] = await make_lst(1)
    """)
    assert "invalid-assignment" not in output.lower(), (
        f"False positive: invalid-assignment on union await:\n{output}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass — regression + true-positive preservation
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_await_true_positive_preserved():
    """Genuine type mismatch through await must still be flagged."""
    output = _run_ty("""\
        async def get_int() -> int:
            return 42

        async def _():
            x: str = await get_int()
    """)
    assert "invalid-assignment" in output.lower(), (
        f"True positive lost: str = await get_int() should error:\n{output}"
    )


# [pr_diff] pass_to_pass
def test_await_basic_typed():
    """Simple typed await without generics must not regress."""
    output = _run_ty("""\
        async def identity[T](x: T) -> T:
            return x

        async def _():
            y: int = await identity(42)
    """)
    assert "invalid-assignment" not in output.lower(), (
        f"Regression: basic typed await reports false positive:\n{output}"
    )


# [pr_diff] pass_to_pass
def test_await_no_annotation():
    """Await without annotation must still infer correctly (no errors)."""
    output = _run_ty("""\
        async def make_lst[T](x: T) -> list[T]:
            return [x]

        async def _():
            x = await make_lst(1)
    """)
    assert "invalid-assignment" not in output.lower(), (
        f"Regression: await without annotation reports error:\n{output}"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:76 @ f283ddc382bf2d2825d21d4a59f2610ed97e5302
def test_no_local_rust_imports():
    """New code must not add `use` imports inside function bodies."""
    import re
    added = _get_added_lines()
    if not added.strip():
        return  # no changes yet (base commit) — pass
    # Local imports in Rust: `use` lines deeply indented (>8 spaces = inside fn)
    local_use = re.findall(r"^(\s{12,}use\s+.+;)", added, re.MULTILINE)
    assert not local_use, (
        f"Local `use` imports found inside functions (AGENTS.md:76):\n"
        + "\n".join(local_use)
    )


# [agent_config] pass_to_pass — AGENTS.md:79 @ f283ddc382bf2d2825d21d4a59f2610ed97e5302
def test_no_new_unwrap_panic():
    """New code must not introduce .unwrap(), panic!(), or unreachable!()."""
    import re
    added = _get_added_lines()
    if not added.strip():
        return  # no changes yet (base commit) — pass
    unwrap_hits = re.findall(r"\.unwrap\(\)", added)
    panic_hits = re.findall(r"\bpanic!\s*\(", added)
    unreachable_hits = re.findall(r"\bunreachable!\s*\(", added)
    violations = []
    if unwrap_hits:
        violations.append(f".unwrap() x{len(unwrap_hits)}")
    if panic_hits:
        violations.append(f"panic!() x{len(panic_hits)}")
    if unreachable_hits:
        violations.append(f"unreachable!() x{len(unreachable_hits)}")
    assert not violations, (
        f"Unsafe patterns in new code (AGENTS.md:79): {', '.join(violations)}"
    )


# [agent_config] pass_to_pass — AGENTS.md:81 @ f283ddc382bf2d2825d21d4a59f2610ed97e5302
def test_expect_over_allow():
    """New lint suppressions must use #[expect()] not #[allow()]."""
    import re
    added = _get_added_lines()
    if not added.strip():
        return  # no changes yet (base commit) — pass
    allow_hits = re.findall(r"#\[allow\(", added)
    assert not allow_hits, (
        f"Use #[expect()] instead of #[allow()] for lint suppression "
        f"(AGENTS.md:81): found {len(allow_hits)} occurrence(s)"
    )
