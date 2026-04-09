"""
Task: ruff-ty-nested-type-checking-inherit
Repo: ruff @ 02e5d6d90e269ca2c49b231f23b7d3c4fd579d92
PR:   24470

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import os
import subprocess
import tempfile
from pathlib import Path

REPO = "/workspace/ruff"

BUILDER_RS = Path(REPO) / "crates/ty_python_semantic/src/semantic_index/builder.rs"

_ty_bin_cache = None


def _ty_bin():
    """Find the pre-built ty binary (built in Dockerfile or by solve.sh)."""
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


def _ty_check(code: str) -> str:
    """Run ty check on a code snippet, return combined stdout+stderr."""
    with tempfile.NamedTemporaryFile(
        suffix=".py", mode="w", dir="/tmp", delete=False
    ) as f:
        f.write(code)
        tmp = f.name
    try:
        r = subprocess.run(
            [_ty_bin(), "check", tmp],
            capture_output=True,
            text=True,
            timeout=60,
        )
        return r.stdout + r.stderr
    finally:
        os.unlink(tmp)


def _extract_function_body(filepath: Path, func_name: str) -> str:
    """Extract the body of a Rust function from source."""
    source = filepath.read_text()
    marker = f"fn {func_name}"
    start = source.find(marker)
    assert start != -1, f"Function {func_name} not found in {filepath.name}"
    next_fn = source.find("\nfn ", start + 1)
    next_pub_fn = source.find("\npub", start + 1)
    candidates = [c for c in [next_fn, next_pub_fn] if c != -1]
    end = min(candidates) if candidates else len(source)
    return source[start:end]


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — compilation check
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_cargo_check():
    """ty binary exists after build."""
    assert Path(_ty_bin()).exists(), "ty binary not found after build"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_nested_if_else_type_checking():
    """Overloads inside if/else nested within TYPE_CHECKING should not trigger invalid-overload."""
    output = _ty_check(
        """\
import typing
import sys

if typing.TYPE_CHECKING:
    if sys.platform == "win32":
        pass
    else:
        @typing.overload
        def foo(x: int) -> int: ...
        @typing.overload
        def foo(x: str) -> str: ...
"""
    )
    # Before fix: invalid-overload emitted because nested block doesn't inherit TYPE_CHECKING
    # After fix: no invalid-overload (treated like a stub context)
    overload_errors = [
        l for l in output.splitlines() if "invalid-overload" in l
    ]
    assert len(overload_errors) == 0, (
        f"Expected no invalid-overload for nested TYPE_CHECKING, got:\n"
        + "\n".join(overload_errors)
    )


# [pr_diff] fail_to_pass
def test_nested_elif_type_checking():
    """Overloads inside elif branch nested within TYPE_CHECKING should not trigger invalid-overload."""
    output = _ty_check(
        """\
import typing
import sys

if typing.TYPE_CHECKING:
    if sys.version_info >= (3, 12):
        pass
    elif sys.platform == "linux":
        @typing.overload
        def bar(x: int) -> int: ...
        @typing.overload
        def bar(x: str) -> str: ...
    else:
        pass
"""
    )
    overload_errors = [
        l for l in output.splitlines() if "invalid-overload" in l
    ]
    assert len(overload_errors) == 0, (
        f"Expected no invalid-overload for elif in TYPE_CHECKING, got:\n"
        + "\n".join(overload_errors)
    )


# [pr_diff] fail_to_pass
def test_deeply_nested_type_checking():
    """Overloads inside double-nested conditionals within TYPE_CHECKING should not trigger invalid-overload."""
    output = _ty_check(
        """\
import typing
import sys

if typing.TYPE_CHECKING:
    if sys.platform == "win32":
        if sys.version_info >= (3, 11):
            @typing.overload
            def baz(x: int) -> int: ...
            @typing.overload
            def baz(x: str) -> str: ...
        else:
            pass
    else:
        pass
