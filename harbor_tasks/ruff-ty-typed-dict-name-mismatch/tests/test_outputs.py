"""Behavioral tests for ty's TypedDict-name-mismatch diagnostic.

The PR adds a check: when a functional `TypedDict("Name", ...)` is assigned
to a variable, the string passed as `typename` must match the assignment
target's identifier; otherwise ty emits an `invalid-argument-type` diagnostic.

These tests run the compiled `ty` binary against tempfiles and inspect its
output. They do NOT use the in-repo mdtest framework, so they are
independent of any test-fixture changes the agent may or may not have made
to `crates/ty_python_semantic/resources/mdtest/typed_dict.md`.
"""

from __future__ import annotations

import os
import subprocess
import tempfile

REPO = "/workspace/ruff"
TY = os.path.join(REPO, "target", "debug", "ty")


def _run_ty(source: str) -> tuple[int, str]:
    """Write source to a temp .py, run `ty check` on it, return (rc, combined output)."""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False, dir="/tmp"
    ) as fh:
        fh.write(source)
        path = fh.name
    try:
        proc = subprocess.run(
            [TY, "check", path],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=REPO,
        )
    finally:
        try:
            os.unlink(path)
        except OSError:
            pass
    return proc.returncode, proc.stdout + proc.stderr


# ─── fail_to_pass ────────────────────────────────────────────────────────────


def test_diagnostic_emitted_for_mismatched_name():
    """A TypedDict whose typename argument differs from the assigned variable
    name must be flagged. At base, ty silently accepts this; the fix must
    cause ty to exit non-zero."""
    src = (
        "from typing_extensions import TypedDict\n"
        'BadTypedDict3 = TypedDict("WrongName", {"name": str})\n'
    )
    rc, out = _run_ty(src)
    assert rc != 0, (
        f"ty exited 0 on a TypedDict with mismatched typename — "
        f"no diagnostic was raised.\nOutput:\n{out}"
    )


def test_diagnostic_mentions_both_names():
    """The diagnostic must reference both the string typename and the
    target variable so the user can see what to change."""
    src = (
        "from typing_extensions import TypedDict\n"
        'BadTypedDict3 = TypedDict("WrongName", {"name": str})\n'
    )
    rc, out = _run_ty(src)
    assert rc != 0, f"expected non-zero exit, got 0\n{out}"
    assert "WrongName" in out, (
        f"diagnostic must mention the offending typename `WrongName`.\n{out}"
    )
    assert "BadTypedDict3" in out, (
        f"diagnostic must mention the assigned variable `BadTypedDict3`.\n{out}"
    )


def test_diagnostic_uses_invalid_argument_type_category():
    """The diagnostic must be emitted under the existing `invalid-argument-type`
    rule — consistent with sibling TypedDict argument checks."""
    src = (
        "from typing_extensions import TypedDict\n"
        'BadTypedDict3 = TypedDict("WrongName", {"name": str})\n'
    )
    rc, out = _run_ty(src)
    assert rc != 0, f"expected non-zero exit, got 0\n{out}"
    assert "invalid-argument-type" in out, (
        f"diagnostic should be of category `invalid-argument-type`, "
        f"matching other TypedDict argument errors.\nOutput:\n{out}"
    )


def test_diagnostic_emitted_for_alternative_mismatch():
    """Vary the names — the check must not be hard-coded to one literal pair.
    Tests that any mismatch (different identifiers, different typename) is
    flagged."""
    src = (
        "from typing_extensions import TypedDict\n"
        'Movie = TypedDict("Film", {"title": str, "year": int})\n'
    )
    rc, out = _run_ty(src)
    assert rc != 0, (
        f"ty did not flag mismatch between variable `Movie` and typename "
        f"`Film`.\nOutput:\n{out}"
    )
    assert "Movie" in out and "Film" in out, (
        f"diagnostic must mention both `Movie` (variable) and `Film` "
        f"(typename).\nOutput:\n{out}"
    )


# ─── pass_to_pass ────────────────────────────────────────────────────────────


def test_no_false_positive_when_names_match():
    """Sanity: a correct TypedDict (typename string == variable identifier)
    must NOT trigger the new diagnostic. Guards against an over-broad fix
    that flags every functional TypedDict."""
    src = (
        "from typing_extensions import TypedDict\n"
        'Movie = TypedDict("Movie", {"title": str, "year": int})\n'
    )
    rc, out = _run_ty(src)
    assert rc == 0, (
        f"ty should accept a TypedDict whose typename matches the "
        f"variable name.\nrc={rc}\nOutput:\n{out}"
    )
    assert "Movie" not in out or "match" not in out.lower(), (
        f"no name-mismatch diagnostic should be emitted for matching "
        f"names.\nOutput:\n{out}"
    )


def test_pre_existing_invalid_typename_still_diagnosed():
    """Pre-existing behavior: a non-string typename (`TypedDict(123, ...)`)
    must still be diagnosed as `invalid-argument-type`. Guards against the
    fix accidentally bypassing the existing literal-type check."""
    src = (
        "from typing_extensions import TypedDict\n"
        'Bad1 = TypedDict(123, {"name": str})\n'
    )
    rc, out = _run_ty(src)
    assert rc != 0, f"ty should still reject TypedDict(123, ...)\n{out}"
    assert "invalid-argument-type" in out, (
        f"non-string typename must still emit `invalid-argument-type`.\n{out}"
    )
    assert "typename" in out.lower(), (
        f"diagnostic should mention `typename` parameter.\n{out}"
    )


def test_ty_accepts_clean_python_file():
    """Pre-existing behavior: ty must run cleanly on a trivial valid Python
    file, with no diagnostics. Guards against the fix breaking the binary
    or introducing crashes."""
    src = (
        "x: int = 1\n"
        "y: str = 'hello'\n"
        "def add(a: int, b: int) -> int:\n"
        "    return a + b\n"
    )
    rc, out = _run_ty(src)
    assert rc == 0, f"ty failed on a trivial valid file:\nrc={rc}\n{out}"


def test_ty_binary_compiles():
    """Pre-existing behavior: the ty crate must still compile after any fix.
    Catches `cargo build` failures (broken Rust) before the behavioral tests
    run."""
    proc = subprocess.run(
        ["cargo", "build", "--bin", "ty"],
        capture_output=True,
        text=True,
        timeout=600,
        cwd=REPO,
    )
    assert proc.returncode == 0, (
        f"cargo build --bin ty failed.\nstderr (tail):\n{proc.stderr[-2000:]}"
    )
