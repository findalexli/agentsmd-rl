"""
Task: bun-hot-test-stderr-buffer-loss
Repo: oven-sh/bun @ af24e281ebacd6ac77c0f14b4206599cf4ae1c9f
PR:   28202

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

BEHAVIORAL TESTS: We actually RUN the code via subprocess and verify it completes,
rather than grepping for implementation patterns. The bug causes sourcemap tests
to hang; the fix allows them to complete within a reasonable timeout.
"""

import os
import re
import subprocess
import time
from pathlib import Path

REPO = "/workspace/bun"
TARGET = f"{REPO}/test/cli/hot/hot.test.ts"
BUN_INSTALL_TIMEOUT = 120
TEST_TIMEOUT = 180  # Hot tests with 50 reload cycles should complete in this time


def _ensure_bun():
    """Install bun if not available."""
    result = subprocess.run(
        ["bash", "-c", "export PATH=/root/.bun/bin:$PATH && bun --version 2>/dev/null"],
        capture_output=True, text=True, timeout=10
    )
    if result.returncode == 0:
        return True

    # Install bun
    subprocess.run(
        ["bash", "-c", "apt-get update -qq && apt-get install -y -qq unzip >/dev/null 2>&1"],
        capture_output=True, text=True, timeout=60
    )
    install_result = subprocess.run(
        ["bash", "-c", "curl -fsSL https://bun.sh/install | bash"],
        capture_output=True, text=True, timeout=BUN_INSTALL_TIMEOUT
    )
    if install_result.returncode != 0:
        raise RuntimeError(f"Failed to install bun: {install_result.stderr}")

    # Verify installation
    verify_result = subprocess.run(
        ["bash", "-c", "export PATH=/root/.bun/bin:$PATH && bun --version"],
        capture_output=True, text=True, timeout=10
    )
    return verify_result.returncode == 0


def _bun_exec(cmd: list[str], timeout: int = TEST_TIMEOUT) -> subprocess.CompletedProcess:
    """Execute a command with bun in PATH."""
    env = os.environ.copy()
    env["PATH"] = "/root/.bun/bin:" + env.get("PATH", "")
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
        env=env,
        cwd=REPO,
    )


def _read_code() -> str:
    """Read the target file, stripping single-line comments to prevent gaming."""
    lines = Path(TARGET).read_text().splitlines()
    result = []
    in_block = False
    for line in lines:
        s = line.strip()
        if in_block:
            if "*/" in s:
                in_block = False
            continue
        if s.startswith("/*") and "*/" not in s:
            in_block = True
            continue
        if s.startswith("/*") and "*/" in s:
            continue
        if s.startswith("//"):
            continue
        result.append(line)
    return "\n".join(result)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

def test_target_file_exists():
    """Target test file must exist and be non-empty."""
    p = Path(TARGET)
    assert p.exists(), f"{TARGET} does not exist"
    assert p.stat().st_size > 0, f"{TARGET} is empty"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
#
# The bug causes sourcemap hot-reload tests to HANG. The fix allows them
# to COMPLETE. We verify this by RUNNING the tests and checking they complete
# within a reasonable timeout, rather than checking for specific patterns.
# ---------------------------------------------------------------------------

def test_data_loss_pattern_fixed():
    """The str='' + continue outer bug must be fixed; sourcemap generation test must complete.

    The buggy pattern discards remaining lines when a duplicate error is seen,
    causing the test to hang waiting for output that was already discarded.

    Behavioral verification: run the sourcemap generation test and verify it
    completes within timeout. If the bug is present, it hangs; if fixed, it completes.
    """
    _ensure_bun()

    # Run the sourcemap generation test (the first and most direct test of the fix)
    result = _bun_exec([
        "bun", "test", TARGET,
        "--grep", "sourcemap generation",
    ], timeout=TEST_TIMEOUT)

    # If the test completes with exit code 0, the fix is working
    # If it times out or fails, the bug is still present
    assert result.returncode == 0, (
        f"Sourcemap generation test did not complete successfully.\n"
        f"Exit code: {result.returncode}\n"
        f"Stdout (last 500 chars): {result.stdout[-500:]}\n"
        f"Stderr (last 500 chars): {result.stderr[-500:]}\n"
        f"This indicates the data loss bug is still present."
    )


