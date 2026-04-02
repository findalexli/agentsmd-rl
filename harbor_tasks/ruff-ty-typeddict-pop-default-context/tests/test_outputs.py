"""
Task: ruff-ty-typeddict-pop-default-context
Repo: astral-sh/ruff @ 55177205a0c5b8664b16a9dbc708a63807de130f
PR:   24229

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import os
import subprocess
import textwrap
from pathlib import Path

REPO = "/workspace/ruff"


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


def _assert_revealed_type(output: str, expected: str):
    """Assert revealed type matches expected exactly (no union)."""
    assert "revealed type" in output.lower(), f"No reveal_type output found:\n{output}"
    assert expected in output, f"Expected revealed type '{expected}' not found:\n{output}"
    for line in output.splitlines():
        if "revealed type" in line.lower():
            assert "|" not in line, f"Revealed type is a union (should be exact):\n{line}"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
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
def test_pop_empty_dict_default():
    """pop() with empty dict default infers field type dict[str, int], not a union."""
    output = _run_ty("""\
        from typing import TypedDict

        class Config(TypedDict, total=False):
            data: dict[str, int]

        def f(c: Config) -> None:
            result = c.pop("data", {})
            reveal_type(result)
    """)
    _assert_revealed_type(output, "dict[str, int]")


# [pr_diff] fail_to_pass
def test_pop_nonempty_dict_default():
    """pop() with non-empty dict default infers field type dict[str, int]."""
    output = _run_ty("""\
        from typing import TypedDict

        class Config(TypedDict, total=False):
            data: dict[str, int]

        def f(c: Config) -> None:
            result = c.pop("data", {"a": 1})
            reveal_type(result)
    """)
    _assert_revealed_type(output, "dict[str, int]")


# [pr_diff] fail_to_pass
def test_pop_list_default():
    """pop() with empty list default infers field type list[int]."""
    output = _run_ty("""\
        from typing import TypedDict

        class Config(TypedDict, total=False):
            items: list[int]

        def f(c: Config) -> None:
            result = c.pop("items", [])
            reveal_type(result)
    """)
    _assert_revealed_type(output, "list[int]")


# [pr_diff] fail_to_pass
def test_pop_set_default():
    """pop() with set() default on different field infers set[str]."""
    output = _run_ty("""\
        from typing import TypedDict

        class Settings(TypedDict, total=False):
            name: str
            tags: set[str]

        def f(s: Settings) -> None:
            result = s.pop("tags", set())
            reveal_type(result)
    """)
    _assert_revealed_type(output, "set[str]")


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / repo_tests) — regression
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_pop_no_default():
    """pop() without default still returns the field type."""
    output = _run_ty("""\
        from typing import TypedDict

        class Config(TypedDict, total=False):
            data: dict[str, int]

        def f(c: Config) -> None:
            result = c.pop("data")
            reveal_type(result)
    """)
    assert "dict[str, int]" in output, f"pop() without default should return field type:\n{output}"


# [pr_diff] pass_to_pass
def test_get_bidirectional():
    """get() bidirectional inference not regressed."""
    output = _run_ty("""\
        from typing import TypedDict

        class Config(TypedDict, total=False):
            data: dict[str, int]

        def f(c: Config) -> None:
            result = c.get("data", {})
            reveal_type(result)
    """)
    _assert_revealed_type(output, "dict[str, int]")


# [repo_tests] pass_to_pass
def test_mdtest_typed_dict():
    """Existing typed_dict mdtest suite still passes."""
    env = {**os.environ, "CARGO_PROFILE_DEV_OPT_LEVEL": "1",
           "INSTA_FORCE_PASS": "1", "INSTA_UPDATE": "always"}
    r = subprocess.run(
        ["cargo", "test", "-p", "ty_python_semantic", "--", "mdtest::typed_dict"],
        cwd=REPO, capture_output=True, timeout=600, env=env,
    )
    assert r.returncode == 0, (
        f"typed_dict mdtests failed:\n{r.stdout.decode()[-2000:]}\n{r.stderr.decode()[-2000:]}"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config)
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:79 @ 55177205a0c5b8664b16a9dbc708a63807de130f
def test_no_new_unwrap():
    """No new .unwrap() calls added to typed_dict.rs (AGENTS.md:79)."""
    td_file = Path(REPO) / "crates/ty_python_semantic/src/types/class/typed_dict.rs"
    assert td_file.exists(), "typed_dict.rs not found"

    current_count = td_file.read_text().count(".unwrap()")

    r = subprocess.run(
        ["git", "show", "HEAD:crates/ty_python_semantic/src/types/class/typed_dict.rs"],
        cwd=REPO, capture_output=True,
    )
    base_count = r.stdout.decode().count(".unwrap()") if r.returncode == 0 else 0

    assert current_count <= base_count, (
        f"New .unwrap() calls added ({base_count} -> {current_count})"
    )


# [agent_config] pass_to_pass — AGENTS.md:79 @ 55177205a0c5b8664b16a9dbc708a63807de130f
def test_no_new_panic_unreachable():
    """No new panic!() or unreachable!() calls added to typed_dict.rs (AGENTS.md:79)."""
    td_file = Path(REPO) / "crates/ty_python_semantic/src/types/class/typed_dict.rs"
    assert td_file.exists(), "typed_dict.rs not found"

    current_text = td_file.read_text()

    r = subprocess.run(
        ["git", "show", "HEAD:crates/ty_python_semantic/src/types/class/typed_dict.rs"],
        cwd=REPO, capture_output=True,
    )
    base_text = r.stdout.decode() if r.returncode == 0 else ""

    for pattern in ["panic!(", "unreachable!("]:
        current_count = current_text.count(pattern)
        base_count = base_text.count(pattern)
        assert current_count <= base_count, (
            f"New {pattern}) calls added ({base_count} -> {current_count})"
        )


# ---------------------------------------------------------------------------
# Anti-stub (static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_truncated():
    """typed_dict.rs is not truncated (has substantial content)."""
    td_file = Path(REPO) / "crates/ty_python_semantic/src/types/class/typed_dict.rs"
    assert td_file.exists(), "typed_dict.rs not found"
    line_count = len(td_file.read_text().splitlines())
    assert line_count > 200, f"typed_dict.rs only has {line_count} lines (likely truncated)"
