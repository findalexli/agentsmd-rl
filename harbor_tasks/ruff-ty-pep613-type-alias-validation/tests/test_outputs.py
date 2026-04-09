"""
Task: ruff-ty-pep613-type-alias-validation
Repo: astral-sh/ruff @ 50ee3c2e70ccd8b945b1280cc1a1bf92612744db
PR:   24370

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import os
import subprocess
import tempfile
from pathlib import Path

REPO = "/workspace/ruff"
TYPE_EXPR_RS = Path(REPO) / "crates/ty_python_semantic/src/types/infer/builder/type_expression.rs"
BUILDER_RS = Path(REPO) / "crates/ty_python_semantic/src/types/infer/builder.rs"
POST_INFERENCE_MOD = Path(REPO) / "crates/ty_python_semantic/src/types/infer/builder/post_inference/mod.rs"
PEP613_ALIAS_RS = Path(REPO) / "crates/ty_python_semantic/src/types/infer/builder/post_inference/pep_613_alias.rs"

CARGO_ENV = {**os.environ, "CARGO_PROFILE_DEV_OPT_LEVEL": "1"}


def _run_ty_check(python_code: str, timeout: int = 600) -> subprocess.CompletedProcess:
    """Write a Python snippet to a temp file and run ty check on it."""
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
        f.write(python_code)
        f.flush()
        try:
            r = subprocess.run(
                ["cargo", "run", "--bin", "ty", "--", "check", f.name],
                cwd=REPO,
                capture_output=True,
                text=True,
                timeout=timeout,
                env=CARGO_ENV,
            )
            return r
        finally:
            os.unlink(f.name)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — compilation check
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_compiles():
    """Modified ty_python_semantic crate compiles successfully."""
    r = subprocess.run(
        ["cargo", "check", "-p", "ty_python_semantic"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
        env=CARGO_ENV,
    )
    assert r.returncode == 0, f"Compilation failed:\n{r.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_literal_negative_float_invalid():
    """Literal[-3.14] must be flagged as invalid-type-form."""
    code = """\
from typing import Literal

x: Literal[-3.14]
y: Literal[-2.718]
"""
    r = _run_ty_check(code)
    output = r.stdout + r.stderr
    assert "invalid-type-form" in output, (
        f"Expected 'invalid-type-form' for Literal[-3.14] but got:\n{output[-2000:]}"
    )
    # Both lines should be flagged
    count = output.count("invalid-type-form")
    assert count >= 2, (
        f"Expected at least 2 invalid-type-form errors (for -3.14 and -2.718), got {count}"
    )


# [pr_diff] fail_to_pass
def test_literal_negative_complex_invalid():
    """Literal[-3j] must be flagged as invalid-type-form."""
    code = """\
from typing import Literal

z: Literal[-3j]
w: Literal[-1.5j]
"""
    r = _run_ty_check(code)
    output = r.stdout + r.stderr
    assert "invalid-type-form" in output, (
        f"Expected 'invalid-type-form' for Literal[-3j] but got:\n{output[-2000:]}"
    )


# [pr_diff] fail_to_pass
def test_type_alias_variable_ref_invalid():
    """TypeAlias = var1 (where var1 is an int) must be flagged as invalid-type-form."""
    code = """\
from typing_extensions import TypeAlias

var1 = 3
Bad: TypeAlias = var1
"""
    r = _run_ty_check(code)
    output = r.stdout + r.stderr
    assert "invalid-type-form" in output, (
        f"Expected 'invalid-type-form' for TypeAlias = var1 but got:\n{output[-2000:]}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — valid cases must NOT be flagged
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_literal_negative_int_valid():
    """Literal[-3] (integer) must NOT be flagged — negative ints are valid in Literal."""
    code = """\
from typing import Literal

a: Literal[-3]
b: Literal[-42]
c: Literal[+7]
"""
    r = _run_ty_check(code)
    output = r.stdout + r.stderr
    assert "invalid-type-form" not in output, (
        f"Literal[-3] should be valid but got error:\n{output[-2000:]}"
    )


# [pr_diff] pass_to_pass
def test_valid_type_alias_not_flagged():
    """Valid PEP-613 type aliases must not produce invalid-type-form errors."""
    code = """\
from typing_extensions import TypeAlias

Good1: TypeAlias = int
Good2: TypeAlias = int | str
Good3: TypeAlias = list[int]
Good4: TypeAlias = tuple[int, str]
"""
    r = _run_ty_check(code)
    output = r.stdout + r.stderr
    assert "invalid-type-form" not in output, (
        f"Valid type aliases should not be flagged:\n{output[-2000:]}"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:79 @ 50ee3c2e70ccd8b945b1280cc1a1bf92612744db
def test_no_panic_unwrap_in_new_module():
    """No panic!/unwrap in the new pep_613_alias module (AGENTS.md:79)."""
    assert PEP613_ALIAS_RS.exists(), "pep_613_alias.rs not found"
    content = PEP613_ALIAS_RS.read_text()
    for i, line in enumerate(content.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("//"):
            continue
        assert "panic!(" not in stripped, f"panic! at line {i}: {stripped}"
        assert ".unwrap()" not in stripped, f".unwrap() at line {i}: {stripped}"
        assert "unreachable!(" not in stripped, f"unreachable! at line {i}: {stripped}"


# [agent_config] pass_to_pass — AGENTS.md:76 @ 50ee3c2e70ccd8b945b1280cc1a1bf92612744db
def test_no_local_imports_in_new_module():
    """Rust imports at top of file, never locally in functions (AGENTS.md:76)."""
    assert PEP613_ALIAS_RS.exists(), "pep_613_alias.rs not found"
    content = PEP613_ALIAS_RS.read_text()
    in_fn = False
    for i, line in enumerate(content.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("pub(crate) fn ") or stripped.startswith("fn "):
            in_fn = True
        if in_fn and stripped.startswith("use "):
            assert False, f"Local import inside function at line {i}: {stripped}"
