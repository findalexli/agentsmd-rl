"""
Task: ruff-typeddict-name-mismatch-diagnostic
Repo: astral-sh/ruff @ ca3343e4cf25e8314c26cce2031abb67ed6a3b16
PR:   #24295

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import textwrap
import tempfile
from pathlib import Path

REPO = "/workspace/ruff"


def _build_ty():
    """Build ty binary (incremental, should be fast after Dockerfile pre-build)."""
    r = subprocess.run(
        ["cargo", "build", "--bin", "ty"],
        cwd=REPO,
        capture_output=True,
        timeout=600,
    )
    assert r.returncode == 0, f"cargo build failed:\n{r.stderr.decode()[-2000:]}"
    return Path(REPO) / "target" / "debug" / "ty"


def _run_ty(code: str) -> str:
    """Write code to a temp file, run ty check, return combined output."""
    ty = _build_ty()
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
        f.write(textwrap.dedent(code))
        f.flush()
        r = subprocess.run(
            [str(ty), "check", f.name],
            capture_output=True,
            timeout=120,
        )
    return r.stdout.decode() + r.stderr.decode()


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — compilation check
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_cargo_check():
    """ty_python_semantic crate must compile."""
    r = subprocess.run(
        ["cargo", "check", "-p", "ty_python_semantic", "--quiet"],
        cwd=REPO,
        capture_output=True,
        timeout=600,
    )
    assert r.returncode == 0, f"cargo check failed:\n{r.stderr.decode()[-2000:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_mismatch_typing_import():
    """TypedDict("WrongName") assigned to BadTypedDict emits a diagnostic."""
    output = _run_ty("""\
        from typing import TypedDict

        BadTypedDict = TypedDict("WrongName", {"name": str})
    """)
    assert "error" in output.lower() or "warning" in output.lower(), (
        f"No diagnostic for typing import mismatch:\n{output}"
    )
    assert "WrongName" in output, f"Diagnostic should mention 'WrongName':\n{output}"


# [pr_diff] fail_to_pass
def test_mismatch_typing_extensions():
    """TypedDict("Mismatch") from typing_extensions assigned to AnotherBad emits a diagnostic."""
    output = _run_ty("""\
        from typing_extensions import TypedDict

        AnotherBad = TypedDict("Mismatch", {"x": int, "y": str})
    """)
    assert "error" in output.lower() or "warning" in output.lower(), (
        f"No diagnostic for typing_extensions mismatch:\n{output}"
    )


# [pr_diff] fail_to_pass
def test_mismatch_short_names():
    """Foo = TypedDict("Bar", ...) emits a diagnostic (varied short names)."""
    output = _run_ty("""\
        from typing import TypedDict

        Foo = TypedDict("Bar", {"a": int})
    """)
    assert "error" in output.lower() or "warning" in output.lower(), (
        f"No diagnostic for Foo/Bar mismatch:\n{output}"
    )


# [pr_diff] fail_to_pass
def test_mixed_file_only_mismatch_flagged():
    """In a file with both matching and mismatched TypedDicts, only the mismatch is flagged."""
    output = _run_ty("""\
        from typing import TypedDict

        CorrectOne = TypedDict("CorrectOne", {"a": int})
        BadOne = TypedDict("WrongOne", {"b": str})
    """)
    # Must flag the bad one
    assert "error" in output.lower() or "warning" in output.lower(), (
        f"No diagnostic for mismatch in mixed file:\n{output}"
    )
    # Must NOT mention the correct one in any diagnostic
    assert "CorrectOne" not in output, (
        f"Diagnostic incorrectly mentions CorrectOne:\n{output}"
    )


# [agent_config] fail_to_pass — AGENTS.md:83 @ ca3343e4cf25e8314c26cce2031abb67ed6a3b16
def test_diagnostic_mentions_both_names():
    """Diagnostic includes both the string name and the variable name (concise error messages)."""
    output = _run_ty("""\
        from typing import TypedDict

        MyDict = TypedDict("OtherName", {"key": str})
    """)
    assert "OtherName" in output, f"Diagnostic should mention string name 'OtherName':\n{output}"
    assert "MyDict" in output, f"Diagnostic should mention variable name 'MyDict':\n{output}"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / repo_tests) — regression + no false positives
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_correct_name_not_flagged():
    """GoodTypedDict = TypedDict("GoodTypedDict", ...) produces no diagnostic."""
    output = _run_ty("""\
        from typing import TypedDict

        GoodTypedDict = TypedDict("GoodTypedDict", {"name": str})
    """)
    # Filter out informational lines, check for actual errors/warnings
    has_diag = any(
        x in output.lower() for x in ["error[", "warning["]
    )
    assert not has_diag, f"False positive on matching TypedDict name:\n{output}"


# [pr_diff] pass_to_pass
def test_class_syntax_unaffected():
    """Class-based TypedDict syntax is not broken by the change."""
    output = _run_ty("""\
        from typing import TypedDict

        class MyDict(TypedDict):
            name: str
            age: int
    """)
    has_diag = any(
        x in output.lower() for x in ["error[", "warning["]
    )
    assert not has_diag, f"Class-based TypedDict incorrectly flagged:\n{output}"


# [repo_tests] pass_to_pass
def test_upstream_typed_dict_mdtest():
    """Existing typed_dict mdtest suite still passes."""
    import os
    env = os.environ.copy()
    env["MDTEST_TEST_FILTER"] = "typed_dict"
    r = subprocess.run(
        ["cargo", "test", "-p", "ty_python_semantic", "--test", "mdtest"],
        cwd=REPO,
        capture_output=True,
        timeout=600,
        env=env,
    )
    output = r.stdout.decode() + r.stderr.decode()
    assert r.returncode == 0 or "test result: ok" in output, (
        f"Upstream typed_dict mdtest failed:\n{output[-2000:]}"
    )
