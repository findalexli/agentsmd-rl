"""
Task: ruff-ty-paramspec-concatenate-prefix
Repo: ruff @ 9311680c97e2ab9db027303671d2da9fa4b0de0b
PR:   24474

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import os
import subprocess
import tempfile
from pathlib import Path

REPO = "/workspace/ruff"

SUBSCRIPT_RS = Path(REPO) / "crates/ty_python_semantic/src/types/infer/builder/subscript.rs"
TYPE_EXPR_RS = Path(REPO) / "crates/ty_python_semantic/src/types/infer/builder/type_expression.rs"
TYPEVAR_RS = Path(REPO) / "crates/ty_python_semantic/src/types/infer/builder/typevar.rs"

_ty_bin_cache = None


def _ty_bin():
    """Find the pre-built ty binary."""
    global _ty_bin_cache
    if _ty_bin_cache is not None:
        return _ty_bin_cache

    for profile in ["debug", "release"]:
        p = Path(REPO) / "target" / profile / "ty"
        if p.exists():
            _ty_bin_cache = str(p)
            return _ty_bin_cache

    raise RuntimeError(
        "ty binary not found — it should be pre-built in the Docker image. "
        "Run 'cargo build --bin ty' in /workspace/ruff."
    )


def _ty_check(code: str, python_version: str = "3.12") -> str:
    """Run ty check on a code snippet, return combined stdout+stderr."""
    with tempfile.NamedTemporaryFile(
        suffix=".py", mode="w", dir="/tmp", delete=False
    ) as f:
        f.write(code)
        tmp = f.name
    try:
        r = subprocess.run(
            [_ty_bin(), "check", "--python-version", python_version, tmp],
            capture_output=True,
            text=True,
            timeout=60,
        )
        return r.stdout + r.stderr
    finally:
        os.unlink(tmp)


def _has_invalid_type_form(output: str, paramspec_name: str) -> bool:
    """Check if output contains invalid-type-form error for a specific bare ParamSpec."""
    return (
        "invalid-type-form" in output
        and "Bare ParamSpec" in output
        and f"`{paramspec_name}`" in output
    )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — compilation check
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_cargo_check():
    """ty binary exists (compilation succeeded)."""
    assert Path(_ty_bin()).exists(), "ty binary not found after build"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_paramspec_in_concatenate_prefix_pep695():
    """ty reports error for bare ParamSpec in Concatenate prefix inside subscript (PEP 695)."""
    output = _ty_check(
        """\
from typing import Concatenate, Callable

class Foo[**P]:
    attr: Callable[P, None]

def func[**P2](c: Callable[Concatenate[P2, ...], bool]):
    reveal_type(Foo[Concatenate[P2, ...]].attr)
"""
    )
    # Before fix: P2 is incorrectly accepted as prefix arg in Concatenate inside Foo[...]
    # After fix: invalid-type-form error for bare ParamSpec P2
    assert _has_invalid_type_form(output, "P2"), (
        f"Expected invalid-type-form for bare P2 in Concatenate prefix, got:\n{output}"
    )


# [pr_diff] fail_to_pass
# NOTE: This test uses Python 3.13 because ParamSpec default parameter was added in 3.13
def test_paramspec_in_default_list():
    """ty reports error for bare ParamSpec in default list for another ParamSpec."""
    output = _ty_check(
        """\
from typing import ParamSpec

Q = ParamSpec("Q")

# Bare Q in default list should be invalid
P5 = ParamSpec("P5", default=[Q])
""",
        python_version="3.13"
    )
    # Before fix: bare Q inside [Q] default list is incorrectly accepted
    # After fix: invalid-type-form for bare Q
    assert _has_invalid_type_form(output, "Q"), (
        f"Expected invalid-type-form for bare Q in default list, got:\n{output}"
    )


# [pr_diff] fail_to_pass
def test_paramspec_in_concatenate_nonlast_prefix():
    """ty reports error for bare ParamSpec in non-last position of Concatenate inside subscript."""
    output = _ty_check(
        """\
from typing import Callable, Concatenate

class Foo[**P1]:
    attr: Callable[P1, None]

type Alias[**P1] = int

def func[**P2, **P3](
    x: Foo[Concatenate[P2, P3]],
    y: Alias[Concatenate[P2, P3]],
):
    pass
"""
    )
    # Before fix: bare P2 in Concatenate prefix position inside Foo[...] accepted
    # After fix: invalid-type-form for bare P2 (not last arg of Concatenate)
    assert _has_invalid_type_form(output, "P2"), (
        f"Expected invalid-type-form for bare P2 in Concatenate non-last, got:\n{output}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / repo_tests) — regression + valid cases
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_valid_callable_paramspec():
    """Valid Callable[P, int] still works — no false positive errors."""
    output = _ty_check(
        """\
from typing import Callable, ParamSpec

P = ParamSpec("P")

def valid(
    a1: Callable[P, int],
    a2: Callable["P", int],
) -> None: ...
"""
    )
    # Valid uses of bare ParamSpec as first arg of Callable should NOT error
    assert "invalid-type-form" not in output or "Bare ParamSpec" not in output, (
        f"False positive: valid Callable[P, int] incorrectly flagged:\n{output}"
    )


# [pr_diff] pass_to_pass
def test_valid_concatenate_tail():
    """Valid Concatenate[int, P] still works — no false positive errors."""
    output = _ty_check(
        """\
from typing import Callable, Concatenate, ParamSpec

P = ParamSpec("P")

def valid(c: Callable[Concatenate[int, P], bool]):
    pass
