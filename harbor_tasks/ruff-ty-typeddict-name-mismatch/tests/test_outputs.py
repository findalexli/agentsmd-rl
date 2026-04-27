"""Behavioral tests for: ty must reject functional TypedDict() calls whose
string name argument does not match the assigned variable name.

ty is built once when the Docker image is created. After the agent's edit,
solve.sh / the agent should recompile the ``ty`` binary; tests then invoke
that binary directly via subprocess against a Python snippet on disk.
"""

import os
import subprocess
import tempfile
from pathlib import Path

REPO = "/workspace/ruff"
TY_BIN = os.environ.get("TY_BIN", f"{REPO}/target/release/ty")


def _run_ty_check(code: str, *, output_format: str = "concise") -> subprocess.CompletedProcess:
    """Run `ty check` on a Python snippet and return the completed process."""
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "snippet.py"
        p.write_text(code)
        return subprocess.run(
            [TY_BIN, "check", f"--output-format={output_format}", str(p)],
            capture_output=True,
            text=True,
            timeout=120,
        )


def _all_output(r: subprocess.CompletedProcess) -> str:
    return (r.stdout or "") + (r.stderr or "")


# --- fail_to_pass ----------------------------------------------------------


def test_mismatched_name_emits_diagnostic():
    """A functional TypedDict whose first-argument string differs from the
    assigned variable name must produce a diagnostic mentioning BOTH names."""
    code = (
        "from typing import TypedDict\n"
        'BadTypedDict3 = TypedDict("WrongName", {"name": str})\n'
    )
    r = _run_ty_check(code)
    out = _all_output(r)
    assert "WrongName" in out, f"diagnostic should mention the literal name 'WrongName'\n---OUTPUT---\n{out}"
    assert "BadTypedDict3" in out, f"diagnostic should mention the assigned variable 'BadTypedDict3'\n---OUTPUT---\n{out}"


def test_mismatched_name_diagnostic_phrasing():
    """The diagnostic must use the phrase 'must match the name of the variable
    it is assigned to', so users understand why their call is being rejected."""
    code = (
        "from typing import TypedDict\n"
        'MyDict = TypedDict("OtherName", {"x": int})\n'
    )
    r = _run_ty_check(code)
    out = _all_output(r)
    assert "must match the name of the variable it is assigned to" in out, (
        f"expected canonical phrase in diagnostic\n---OUTPUT---\n{out}"
    )


def test_mismatched_name_uses_invalid_argument_type_lint():
    """The diagnostic must be reported under the invalid-argument-type lint."""
    code = (
        "from typing import TypedDict\n"
        'Foo = TypedDict("Bar", {"a": int})\n'
    )
    r = _run_ty_check(code)
    out = _all_output(r)
    assert "invalid-argument-type" in out, (
        f"diagnostic must use the invalid-argument-type lint code\n---OUTPUT---\n{out}"
    )


def test_mismatched_name_typing_extensions():
    """The check must apply equally to typing_extensions.TypedDict."""
    code = (
        "from typing_extensions import TypedDict\n"
        'XDict = TypedDict("YDict", {"k": str})\n'
    )
    r = _run_ty_check(code)
    out = _all_output(r)
    assert "must match" in out, (
        f"check should fire for typing_extensions.TypedDict too\n---OUTPUT---\n{out}"
    )


# --- pass_to_pass ----------------------------------------------------------


def test_matching_name_no_mismatch_diagnostic():
    """A TypedDict whose assigned variable name equals its string argument
    must NOT trigger the name-mismatch diagnostic."""
    code = (
        "from typing import TypedDict\n"
        'Good = TypedDict("Good", {"name": str})\n'
    )
    r = _run_ty_check(code)
    out = _all_output(r)
    assert "must match" not in out, (
        f"matching names must not produce a name-mismatch diagnostic\n---OUTPUT---\n{out}"
    )


def test_non_string_name_still_flagged():
    """Pre-existing diagnostic for a non-string typename argument must still
    fire (regression test for the surrounding code path)."""
    code = (
        "from typing import TypedDict\n"
        'Bad1 = TypedDict(123, {"name": str})\n'
    )
    r = _run_ty_check(code)
    out = _all_output(r)
    assert "Invalid argument to parameter" in out or "invalid-argument-type" in out, (
        f"pre-existing TypedDict(non-str, ...) diagnostic must still fire\n---OUTPUT---\n{out}"
    )


def test_clean_module_no_typed_dict_diagnostics():
    """A module that uses no TypedDict at all must not emit any TypedDict
    diagnostic — confirms the new check does not over-fire."""
    code = (
        "def add(x: int, y: int) -> int:\n"
        "    return x + y\n"
    )
    r = _run_ty_check(code)
    out = _all_output(r)
    assert "TypedDict" not in out, (
        f"non-TypedDict code must not produce TypedDict diagnostics\n---OUTPUT---\n{out}"
    )


def test_ty_binary_runs():
    """Sanity check: ty --version exits cleanly (verifies the compiled binary
    is present and executable)."""
    r = subprocess.run([TY_BIN, "--version"], capture_output=True, text=True, timeout=30)
    assert r.returncode == 0, f"ty --version failed: {r.stderr}"
    assert "ty" in (r.stdout + r.stderr).lower()
