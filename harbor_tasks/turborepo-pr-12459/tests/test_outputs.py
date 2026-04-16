"""
test_outputs.py — vercel/turborepo#12459
Fix: Prevent panic in `turbo watch` with persistent tasks

Tests that the fix compiles, passes clippy, and doesn't break existing tests.
The base commit has two bugs:
1. Arc::into_inner panics when persistent tasks hold extra Arc clones
2. processes.stop() kills persistent tasks that watch coordinator should manage
"""

import subprocess
import os
import pytest
import re

REPO = "/workspace/turbo_repo"


def test_cargo_check():
    """turborepo-lib compiles without errors (fail_to_pass)."""
    r = subprocess.run(
        ["cargo", "check", "-p", "turborepo-lib"],
        cwd=REPO,
        capture_output=True,
        timeout=600,
        env={**os.environ, "RUSTFLAGS": "-D warnings"},
    )
    assert r.returncode == 0, (
        f"cargo check failed:\n"
        f"STDOUT:\n{r.stdout[-3000:].decode()}\n"
        f"STDERR:\n{r.stderr[-3000:].decode()}"
    )


def test_cargo_clippy():
    """turborepo-lib passes clippy lints (fail_to_pass).

    The fix replaces Arc::into_inner (which panics on extra refs) with
    Arc::try_unwrap (which handles extra refs gracefully). This pattern
    should pass clippy scrutiny.
    """
    r = subprocess.run(
        ["cargo", "clippy", "-p", "turborepo-lib", "--", "-D", "warnings"],
        cwd=REPO,
        capture_output=True,
        timeout=600,
        env={**os.environ, "RUSTFLAGS": "-D warnings"},
    )
    assert r.returncode == 0, (
        f"clippy failed:\n"
        f"STDOUT:\n{r.stdout[-3000:].decode()}\n"
        f"STDERR:\n{r.stderr[-3000:].decode()}"
    )


def test_cargo_test_turborepo_lib():
    """turborepo-lib unit tests pass (pass_to_pass).

    Runs the existing unit test suite for the turborepo-lib crate.
    These tests must continue to pass after the fix is applied.
    """
    r = subprocess.run(
        ["cargo", "test", "-p", "turborepo-lib"],
        cwd=REPO,
        capture_output=True,
        timeout=900,
    )
    assert r.returncode == 0, (
        f"cargo test failed:\n"
        f"STDOUT:\n{r.stdout[-3000:].decode()}\n"
        f"STDERR:\n{r.stderr[-3000:].decode()}"
    )


def test_try_unwrap_pattern_exists():
    """Verify the fix uses Arc::try_unwrap instead of Arc::into_inner (f2p).

    The visitor/mod.rs originally used Arc::into_inner which panics when
    there are multiple strong references. In watch mode with fire-and-forget
    persistent tasks, extra Arc clones exist. The fix uses Arc::try_unwrap
    with a fallback that drains the mutex.

    The buggy code is around line 560-570 in the Visitor's finish() method.
    """
    visitor_path = os.path.join(
        REPO, "crates/turborepo-lib/src/task_graph/visitor/mod.rs"
    )
    with open(visitor_path, "r") as f:
        lines = f.readlines()

    # Find line numbers for Arc::into_inner and Arc::try_unwrap in visitor/mod.rs
    into_inner_lines = []
    try_unwrap_lines = []
    for i, line in enumerate(lines):
        if "Arc::into_inner" in line:
            into_inner_lines.append(i + 1)  # 1-indexed
        if "try_unwrap" in line:
            try_unwrap_lines.append(i + 1)

    # In the buggy base commit: Arc::into_inner is at line ~563 (in finish method)
    # After fix: that line becomes Arc::try_unwrap
    # The finish() method is the only place where error Arc unwrapping happens

    # Check: finish() method should NOT use Arc::into_inner with expect
    # (that's the buggy panic-prone pattern)
    for lineno in into_inner_lines:
        # Get surrounding context (within 20 lines = in the same small function)
        context_start = max(0, lineno - 20)
        context_end = min(len(lines), lineno + 5)
        context = "".join(lines[context_start:context_end])
        # The finish() method in Visitor processes errors with Arc::into_inner
        # If this Arc::into_inner is near try_unwrap usage (from a different fn),
        # we need to distinguish
        # The bug is specifically in the error-collection unwrapping in finish()
        if "Arc::into_inner(errors)" in context:
            pytest.fail(
                f"finish() method uses panic-prone Arc::into_inner(errors).expect() "
                f"at line {lineno}. Should use Arc::try_unwrap with fallback. "
                f"In watch mode with persistent tasks, Arc may have multiple refs."
            )

    # The fixed code should have try_unwrap in the error-handling section
    # Specifically, the fix adds try_unwrap near the old into_inner location
    has_proper_unwrap = False
    for lineno in try_unwrap_lines:
        context_start = max(0, lineno - 5)
        context_end = min(len(lines), lineno + 10)
        context = "".join(lines[context_start:context_end])
        # The fix introduces try_unwrap for the errors mutex
        if "errors" in context and "mutex" in context.lower():
            has_proper_unwrap = True
            break

    assert has_proper_unwrap, (
        "finish() method should use Arc::try_unwrap to handle errors mutex "
        "(try_unwrap needed because persistent tasks may hold extra Arc refs)"
    )


