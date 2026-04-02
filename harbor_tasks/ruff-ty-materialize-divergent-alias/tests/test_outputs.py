"""
Task: ruff-ty-materialize-divergent-alias
Repo: astral-sh/ruff @ c4c6c22d7b73342b3dfebcd526c466fa1df759c8
PR:   23784

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import subprocess
import tempfile
from pathlib import Path

REPO = Path("/workspace/ruff") if Path("/workspace/ruff").exists() else Path("/repo")
TARGET = REPO / "crates" / "ty_python_semantic" / "src" / "types.rs"


def _ty_bin() -> str:
    """Build ty (incremental if already compiled) and return the binary path."""
    r = subprocess.run(
        ["cargo", "build", "--bin", "ty"],
        cwd=REPO,
        capture_output=True,
        timeout=300,
    )
    assert r.returncode == 0, f"cargo build --bin ty failed:\n{r.stderr.decode()[-2000:]}"
    # Find binary via cargo metadata
    meta = subprocess.run(
        ["cargo", "metadata", "--format-version=1", "--no-deps"],
        cwd=REPO,
        capture_output=True,
        timeout=30,
    )
    if meta.returncode == 0:
        target_dir = json.loads(meta.stdout)["target_directory"]
        candidate = Path(target_dir) / "debug" / "ty"
        if candidate.exists():
            return str(candidate)
    return str(REPO / "target" / "debug" / "ty")


def _run_ty(code: str, timeout: int = 60) -> subprocess.CompletedProcess:
    """Write code to a temp file and run ty check on it."""
    ty = _ty_bin()
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
        f.write(code)
        f.flush()
        return subprocess.run(
            [ty, "check", "--python-version", "3.12", f.name],
            capture_output=True,
            timeout=timeout,
        )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_ty_compiles():
    """ty crate must compile without errors."""
    _ty_bin()  # asserts inside


# [static] pass_to_pass
def test_target_file_not_stubbed():
    """types.rs must have real content (not gutted)."""
    line_count = len(TARGET.read_text().splitlines())
    assert line_count >= 5000, f"types.rs looks stubbed ({line_count} lines, expected >=5000)"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_recursive_callable_typeis_no_crash():
    """Recursive Callable aliases with TypeIs resolve without crash/timeout."""
    result = _run_ty(
        "from typing_extensions import TypeIs\n"
        "from collections.abc import Callable\n"
        "\n"
        "type CallableIs = TypeIs[Callable[[], CallableIs]]\n"
        "x: object = CallableIs\n"
    )
    assert result.returncode <= 1, (
        f"ty crashed or timed out (exit={result.returncode}):\n"
        f"{result.stderr.decode()[-1000:]}"
    )


# [pr_diff] fail_to_pass
def test_recursive_callable_typeguard_no_crash():
    """Recursive Callable aliases with TypeGuard resolve without crash/timeout."""
    result = _run_ty(
        "from typing_extensions import TypeGuard\n"
        "from collections.abc import Callable\n"
        "\n"
        "type CallableGuard = TypeGuard[Callable[[], CallableGuard]]\n"
        "y: object = CallableGuard\n"
    )
    assert result.returncode <= 1, (
        f"ty crashed or timed out (exit={result.returncode}):\n"
        f"{result.stderr.decode()[-1000:]}"
    )


# [pr_diff] fail_to_pass
def test_callable_aliases_not_flagged_cyclic():
    """Callable-wrapped recursive TypeIs/TypeGuard aliases are not flagged as cyclic."""
    result = _run_ty(
        "from typing_extensions import TypeGuard, TypeIs\n"
        "from collections.abc import Callable\n"
        "\n"
        "type CallableIs = TypeIs[Callable[[], CallableIs]]\n"
        "type CallableGuard = TypeGuard[Callable[[], CallableGuard]]\n"
        "\n"
        "def use_is(x: CallableIs) -> None:\n"
        "    pass\n"
        "\n"
        "def use_guard(x: CallableGuard) -> None:\n"
        "    pass\n"
    )
    assert result.returncode <= 1, f"ty crashed (exit={result.returncode})"
    output = result.stdout.decode() + result.stderr.decode()
    assert "cyclic-type-alias-definition" not in output, (
        f"Callable-wrapped aliases incorrectly flagged as cyclic:\n{output[:1000]}"
    )


# [pr_diff] fail_to_pass
def test_nested_callable_recursion():
    """Deeper nesting: Callable wrapping Callable with recursive TypeIs reference."""
    result = _run_ty(
        "from typing_extensions import TypeIs\n"
        "from collections.abc import Callable\n"
        "\n"
        "type NestedCallableIs = TypeIs[Callable[[int], Callable[[], NestedCallableIs]]]\n"
        "val: object = NestedCallableIs\n"
    )
    assert result.returncode <= 1, (
        f"ty crashed on nested Callable recursion (exit={result.returncode}):\n"
        f"{result.stderr.decode()[-1000:]}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_direct_recursive_typeis_still_cyclic():
    """Direct recursive TypeIs[Self] (not Callable-wrapped) still produces cyclic error."""
    result = _run_ty(
        "from typing_extensions import TypeIs\n"
        "\n"
        "type RecursiveIs = TypeIs[RecursiveIs]\n"
    )
    output = result.stdout.decode() + result.stderr.decode()
    assert "cyclic-type-alias-definition" in output, (
        f"Direct recursive TypeIs should be flagged as cyclic but wasn't:\n{output[:1000]}"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:76 @ c4c6c22
def test_no_local_imports_in_diff():
    """Rust imports should be at top of file, not locally in functions (AGENTS.md:76)."""
    r = subprocess.run(
        ["git", "diff", "HEAD"],
        cwd=REPO,
        capture_output=True,
        timeout=10,
    )
    diff = r.stdout.decode()
    if not diff:
        r2 = subprocess.run(
            ["git", "diff", "HEAD~1"],
            cwd=REPO,
            capture_output=True,
            timeout=10,
        )
        diff = r2.stdout.decode()
    if not diff:
        return  # no diff to check
    added_lines = [
        line for line in diff.splitlines()
        if line.startswith("+") and not line.startswith("+++")
    ]
    local_imports = [
        line for line in added_lines
        if line.lstrip("+").startswith("        use ")  # 8+ spaces = inside function
    ]
    assert len(local_imports) == 0, (
        f"Found {len(local_imports)} new deeply-nested imports in functions:\n"
        + "\n".join(local_imports[:5])
    )


# [agent_config] pass_to_pass — AGENTS.md:79 @ c4c6c22
def test_no_unwrap_panic_in_diff():
    """Avoid panic!, unreachable!, or .unwrap() in new code (AGENTS.md:79)."""
    r = subprocess.run(
        ["git", "diff", "HEAD"],
        cwd=REPO,
        capture_output=True,
        timeout=10,
    )
    diff = r.stdout.decode()
    if not diff:
        r2 = subprocess.run(
            ["git", "diff", "HEAD~1"],
            cwd=REPO,
            capture_output=True,
            timeout=10,
        )
        diff = r2.stdout.decode()
    if not diff:
        return  # no diff to check
    added_lines = [
        line for line in diff.splitlines()
        if line.startswith("+") and not line.startswith("+++")
    ]
    violations = [
        line for line in added_lines
        if ".unwrap()" in line or "panic!(" in line or "unreachable!(" in line
    ]
    assert len(violations) == 0, (
        f"Found {len(violations)} unwrap()/panic!/unreachable! in new code:\n"
        + "\n".join(violations[:5])
    )
