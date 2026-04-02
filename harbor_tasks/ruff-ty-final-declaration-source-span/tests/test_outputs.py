"""
Task: ruff-ty-final-declaration-source-span
Repo: astral-sh/ruff @ 929eb5238c82bfadad4549ff526f02efc0163dd0
PR:   #24194

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import re
import tempfile
from pathlib import Path

REPO = "/workspace/ruff"
TY = None  # built lazily


def _build_ty():
    """Build the ty binary and return its path."""
    global TY
    if TY is not None:
        return TY
    r = subprocess.run(
        ["cargo", "build", "--bin", "ty"],
        cwd=REPO,
        capture_output=True,
        timeout=600,
    )
    assert r.returncode == 0, f"cargo build --bin ty failed:\n{r.stderr.decode()[-2000:]}"
    TY = f"{REPO}/target/debug/ty"
    return TY


def _run_ty(code: str, filename: str = "test.py") -> str:
    """Write code to a temp file, run ty check on it, return combined output."""
    ty = _build_ty()
    with tempfile.NamedTemporaryFile(mode="w", suffix=f"_{filename}", delete=False) as f:
        f.write(code)
        f.flush()
        r = subprocess.run(
            [ty, "check", f.name],
            capture_output=True,
            timeout=120,
        )
    return r.stdout.decode() + r.stderr.decode()


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — compilation check
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_cargo_check():
    """Modified Rust code must compile."""
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
def test_method_assignment_shows_final_source():
    """Diagnostic for method assignment to Final attr must show 'declared as Final here'."""
    output = _run_ty("""\
from typing import Final

class C:
    x: Final[int] = 1

    def f(self):
        self.x = 2
""")
    assert "invalid-assignment" in output, f"Expected invalid-assignment diagnostic:\n{output}"
    assert re.search(r"(?i)declared as.*Final.*here|Final.*declared.*here", output), \
        f"Missing Final declaration annotation:\n{output}"


# [pr_diff] fail_to_pass
def test_init_reassignment_shows_final_source():
    """__init__ assignment after class-body value shows Final source + 'already has a value'."""
    output = _run_ty("""\
from typing import Final

class C:
    x: Final[int] = 1

    def __init__(self):
        self.x = 2
""")
    assert "invalid-assignment" in output, f"Expected invalid-assignment diagnostic:\n{output}"
    assert "already has a value" in output, f"Missing 'already has a value' message:\n{output}"
    assert re.search(r"(?i)declared as.*Final.*here|Final.*declared.*here", output), \
        f"Missing Final declaration annotation:\n{output}"


# [pr_diff] fail_to_pass
def test_inherited_final_shows_parent_annotation():
    """Inherited Final attribute assignment shows declaration site from base class."""
    output = _run_ty("""\
from typing import Final

class Base:
    x: Final[int] = 1

class Child(Base):
    def f(self):
        self.x = 2
""")
    assert "invalid-assignment" in output, f"Expected invalid-assignment diagnostic:\n{output}"
    assert re.search(r"(?i)declared as.*Final.*here|Final.*declared.*here", output), \
        f"Missing Final declaration annotation for inherited attr:\n{output}"


# ---------------------------------------------------------------------------
# Pass-to-pass — regression tests
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_nonfinal_attr_no_final_annotation():
    """Regular (non-Final) attribute assignment must NOT mention 'declared as Final'."""
    output = _run_ty("""\
class D:
    y: int = 10

    def g(self):
        self.y = 20
""")
    assert not re.search(r"(?i)declared as.*Final.*here|Final.*declared.*here", output), \
        f"Non-Final attribute incorrectly shows Final annotation:\n{output}"


# [repo_tests] pass_to_pass
def test_final_without_value_still_diagnosed():
    """Module-level Final without value must still report final-without-value."""
    output = _run_ty("""\
from typing import Final

UNINITIALIZED: Final[int]
INITIALIZED: Final[int] = 42
""")
    assert "final-without-value" in output, f"Missing final-without-value diagnostic:\n{output}"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:76 @ 929eb5238c82
def test_no_local_imports_in_functions():
    """Rust imports must be at the top of the file, not inside function bodies."""
    fa_path = Path(REPO) / "crates/ty_python_semantic/src/types/infer/builder/final_attribute.rs"
    types_path = Path(REPO) / "crates/ty_python_semantic/src/types.rs"

    for fpath in [fa_path, types_path]:
        if not fpath.exists():
            continue
        content = fpath.read_text()
        in_fn = False
        brace_depth = 0
        for line in content.splitlines():
            stripped = line.strip()
            if re.match(r"(pub\s+)?(fn|async\s+fn)\s+", stripped):
                in_fn = True
                brace_depth = 0
            if in_fn:
                brace_depth += stripped.count("{") - stripped.count("}")
                if brace_depth > 0 and re.match(r"use\s+", stripped):
                    assert False, f"Found import inside function body in {fpath.name}: {stripped}"
                if brace_depth <= 0 and "{" in line:
                    in_fn = False


# [agent_config] pass_to_pass — AGENTS.md:79 @ 929eb5238c82
def test_no_new_unwrap_calls():
    """No new .unwrap() calls added to final_attribute.rs."""
    fa_path = Path(REPO) / "crates/ty_python_semantic/src/types/infer/builder/final_attribute.rs"
    assert fa_path.exists(), "final_attribute.rs not found"

    # Count .unwrap() in base version
    r = subprocess.run(
        ["git", "show", "HEAD:" + "crates/ty_python_semantic/src/types/infer/builder/final_attribute.rs"],
        cwd=REPO,
        capture_output=True,
    )
    base_content = r.stdout.decode() if r.returncode == 0 else ""
    base_unwraps = base_content.count(".unwrap()")

    curr_content = fa_path.read_text()
    curr_unwraps = curr_content.count(".unwrap()")

    assert curr_unwraps <= base_unwraps, \
        f"New .unwrap() calls added ({base_unwraps} -> {curr_unwraps})"
