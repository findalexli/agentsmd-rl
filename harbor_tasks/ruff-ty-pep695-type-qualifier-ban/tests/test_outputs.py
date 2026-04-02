"""
Task: ruff-ty-pep695-type-qualifier-ban
Repo: astral-sh/ruff @ 6505b079d7b7eddbf27c8a2e60a647a085d1b8ff
PR:   #24242

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import tempfile
import re
from pathlib import Path

REPO = "/workspace/ruff"
TY = f"{REPO}/target/debug/ty"

# Files modified by the fix
MODIFIED_RS_FILES = [
    "crates/ty_python_semantic/src/types.rs",
    "crates/ty_python_semantic/src/types/infer.rs",
    "crates/ty_python_semantic/src/types/infer/builder.rs",
    "crates/ty_python_semantic/src/types/infer/builder/type_expression.rs",
]


def _build_ty():
    """Build ty binary if not already built."""
    if Path(TY).exists():
        return
    r = subprocess.run(
        ["cargo", "build", "--bin", "ty"],
        cwd=REPO, capture_output=True, timeout=600,
    )
    assert r.returncode == 0, f"cargo build failed:\n{r.stderr.decode()[-2000:]}"


def _run_ty(code: str) -> str:
    """Write code to a temp file and run ty check on it, return stdout+stderr."""
    _build_ty()
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
        f.write(code)
        f.flush()
        r = subprocess.run(
            [TY, "check", f.name],
            capture_output=True, timeout=120,
        )
    return r.stdout.decode() + r.stderr.decode()


def _get_diff_lines() -> str:
    """Get the git diff of modified Rust files."""
    r = subprocess.run(
        ["git", "diff", "HEAD", "--"] + MODIFIED_RS_FILES,
        cwd=REPO, capture_output=True, timeout=30,
    )
    return r.stdout.decode()


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_cargo_check():
    """Rust code must compile."""
    r = subprocess.run(
        ["cargo", "check", "-p", "ty_python_semantic", "--quiet"],
        cwd=REPO, capture_output=True, timeout=600,
    )
    assert r.returncode == 0, f"cargo check failed:\n{r.stderr.decode()[-2000:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_classvar_rejected_in_pep695_alias():
    """ClassVar (subscripted and bare) must produce invalid-type-form in PEP 695 type aliases."""
    # Subscripted form
    output = _run_ty(
        "from typing_extensions import ClassVar\n"
        "type A = ClassVar[str]\n"
    )
    assert "invalid-type-form" in output and "ClassVar" in output, (
        f"ClassVar[str] not flagged:\n{output}"
    )

    # Bare form
    output2 = _run_ty(
        "from typing_extensions import ClassVar\n"
        "type B = ClassVar\n"
    )
    assert "invalid-type-form" in output2 and "ClassVar" in output2, (
        f"Bare ClassVar not flagged:\n{output2}"
    )

    # Different import path
    output3 = _run_ty(
        "from typing import ClassVar\n"
        "type C = ClassVar[int]\n"
    )
    assert "invalid-type-form" in output3 and "ClassVar" in output3, (
        f"typing.ClassVar[int] not flagged:\n{output3}"
    )


# [pr_diff] fail_to_pass
def test_final_rejected_in_pep695_alias():
    """Final (subscripted and bare) must produce invalid-type-form in PEP 695 type aliases."""
    output = _run_ty(
        "from typing_extensions import Final\n"
        "type A = Final[int]\n"
        "type B = Final\n"
    )
    lines = [l for l in output.splitlines() if "invalid-type-form" in l and "Final" in l]
    assert len(lines) >= 2, f"Expected >=2 Final errors, got {len(lines)}:\n{output}"

    # Also check via typing module
    output2 = _run_ty(
        "from typing import Final\n"
        "type X = Final[str]\n"
    )
    assert "invalid-type-form" in output2 and "Final" in output2, (
        f"typing.Final[str] not flagged:\n{output2}"
    )


# [pr_diff] fail_to_pass
def test_required_notreq_readonly_rejected():
    """Required, NotRequired, ReadOnly must each produce invalid-type-form in PEP 695 type aliases."""
    output = _run_ty(
        "from typing_extensions import Required, NotRequired, ReadOnly\n"
        "type A = Required[int]\n"
        "type B = NotRequired[int]\n"
        "type C = ReadOnly[int]\n"
    )
    for qualifier in ("Required", "NotRequired", "ReadOnly"):
        matches = [l for l in output.splitlines() if "invalid-type-form" in l and qualifier in l]
        assert len(matches) >= 1, f"Expected {qualifier} error, got 0:\n{output}"


# [pr_diff] fail_to_pass
def test_initvar_rejected_in_pep695_alias():
    """InitVar (subscripted and bare) must produce invalid-type-form in PEP 695 type aliases."""
    output = _run_ty(
        "from dataclasses import InitVar\n"
        "type A = InitVar[int]\n"
        "type B = InitVar\n"
    )
    lines = [l for l in output.splitlines() if "invalid-type-form" in l and "InitVar" in l]
    assert len(lines) >= 2, f"Expected >=2 InitVar errors, got {len(lines)}:\n{output}"

    # Verify with a different subscript type
    output2 = _run_ty(
        "from dataclasses import InitVar\n"
        "type C = InitVar[str]\n"
    )
    assert "invalid-type-form" in output2 and "InitVar" in output2, (
        f"InitVar[str] not flagged:\n{output2}"
    )


# [pr_diff] fail_to_pass
def test_all_nine_qualifiers_flagged():
    """All 9 type qualifier uses in PEP 695 aliases must produce invalid-type-form."""
    output = _run_ty(
        "from typing_extensions import ClassVar, Final, Required, NotRequired, ReadOnly\n"
        "from dataclasses import InitVar\n"
        "type Bad1 = ClassVar[str]\n"
        "type Bad2 = ClassVar\n"
        "type Bad3 = Final[int]\n"
        "type Bad4 = Final\n"
        "type Bad5 = Required[int]\n"
        "type Bad6 = NotRequired[int]\n"
        "type Bad7 = ReadOnly[int]\n"
        "type Bad8 = InitVar[int]\n"
        "type Bad9 = InitVar\n"
    )
    error_lines = [l for l in output.splitlines() if "invalid-type-form" in l]
    assert len(error_lines) >= 9, f"Expected >=9 diagnostics, got {len(error_lines)}:\n{output}"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression checks
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_valid_pep695_aliases_accepted():
    """Valid PEP 695 type aliases must not produce invalid-type-form errors."""
    output = _run_ty(
        "type IntOrStr = int | str\n"
        "type OptionalInt = int | None\n"
        "type ListOf[T] = list[T]\n"
        "type DictOf[K, V] = dict[K, V]\n"
    )
    assert "invalid-type-form" not in output, f"False positive on valid aliases:\n{output}"


# [pr_diff] pass_to_pass
def test_classvar_in_annotation_still_valid():
    """ClassVar in a class annotation must not regress."""
    output = _run_ty(
        "from typing import ClassVar\n"
        "class Foo:\n"
        "    x: ClassVar[int] = 42\n"
    )
    assert "invalid-type-form" not in output, f"ClassVar in annotation regressed:\n{output}"


# [pr_diff] pass_to_pass
def test_final_in_annotation_still_valid():
    """Final in a variable annotation must not regress."""
    output = _run_ty(
        "from typing import Final\n"
        "x: Final[int] = 42\n"
    )
    assert "invalid-type-form" not in output, f"Final in annotation regressed:\n{output}"


# [pr_diff] pass_to_pass
def test_pep613_aliases_still_flagged():
    """PEP 613 TypeAlias form must still flag qualifiers (regression check)."""
    output = _run_ty(
        "from typing import TypeAlias\n"
        "from typing_extensions import ClassVar\n"
        "Bad: TypeAlias = ClassVar[int]\n"
    )
    assert "invalid-type-form" in output, f"PEP 613 alias with ClassVar not flagged:\n{output}"


# ---------------------------------------------------------------------------
# Config-derived (agent_config)
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — AGENTS.md:83 @ 6505b079d7b7eddbf27c8a2e60a647a085d1b8ff
def test_error_messages_concise():
    """Error messages for type qualifier violations must be concise (<150 chars)."""
    output = _run_ty(
        "from typing_extensions import ClassVar, Final, Required, NotRequired, ReadOnly\n"
        "from dataclasses import InitVar\n"
        "type Bad1 = ClassVar[str]\n"
        "type Bad2 = Final[int]\n"
        "type Bad3 = Required[int]\n"
        "type Bad4 = InitVar[int]\n"
    )
    error_lines = [l for l in output.splitlines() if "invalid-type-form" in l]
    assert len(error_lines) >= 1, f"No diagnostics to check conciseness on:\n{output}"
    # Extract just the message portion (after the rule name)
    for line in error_lines:
        # Format: /path/file.py:line:col: error[rule] message
        match = re.search(r'error\[invalid-type-form\]\s*(.*)', line)
        if match:
            msg = match.group(1)
            assert len(msg) <= 150, f"Message exceeds 150 chars ({len(msg)}): {msg}"


# [agent_config] fail_to_pass — AGENTS.md:79 @ 6505b079d7b7eddbf27c8a2e60a647a085d1b8ff
def test_no_unwrap_in_diff():
    """Changed code must not introduce .unwrap() / panic!() / unreachable!() calls."""
    diff = _get_diff_lines()
    if not diff:
        return  # No changes yet (nop case — will fail on other tests)
    added_lines = [l[1:] for l in diff.splitlines() if l.startswith("+") and not l.startswith("+++")]
    for line in added_lines:
        stripped = line.strip()
        # Skip comments and test/doc lines
        if stripped.startswith("//") or stripped.startswith("///"):
            continue
        assert ".unwrap()" not in stripped, f"Found .unwrap() in added code: {stripped}"
        # panic! and unreachable! — only flag if not in a comment
        if "panic!" in stripped and not stripped.startswith("//"):
            assert False, f"Found panic!() in added code: {stripped}"


# [agent_config] pass_to_pass — AGENTS.md:76 @ 6505b079d7b7eddbf27c8a2e60a647a085d1b8ff
def test_no_local_imports():
    """Rust imports must be at the top of the file, not locally in functions."""
    diff = _get_diff_lines()
    if not diff:
        return
    # Look for `use` statements in added lines that appear inside fn bodies
    # Simple heuristic: added lines containing `use ` that are indented more than typical top-level
    added_lines = [l[1:] for l in diff.splitlines() if l.startswith("+") and not l.startswith("+++")]
    for line in added_lines:
        # Top-level use statements have 0 indentation or are in impl blocks (4 spaces)
        # Function-local use statements typically have 8+ spaces of indentation
        if re.match(r'^\s{8,}use\s', line):
            assert False, f"Found likely function-local import: {line.strip()}"