"""
    )
    overload_errors = [
        l for l in output.splitlines() if "invalid-overload" in l
    ]
    assert len(overload_errors) == 0, (
        f"Expected no invalid-overload for deeply nested TYPE_CHECKING, got:\n"
        + "\n".join(overload_errors)
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / repo_tests) — regression + valid cases
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_direct_type_checking_no_regression():
    """Overloads directly inside TYPE_CHECKING (no nesting) still produce no false positive."""
    output = _ty_check(
        """\
import typing

if typing.TYPE_CHECKING:
    @typing.overload
    def qux(x: int) -> int: ...
    @typing.overload
    def qux(x: str) -> str: ...
"""
    )
    overload_errors = [
        l for l in output.splitlines() if "invalid-overload" in l
    ]
    assert len(overload_errors) == 0, (
        f"Expected no invalid-overload for direct TYPE_CHECKING, got:\n"
        + "\n".join(overload_errors)
    )


# [repo_tests] pass_to_pass
def test_overloads_mdtest():
    """Upstream overloads mdtest suite passes."""
    env = os.environ.copy()
    env["CARGO_PROFILE_DEV_OPT_LEVEL"] = "1"
    env["INSTA_FORCE_PASS"] = "1"
    env["INSTA_UPDATE"] = "always"
    r = subprocess.run(
        [
            "cargo", "nextest", "run",
            "-p", "ty_python_semantic",
            "--", "mdtest::overloads",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        env=env,
    )
    assert r.returncode == 0, (
        f"overloads mdtest failed:\n{r.stdout[-2000:]}\n{r.stderr[-2000:]}"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:79 @ 02e5d6d90e269ca2c49b231f23b7d3c4fd579d92
def test_no_panic_unwrap():
    """No panic!/unreachable!/unwrap in the visit_stmt_if Visitor section (AGENTS.md:79)."""
    source = BUILDER_RS.read_text()
    # Find the visit_stmt_if / in_type_checking_block section where the fix lives
    marker = "self.in_type_checking_block"
    occurrences = [i for i, line in enumerate(source.splitlines(), 1)
                   if marker in line]
    assert len(occurrences) > 0, "Could not find in_type_checking_block assignments in builder.rs"

    # Check a window around each occurrence for panic/unwrap patterns
    lines = source.splitlines()
    for occ in occurrences:
        window_start = max(0, occ - 5)
        window_end = min(len(lines), occ + 5)
        for i in range(window_start, window_end):
            stripped = lines[i].strip()
            if stripped.startswith("//"):
                continue
            assert "panic!(" not in stripped, (
                f"panic! near in_type_checking_block at builder.rs:{i + 1}: {stripped}"
            )
            assert ".unwrap()" not in stripped, (
                f".unwrap() near in_type_checking_block at builder.rs:{i + 1}: {stripped}"
            )
            assert "unreachable!(" not in stripped, (
                f"unreachable! near in_type_checking_block at builder.rs:{i + 1}: {stripped}"
            )


# [agent_config] pass_to_pass — AGENTS.md:76 @ 02e5d6d90e269ca2c49b231f23b7d3c4fd579d92
def test_no_local_imports():
    """No local use/import statements inside the Visitor impl (AGENTS.md:76)."""
    source = BUILDER_RS.read_text()
    # Find the Visitor impl block where the fix lives
    visitor_start = source.find("impl<'ast> Visitor<'ast> for SemanticIndexBuilder")
    assert visitor_start != -1, "Could not find Visitor impl in builder.rs"

    visitor_section = source[visitor_start:]
    for i, line in enumerate(visitor_section.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("//"):
            continue
        # use statements at indentation > 0 inside impl are local imports
        if stripped.startswith("use ") and line.startswith("    "):
            # Allow use in match arms and closures (common Rust pattern) but not in fn bodies
            # A local `use` that's deeply indented inside a function is the problem
            if line.startswith("            use ") or line.startswith("                use "):
                assert False, (
                    f"Local import in Visitor impl at builder.rs: {stripped}"
                )