def test_watch_mode_guard_exists():
    """Verify processes.stop() is guarded by is_watch check (f2p).

    The run/mod.rs originally called processes.stop() unconditionally after
    visitor.visit(). In watch mode, persistent tasks run as fire-and-forget
    background processes managed by the watch coordinator — killing them
    here causes the panic. The fix wraps the stop call in if !is_watch.
    """
    run_mod_path = os.path.join(
        REPO, "crates/turborepo-lib/src/run/mod.rs"
    )
    with open(run_mod_path, "r") as f:
        content = f.read()

    lines = content.split("\n")
    in_execute_visitor = False
    brace_depth = 0  # Track brace nesting depth
    found_guarded_stop = False

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Detect enter/exit of execute_visitor function
        if "fn execute_visitor" in line:
            in_execute_visitor = True
            brace_depth = 0
            continue

        if in_execute_visitor:
            # Count braces to track when we leave execute_visitor
            brace_depth += stripped.count("{") - stripped.count("}")
            if brace_depth < 0 or (brace_depth == 0 and "}" in stripped):
                in_execute_visitor = False
                continue

            if "processes.stop()" in line:
                # Check if this line is inside an `if !is_watch` block
                # by looking at preceding lines within the same function
                preceding = "\n".join(lines[max(0, i-10):i])
                # Look for `if !is_watch {` before this line, without an
                # intervening closing brace that would close the if block
                if re.search(r"if\s+!\s*is_watch\s*\{", preceding):
                    found_guarded_stop = True
                break

    assert found_guarded_stop, (
        "processes.stop() in execute_visitor() should be guarded by "
        "if !is_watch { ... } to prevent killing persistent tasks in watch mode"
    )


def test_repo_watch_tests():
    """Watch mode tests pass (pass_to_pass).

    The fix addresses issues in watch mode where persistent tasks
    need special handling. Run the watch-specific tests to verify.
    """
    r = subprocess.run(
        ["cargo", "test", "-p", "turborepo-lib", "run::watch"],
        cwd=REPO,
        capture_output=True,
        timeout=600,
    )
    assert r.returncode == 0, (
        f"Watch mode tests failed:\n"
        f"STDOUT:\n{r.stdout[-3000:].decode()}\n"
        f"STDERR:\n{r.stderr[-3000:].decode()}"
    )


def test_repo_visitor_command_tests():
    """Visitor command tests pass (pass_to_pass).

    The visitor/mod.rs changes affect how commands are processed.
    Run the visitor command tests to verify command handling works.
    """
    r = subprocess.run(
        ["cargo", "test", "-p", "turborepo-lib", "task_graph::visitor::command"],
        cwd=REPO,
        capture_output=True,
        timeout=600,
    )
    assert r.returncode == 0, (
        f"Visitor command tests failed:\n"
        f"STDOUT:\n{r.stdout[-3000:].decode()}\n"
        f"STDERR:\n{r.stderr[-3000:].decode()}"
    )


def test_repo_task_filter_tests():
    """Task filter tests pass (pass_to_pass).

    The run/mod.rs handles task filtering which may interact with
    the persistent task fix. Run task filter tests to verify.
    """
    r = subprocess.run(
        ["cargo", "test", "-p", "turborepo-lib", "run::task_filter"],
        cwd=REPO,
        capture_output=True,
        timeout=600,
    )
    assert r.returncode == 0, (
        f"Task filter tests failed:\n"
        f"STDOUT:\n{r.stdout[-3000:].decode()}\n"
        f"STDERR:\n{r.stderr[-3000:].decode()}"
    )


def test_repo_fmt_check():
    """Repo formatting check passes (pass_to_pass).

    CI runs cargo fmt --check on all Rust changes.
    Verify formatting is correct.
    """
    r = subprocess.run(
        ["cargo", "fmt", "--check"],
        cwd=REPO,
        capture_output=True,
        timeout=120,
    )
    assert r.returncode == 0, (
        f"Formatting check failed:\n"
        f"STDOUT:\n{r.stdout[-1000:].decode()}\n"
        f"STDERR:\n{r.stderr[-1000:].decode()}"
    )
