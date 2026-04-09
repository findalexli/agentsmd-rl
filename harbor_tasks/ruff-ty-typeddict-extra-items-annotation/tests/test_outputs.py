"""
Task: ruff-ty-typeddict-extra-items-annotation
Repo: ruff @ a617c54b0708a8c1eb850cc3b2a5caee21137a28
PR:   24362

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import os
import tempfile
from pathlib import Path

REPO = "/workspace/ruff"


def _build_ty():
    """Build the ty binary (idempotent — skips if already built)."""
    ty = Path(REPO, "target", "debug", "ty")
    if ty.exists():
        return str(ty)
    env = {**os.environ, "CARGO_PROFILE_DEV_OPT_LEVEL": "1"}
    r = subprocess.run(
        ["cargo", "build", "--bin", "ty"],
        cwd=REPO, capture_output=True, timeout=900, env=env,
    )
    assert r.returncode == 0, f"ty build failed:\n{r.stderr.decode()[-3000:]}"
    return str(ty)


def _ty_check(code, suffix=".py"):
    """Run ty check on a Python code snippet, return combined stdout+stderr."""
    ty = _build_ty()
    fd, path = tempfile.mkstemp(suffix=suffix, dir=REPO)
    try:
        with os.fdopen(fd, "w") as f:
            f.write(code)
        r = subprocess.run(
            [ty, "check", path],
            cwd=REPO, capture_output=True, timeout=120,
        )
        return r.stdout.decode() + "\n" + r.stderr.decode()
    finally:
        os.unlink(path)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — compilation check
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_cargo_check():
    """ty_python_semantic crate compiles without errors."""
    env = {**os.environ, "CARGO_PROFILE_DEV_OPT_LEVEL": "1"}
    r = subprocess.run(
        ["cargo", "check", "-p", "ty_python_semantic"],
        cwd=REPO, capture_output=True, timeout=900, env=env,
    )
    assert r.returncode == 0, f"cargo check failed:\n{r.stderr.decode()[-3000:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_required_rejected_in_extra_items():
    """ty reports invalid-type-form when Required is used in TypedDict extra_items."""
    output = _ty_check(
        "from typing_extensions import TypedDict, Required\n"
        "\n"
        "class TD1(TypedDict, extra_items=Required[int]):\n"
        "    name: str\n"
    )
    assert "invalid-type-form" in output, (
        f"Expected invalid-type-form error for Required in extra_items, got:\n{output}"
    )


# [pr_diff] fail_to_pass
def test_not_required_rejected_in_extra_items():
    """ty reports invalid-type-form when NotRequired is used in TypedDict extra_items."""
    output = _ty_check(
        "from typing_extensions import TypedDict, NotRequired\n"
        "\n"
        "class TD2(TypedDict, extra_items=NotRequired[str]):\n"
        "    x: int\n"
    )
    assert "invalid-type-form" in output, (
        f"Expected invalid-type-form error for NotRequired in extra_items, got:\n{output}"
    )


# [pr_diff] fail_to_pass
def test_classvar_rejected_in_extra_items():
    """ty reports invalid-type-form when ClassVar is used in TypedDict extra_items."""
    output = _ty_check(
        "from typing_extensions import TypedDict, ClassVar\n"
        "\n"
        "class TD3(TypedDict, extra_items=ClassVar[int]):\n"
        "    label: str\n"
    )
    assert "invalid-type-form" in output, (
        f"Expected invalid-type-form error for ClassVar in extra_items, got:\n{output}"
    )


# [pr_diff] fail_to_pass
def test_final_rejected_in_extra_items():
    """ty reports invalid-type-form when Final is used in TypedDict extra_items."""
    output = _ty_check(
        "from typing_extensions import TypedDict, Final\n"
        "\n"
        "class TD4(TypedDict, extra_items=Final[int]):\n"
        "    key: str\n"
    )
    assert "invalid-type-form" in output, (
        f"Expected invalid-type-form error for Final in extra_items, got:\n{output}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — valid extra_items must still be accepted
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_readonly_extra_items_accepted():
    """ty does NOT report invalid-type-form for ReadOnly or plain types in extra_items."""
    output = _ty_check(
        "from typing_extensions import TypedDict, ReadOnly\n"
        "\n"
        "class Good1(TypedDict, extra_items=int):\n"
        "    name: str\n"
        "\n"
        "class Good2(TypedDict, extra_items=ReadOnly[int]):\n"
        "    name: str\n"
    )
    assert "invalid-type-form" not in output, (
        f"Unexpected invalid-type-form error for valid extra_items:\n{output}"
    )