"""
    )
    # Valid Concatenate with ParamSpec as LAST arg should NOT error
    assert "invalid-type-form" not in output or "Bare ParamSpec" not in output, (
        f"False positive: valid Concatenate[int, P] incorrectly flagged:\n{output}"
    )


# [pr_diff] pass_to_pass
def test_valid_pep695_concatenate():
    """Valid PEP 695 Concatenate[int, P] inside subscript still works."""
    output = _ty_check(
        """\
from typing import Callable, Concatenate

class Foo[**P1]:
    attr: Callable[P1, None]

def valid[**P2](c: Callable[Concatenate[int, P2], bool]):
    reveal_type(c)
    reveal_type(Foo[Concatenate[int, P2]].attr)
"""
    )
    # Valid Concatenate with P2 as LAST arg should NOT error
    assert "invalid-type-form" not in output or "Bare ParamSpec" not in output, (
        f"False positive: valid Foo[Concatenate[int, P2]] incorrectly flagged:\n{output}"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:79 @ 9311680c97e2ab9db027303671d2da9fa4b0de0b
# Only check lines ADDED by the gold patch (those with previously_allowed_paramspec pattern)
def test_no_panic_unwrap():
    """No panic!/unreachable!/unwrap in code ADDED by gold patch."""
    # The gold patch adds lines with "previously_allowed_paramspec" pattern
    # Only check those new lines, not pre-existing code in the files
    import re

    # Lines added by gold patch contain this pattern
    patch_pattern = re.compile(r'previously_allowed_paramspec')

    for filepath in [SUBSCRIPT_RS, TYPE_EXPR_RS, TYPEVAR_RS]:
        source = filepath.read_text()
        for i, line in enumerate(source.splitlines(), 1):
            # Only check lines that were ADDED by the gold patch
            if not patch_pattern.search(line):
                continue

            stripped = line.strip()
            if stripped.startswith("//"):
                continue
            assert "panic!(" not in stripped, (
                f"panic! in new code at {filepath.name}:{i}: {stripped}"
            )
            assert ".unwrap()" not in stripped, (
                f".unwrap() in new code at {filepath.name}:{i}: {stripped}"
            )
            assert "unreachable!(" not in stripped, (
                f"unreachable! in new code at {filepath.name}:{i}: {stripped}"
            )


# [agent_config] pass_to_pass — AGENTS.md:76 @ 9311680c97e2ab9db027303671d2da9fa4b0de0b
# Only check lines ADDED by the gold patch
def test_no_local_imports():
    """No local use/import statements inside functions in code ADDED by gold patch."""
    import re

    # Lines added by gold patch contain this pattern
    patch_pattern = re.compile(r'previously_allowed_paramspec')

    for filepath in [SUBSCRIPT_RS, TYPE_EXPR_RS, TYPEVAR_RS]:
        source = filepath.read_text()
        lines = source.splitlines()

        # Build a set of line numbers that were added by the gold patch
        patch_lines = set()
        for i, line in enumerate(lines, 1):
            if patch_pattern.search(line):
                patch_lines.add(i)

        # Only check functions that contain patch lines
        in_fn = False
        fn_start = 0
        brace_depth = 0
        fn_contains_patch = False

        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith("//"):
                continue

            if not in_fn:
                if "fn " in stripped and "{" in stripped:
                    in_fn = True
                    fn_start = i
                    fn_contains_patch = i in patch_lines
                    brace_depth = stripped.count("{") - stripped.count("}")
                    # Also check if any patch lines are in this function
                    # (simple heuristic: scan until we find a patch line at same brace level 1)
                    continue
            else:
                brace_depth += stripped.count("{") - stripped.count("}")

                if i in patch_lines:
                    fn_contains_patch = True

                if brace_depth <= 0:
                    # Function ended - if it contained patch lines, check for local imports
                    if fn_contains_patch:
                        for j in range(fn_start, i + 1):
                            check_line = lines[j - 1].strip()
                            if check_line.startswith("//"):
                                continue
                            assert not check_line.startswith("use "), (
                                f"Local import at {filepath.name}:{j}: {check_line}"
                            )
                    in_fn = False
                    brace_depth = 0
                    fn_contains_patch = False


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — repository CI/CD gates
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_cargo_check():
    """Repo's cargo check passes on ty_python_semantic crate (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "check", "-p", "ty_python_semantic"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"cargo check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_cargo_clippy():
    """Repo's cargo clippy passes on ty_python_semantic crate (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "clippy", "-p", "ty_python_semantic", "--", "-D", "warnings"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"cargo clippy failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_cargo_test_lib():
    """Repo's cargo test --lib passes on ty_python_semantic crate (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "test", "-p", "ty_python_semantic", "--lib", "--", "--test-threads=4"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"cargo test --lib failed:\n{r.stderr[-500:]}"
# [repo_tests] pass_to_pass
def test_repo_cargo_check_ty():
    """Repo's cargo check passes on ty binary crate (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "check", "-p", "ty"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"cargo check -p ty failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_cargo_fmt():
    """Repo's cargo fmt --check passes (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "fmt", "--all", "--check"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"cargo fmt --check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_cargo_clippy_workspace():
    """Repo's cargo clippy passes on workspace code (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "clippy", "-p", "ty_python_semantic", "-p", "ty", "-p", "ty_test", "--", "-D", "warnings"],
        capture_output=True,
        text=True,
        timeout=180,
        cwd=REPO,
    )
    assert r.returncode == 0, f"cargo clippy workspace failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_cargo_test_ty_test():
    """Repo's cargo test passes on ty_test crate (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "test", "-p", "ty_test", "--lib", "--", "--test-threads=4"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"cargo test -p ty_test failed:\n{r.stderr[-500:]}"
