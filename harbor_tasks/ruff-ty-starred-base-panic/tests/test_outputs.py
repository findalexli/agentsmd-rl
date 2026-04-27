"""Tests for astral-sh/ruff#24699 — per-base lint checks must use the
expanded class-base list.

The fix changes
crates/ty_python_semantic/src/types/infer/builder/post_inference/static_class.rs
so that the per-base lint loop in `check_static_class_definitions` iterates
over the *expanded* base entries (which line up with `class.explicit_bases`)
instead of indexing into `class_node.bases()` by enumerated position. The
old code panicked with `index out of bounds` whenever a starred base
(`*tuple_literal`) unpacked more than one element.

The tests below run the freshly built `ty` binary on small Python
reproducers and assert that:
  - ty does not panic (no `error[panic]` diagnostic, exit code != 101)
  - ty emits the expected per-base lint diagnostics for the unpacked
    elements
  - upstream behaviour for non-starred bases is unchanged
"""
from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

REPO = "/workspace/ruff"
TY = f"{REPO}/target/debug/ty"


def _run_ty(source: str) -> subprocess.CompletedProcess:
    """Write `source` to a temp file and invoke `ty check` on it."""
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "case.py"
        path.write_text(source)
        return subprocess.run(
            [TY, "check", str(path)],
            capture_output=True,
            text=True,
            timeout=120,
        )


# ---------------------------------------------------------------------------
# fail-to-pass: panic must be gone, expected diagnostics must be present
# ---------------------------------------------------------------------------

def test_starred_final_tuple_does_not_panic():
    """`class X(*(int, bool)): ...` must not panic in per-base lint checks.

    On the base commit ty exits 101 with `error[panic]: Panicked at
    ...static_class.rs:...:... when checking ... `index out of bounds: the
    len is 1 but the index is 1``. After the fix, ty exits with code 1
    (lint errors) and never with 101 (panic).
    """
    r = _run_ty("class StarredFinalBase(*(int, bool)): ...\n")
    combined = r.stdout + r.stderr
    assert "error[panic]" not in combined, (
        f"ty panicked instead of emitting a normal lint diagnostic.\n"
        f"exit={r.returncode}\noutput:\n{combined[:2000]}"
    )
    assert r.returncode != 101, (
        f"ty exited with the panic exit code 101.\noutput:\n{combined[:2000]}"
    )


def test_starred_final_tuple_emits_subclass_of_final_class():
    """Per-base lint must catch the unpacked `bool` (final class).

    With the fix, the per-base loop walks the expanded base list, so it now
    sees `bool` (one of the unpacked elements) and emits the
    `subclass-of-final-class` diagnostic. On the buggy base commit the loop
    panics before reaching this lint at all.
    """
    r = _run_ty("class StarredFinalBase(*(int, bool)): ...\n")
    combined = r.stdout + r.stderr
    assert "error[panic]" not in combined, combined[:2000]
    assert "subclass-of-final-class" in combined, (
        f"expected `subclass-of-final-class` diagnostic for the unpacked "
        f"`bool` base; got:\n{combined[:2000]}"
    )


def test_starred_named_tuple_inheritance_no_panic():
    """A NamedTuple class with starred bases must not panic and must report
    the multiple-inheritance lint for each unpacked element.
    """
    src = (
        "from typing import NamedTuple\n"
        "class NamedTupleWithStarredBases(NamedTuple, *(int, str)): ...\n"
    )
    r = _run_ty(src)
    combined = r.stdout + r.stderr
    assert "error[panic]" not in combined, combined[:2000]
    assert r.returncode != 101, combined[:2000]
    assert "invalid-named-tuple" in combined, (
        f"expected `invalid-named-tuple` for unpacked NamedTuple bases; "
        f"got:\n{combined[:2000]}"
    )


def test_starred_protocol_inheritance_no_panic():
    """A Protocol class with starred bases must not panic and must report
    the non-protocol-inheritance lint for each unpacked element.
    """
    src = (
        "from typing import Protocol\n"
        "class ProtocolWithStarredBases(Protocol, *(int, str)): ...\n"
    )
    r = _run_ty(src)
    combined = r.stdout + r.stderr
    assert "error[panic]" not in combined, combined[:2000]
    assert r.returncode != 101, combined[:2000]
    assert "invalid-protocol" in combined, (
        f"expected `invalid-protocol` for unpacked Protocol bases; "
        f"got:\n{combined[:2000]}"
    )


def test_starred_named_variable_no_panic():
    """Starred bases sourced from a named variable (not an inline tuple)
    must also be handled without panic. This guards against fixes that only
    special-case inline tuple literals."""
    src = (
        "final_bases = (int, bool)\n"
        "class InheritsFromFinalViaNamedStarred(*final_bases): ...\n"
    )
    r = _run_ty(src)
    combined = r.stdout + r.stderr
    assert "error[panic]" not in combined, combined[:2000]
    assert r.returncode != 101, combined[:2000]
    assert "subclass-of-final-class" in combined, (
        f"expected `subclass-of-final-class` for `bool` reached via a "
        f"named-tuple starred unpack; got:\n{combined[:2000]}"
    )


def test_starred_bare_generic_emits_invalid_base():
    """An unpacked `Generic` should still emit `invalid-base` (the per-base
    loop must reach the Generic-detection arm via the expanded entries).
    """
    src = (
        "from typing import Generic\n"
        "class BareGenericInStarred(*(int, Generic)): ...\n"
    )
    r = _run_ty(src)
    combined = r.stdout + r.stderr
    assert "error[panic]" not in combined, combined[:2000]
    assert "invalid-base" in combined, (
        f"expected `invalid-base` for an unpacked plain `Generic`; "
        f"got:\n{combined[:2000]}"
    )


# ---------------------------------------------------------------------------
# pass-to-pass: pre-existing non-starred behaviour must be unchanged
# ---------------------------------------------------------------------------

def test_plain_subclass_of_final_class_still_reported():
    """Non-starred inheritance from a final class must still report
    `subclass-of-final-class`. Guards against a regression where the fix
    accidentally drops the diagnostic for the simple case.
    """
    r = _run_ty("class DirectFinalSubclass(bool): ...\n")
    combined = r.stdout + r.stderr
    assert "error[panic]" not in combined, combined[:2000]
    assert "subclass-of-final-class" in combined, (
        f"expected `subclass-of-final-class` on a direct final-class "
        f"subclass; got:\n{combined[:2000]}"
    )


def test_simple_module_typechecks_clean():
    """A module with no class-definition issues must still pass cleanly
    (exit 0). Guards against the fix breaking ordinary type-checking."""
    src = (
        "def add(x: int, y: int) -> int:\n"
        "    return x + y\n"
        "\n"
        "class C:\n"
        "    pass\n"
    )
    r = _run_ty(src)
    combined = r.stdout + r.stderr
    assert r.returncode == 0, (
        f"clean module should produce exit 0; got {r.returncode}\n{combined[:2000]}"
    )
    assert "error[panic]" not in combined


# ---------------------------------------------------------------------------
# pass-to-pass: cargo build of the touched crate stays green
# ---------------------------------------------------------------------------

def test_static_class_crate_compiles():
    """The crate that contains the patched file must still compile.
    Catches malformed fixes (e.g. broken let-chains, missing imports).
    """
    r = subprocess.run(
        ["cargo", "build", "--bin", "ty"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert r.returncode == 0, (
        f"cargo build --bin ty failed:\n{r.stderr[-2000:]}"
    )