def test_trailing_partial_lines_preserved():
    """Trailing partial lines from stderr split must be preserved; sourcemap loading test completes.

    When stderr is split mid-line, the trailing partial portion must be saved
    for the next chunk. Without this, lines are lost and tests hang.

    Behavioral verification: run the sourcemap loading test and verify it completes.
    """
    _ensure_bun()

    result = _bun_exec([
        "bun", "test", TARGET,
        "--grep", "sourcemap loading",
    ], timeout=TEST_TIMEOUT)

    assert result.returncode == 0, (
        f"Sourcemap loading test did not complete successfully.\n"
        f"Exit code: {result.returncode}\n"
        f"Stdout (last 500 chars): {result.stdout[-500:]}\n"
        f"Stderr (last 500 chars): {result.stderr[-500:]}\n"
        f"This indicates trailing partial lines are being discarded."
    )


def test_bundler_no_inherit_pipes():
    """Bundler subprocesses must not use stdout/stderr:'inherit' to avoid pipe backpressure.

    When bundler uses 'inherit', the test runner's pipe buffer fills up,
    blocking the bundler and stalling the test.

    Behavioral verification: run the sourcemap loading test (which spawns bundler)
    and verify it completes without deadlock.
    """
    _ensure_bun()

    # The sourcemap loading test spawns a bundler with --watch
    # If pipes are misconfigured, this deadlocks
    result = _bun_exec([
        "bun", "test", TARGET,
        "--grep", "sourcemap loading",
    ], timeout=TEST_TIMEOUT)

    assert result.returncode == 0, (
        f"Sourcemap loading test (with bundler) did not complete.\n"
        f"Exit code: {result.returncode}\n"
        f"Stdout (last 500 chars): {result.stdout[-500:]}\n"
        f"Stderr (last 500 chars): {result.stderr[-500:]}\n"
        f"This indicates pipe backpressure issue with bundler 'inherit'."
    )


def test_early_bundler_exit_detection():
    """Bundler-based tests must detect early exit; large files test completes.

    If bundler exits early and the test doesn't detect it, the test hangs
    waiting for output that will never arrive.

    Behavioral verification: run the large files test and verify it completes.
    """
    _ensure_bun()

    result = _bun_exec([
        "bun", "test", TARGET,
        "--grep", "large files",
    ], timeout=TEST_TIMEOUT)

    assert result.returncode == 0, (
        f"Large files sourcemap test did not complete.\n"
        f"Exit code: {result.returncode}\n"
        f"Stdout (last 500 chars): {result.stdout[-500:]}\n"
        f"Stderr (last 500 chars): {result.stderr[-500:]}\n"
        f"This indicates early bundler exit is not being detected."
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — regression + anti-stub
# ---------------------------------------------------------------------------

def test_sourcemap_tests_preserved():
    """All three sourcemap hot-reload tests must exist and verify 50 reload cycles.

    These tests are the canary that detects the bug. They must be preserved.
    """
    code = _read_code()

    tests = [
        "should work with sourcemap generation",
        "should work with sourcemap loading",
        "should work with sourcemap loading with large files",
    ]
    for t in tests:
        assert t in code, f"Test '{t}' missing from file"

    # Each test must still verify 50 reloads
    reload_checks = len(re.findall(r'(?:toBe|toEqual|===)\s*\(\s*50\s*\)', code))
    assert reload_checks >= 3, (
        f"Expected >= 3 reload-count assertions (toBe/toEqual 50), found {reload_checks}"
    )


def test_not_stub():
    """Modified file must have meaningful code changes, not just comments or trivial edits.

    The fix touches approximately 50+ lines across multiple functions.
    A stub implementation would not have enough changes.
    """
    diff = subprocess.run(
        ["git", "diff", "HEAD", "--", "test/cli/hot/hot.test.ts"],
        capture_output=True, text=True, cwd=REPO,
    ).stdout

    added = removed = 0
    for line in diff.splitlines():
        if line.startswith("+") and not line.startswith("+++"):
            content = line[1:].strip()
            if content and not content.startswith("//") and not content.startswith("/*"):
                added += 1
        elif line.startswith("-") and not line.startswith("---"):
            content = line[1:].strip()
            if content and not content.startswith("//") and not content.startswith("/*"):
                removed += 1

    total_changes = added + removed
    assert total_changes >= 10, (
        f"Only {total_changes} non-comment lines changed — fix should touch ~50+ lines"
    )

    code = Path(TARGET).read_text()
    assert len(code.splitlines()) > 300, "File appears gutted (< 300 lines)"


# ---------------------------------------------------------------------------
# Behavioral verification: all sourcemap tests complete
# This is the ultimate behavioral test - if the fix is correct, all three
# sourcemap tests complete without hanging
# ---------------------------------------------------------------------------

def test_all_sourcemap_tests_complete():
    """All three sourcemap hot-reload tests must complete without hanging.

    This is the master behavioral test: run all sourcemap tests and verify
    they complete. If the bug is present, they hang; if fixed, they complete.
    """
    _ensure_bun()

    # Run the full hot test suite filtered to sourcemap tests
    # Each test verifies 50 reload cycles
    result = _bun_exec([
        "bun", "test", TARGET,
        "--grep", "sourcemap",
    ], timeout=TEST_TIMEOUT * 2)  # Longer timeout for all three tests

    assert result.returncode == 0, (
        f"Sourcemap tests did not complete successfully.\n"
        f"Exit code: {result.returncode}\n"
        f"Stdout (last 1000 chars): {result.stdout[-1000:]}\n"
        f"Stderr (last 1000 chars): {result.stderr[-1000:]}"
    )

    # Verify 50 reload cycles were actually verified
    output = result.stdout + result.stderr
    assert "50" in output, "Could not verify 50 reload cycles in test output"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD checks that must pass on base and after fix
# ---------------------------------------------------------------------------

def test_repo_format():
    """Repo's Prettier formatting check passes on the modified file (pass_to_pass)."""
    subprocess.run(
        ["npm", "install", "-g", "prettier@3.6.2"],
        capture_output=True, text=True, timeout=120,
    )
    r = subprocess.run(
        ["npx", "prettier", "--check", "test/cli/hot/hot.test.ts"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier format check failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


def test_repo_oxlint():
    """Repo's oxlint passes on the target file with 0 errors (pass_to_pass)."""
    subprocess.run(
        ["npm", "install", "-g", "oxlint"],
        capture_output=True, text=True, timeout=120,
    )
    r = subprocess.run(
        ["npx", "oxlint", "--quiet", "test/cli/hot/hot.test.ts"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"oxlint found errors:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


def test_repo_typescript_project():
    """Repo's TypeScript project compiles without errors (pass_to_pass)."""
    subprocess.run(
        ["npm", "install", "-g", "typescript@5.9.2"],
        capture_output=True, text=True, timeout=120,
    )
    r = subprocess.run(
        ["npx", "tsc", "--noEmit", "--skipLibCheck"],
        capture_output=True, text=True, timeout=120, cwd=f"{REPO}/test",
    )
    errors = [line for line in r.stderr.splitlines() if "error TS" in line]
    real_errors = [e for e in errors if "regression/issue/14477" not in e]
    assert len(real_errors) == 0, f"TypeScript errors found:\n" + "\n".join(real_errors[:10])


def test_target_typescript_syntax():
    """Target file has valid TypeScript syntax (pass_to_pass)."""
    subprocess.run(
        ["npm", "install", "-g", "typescript@5.9.2"],
        capture_output=True, text=True, timeout=120,
    )
    r = subprocess.run(
        ["npx", "tsc", "--noEmit", "--skipLibCheck", "--target", "ESNext",
         "--module", "ESNext", "--moduleResolution", "bundler", TARGET],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    errors = [line for line in r.stderr.splitlines()
              if "error TS" in line and "hot.test.ts" in line]
    assert len(errors) == 0, f"TypeScript syntax errors in target file:\n" + "\n".join(errors[:5])


def test_buffer_alloc_convention():
    """Large repetitive strings must use Buffer.alloc instead of .repeat().

    This is a behavioral check: run the tests and verify they complete in
    reasonable time. If .repeat() is used for large strings, the debug
    JavaScriptCore build is very slow.
    """
    _ensure_bun()

    # Run the sourcemap generation test - if Buffer.alloc is used correctly,
    # it completes in reasonable time; with .repeat() for large strings, it's slow
    start = time.time()
    result = _bun_exec([
        "bun", "test", TARGET,
        "--grep", "sourcemap generation",
    ], timeout=TEST_TIMEOUT)
    elapsed = time.time() - start

    assert result.returncode == 0, (
        f"Test failed (likely due to slow .repeat() on large strings):\n"
        f"Exit code: {result.returncode}\n"
        f"Stdout: {result.stdout[-500:]}\n"
        f"Stderr: {result.stderr[-500:]}"
    )

    # If the test takes too long, it might be using .repeat() instead of Buffer.alloc
    # The fix should complete in under 120 seconds on a reasonable machine
    assert elapsed < 120, (
        f"Test took {elapsed:.1f}s - this suggests .repeat() may be used "
        f"instead of Buffer.alloc for large strings"
    )


def test_repo_banned_words():
    """Repo's banned words test passes (pass_to_pass)."""
    _ensure_bun()
    r = subprocess.run(
        ["bash", "-c", "export PATH=/root/.bun/bin:$PATH && bun test test/internal/ban-words.test.ts"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Banned words test failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"