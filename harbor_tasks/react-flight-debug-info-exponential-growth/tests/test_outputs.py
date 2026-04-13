"""
Task: react-flight-debug-info-exponential-growth
Repo: facebook/react @ e8c6362678c8bc86a02b8444d2c3f597b3dc4e22
PR:   35795 — [Flight] Skip transferReferencedDebugInfo during debug info resolution

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import os
import subprocess
from pathlib import Path

REPO = "/workspace/react"
FLIGHT_CLIENT = f"{REPO}/packages/react-client/src/ReactFlightClient.js"
ASYNC_DEBUG_TEST = (
    f"{REPO}/packages/react-server/src/__tests__/ReactFlightAsyncDebugInfo-test.js"
)

ENV = {**os.environ, "CI": "true"}


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax check
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """ReactFlightClient.js must parse without syntax errors."""
    r = subprocess.run(
        ["node", "--check", FLIGHT_CLIENT],
        capture_output=True,
        timeout=30,
    )
    assert r.returncode == 0, f"Syntax error in ReactFlightClient.js:\n{r.stderr.decode()}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral: new regression test must pass
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_no_exponential_debug_accumulation():
    """New regression test verifies debug info doesn't accumulate exponentially.

    Without the fix, a 20-level deep async component tree triggers an infinite
    loop detection error because transferReferencedDebugInfo is called for every
    debug chunk reference, compounding 2x per level.
    """
    # AST-only not applicable here — we run the actual Jest test.
    # On base commit the test case doesn't exist in the file (it's added by the PR),
    # so Jest finds 0 matching tests and exits 1. After the fix is applied the test
    # exists and passes.
    r = subprocess.run(
        [
            "yarn",
            "test",
            "packages/react-server/src/__tests__/ReactFlightAsyncDebugInfo-test.js",
            "--testNamePattern=should not exponentially accumulate debug info on outlined debug chunks",
            "--no-watchman",
        ],
        cwd=REPO,
        capture_output=True,
        timeout=110,
        env=ENV,
    )
    output = r.stdout.decode() + r.stderr.decode()
    assert "should not exponentially accumulate debug info" in output and (
        "PASS" in output or r.returncode == 0
    ), f"Regression test not found or failed:\n{output[-3000:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — structural: key fix primitives present
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
# AST-only because: ReactFlightClient.js uses Flow types, custom module
# resolution, and a browser-like environment that requires the full Jest/React
# test harness; the flag cannot be exercised in isolation.
def test_is_initializing_debug_info_flag_declared():
    """A module-level isInitializingDebugInfo boolean flag must be declared."""
    src = Path(FLIGHT_CLIENT).read_text()
    assert "isInitializingDebugInfo" in src, (
        "isInitializingDebugInfo not found in ReactFlightClient.js"
    )
    # Must have a Flow type annotation (boolean), not just used ad-hoc
    assert "isInitializingDebugInfo:" in src or "isInitializingDebugInfo =" in src, (
        "isInitializingDebugInfo declaration not found"
    )
    # Specifically the let declaration with type
    assert "let isInitializingDebugInfo" in src, (
        "Expected 'let isInitializingDebugInfo' declaration"
    )


# [pr_diff] fail_to_pass
# AST-only because: same as above
def test_flag_set_in_initialize_debug_chunk():
    """initializeDebugChunk must set isInitializingDebugInfo = true and restore it."""
    src = Path(FLIGHT_CLIENT).read_text()
    idx = src.find("function initializeDebugChunk(")
    assert idx != -1, "initializeDebugChunk function not found"
    # Take a generous slice of the function body (it's ~100 lines)
    fn_slice = src[idx : idx + 4000]
    assert "isInitializingDebugInfo = true" in fn_slice, (
        "isInitializingDebugInfo not set to true inside initializeDebugChunk"
    )
    assert "prevIsInitializingDebugInfo" in fn_slice, (
        "Previous flag value not saved (prevIsInitializingDebugInfo) in initializeDebugChunk"
    )
    assert "finally" in fn_slice, (
        "Missing finally block to restore isInitializingDebugInfo in initializeDebugChunk"
    )


# [pr_diff] fail_to_pass
# AST-only because: same as above
def test_flag_set_in_resolve_io_info():
    """resolveIOInfo must set isInitializingDebugInfo = true and restore it."""
    src = Path(FLIGHT_CLIENT).read_text()
    idx = src.find("function resolveIOInfo(")
    assert idx != -1, "resolveIOInfo function not found"
    fn_slice = src[idx : idx + 2000]
    assert "isInitializingDebugInfo = true" in fn_slice, (
        "isInitializingDebugInfo not set to true inside resolveIOInfo"
    )
    assert "prevIsInitializingDebugInfo" in fn_slice, (
        "Previous flag value not saved in resolveIOInfo"
    )
    assert "finally" in fn_slice, (
        "Missing finally block to restore isInitializingDebugInfo in resolveIOInfo"
    )


# [pr_diff] fail_to_pass
# AST-only because: same as above
def test_transfer_debug_info_guarded_during_debug_init():
    """getOutlinedModel must skip transferReferencedDebugInfo when isInitializingDebugInfo."""
    src = Path(FLIGHT_CLIENT).read_text()
    idx = src.find("function getOutlinedModel(")
    if idx == -1:
        idx = src.find("function getOutlinedModel<")
    assert idx != -1, "getOutlinedModel function not found"
    # The function is large; take enough to cover the relevant section
    fn_slice = src[idx : idx + 8000]
    assert "isInitializingDebugInfo" in fn_slice, (
        "isInitializingDebugInfo check missing in getOutlinedModel — "
        "transferReferencedDebugInfo will fire during debug chunk resolution"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — Repo CI/CD checks that must pass
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_lint():
    """Repo's ESLint check passes (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "lint"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
        env=ENV,
    )
    assert r.returncode == 0, f"Lint failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_version_check():
    """Repo's version check passes (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "version-check"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30,
        env=ENV,
    )
    assert r.returncode == 0, f"Version check failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_flow_dom_node():
    """Repo's Flow type check (dom-node) passes (pass_to_pass)."""
    r = subprocess.run(
        ["node", "./scripts/tasks/flow-ci.js", "dom-node"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
        env=ENV,
    )
    assert r.returncode == 0, f"Flow check failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_react_flight_client_tests():
    """React Flight client tests pass (pass_to_pass)."""
    r = subprocess.run(
        [
            "yarn",
            "test",
            "packages/react-client/src/__tests__/ReactFlight-test.js",
            "--no-watchman",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
        env=ENV,
    )
    output = r.stdout + r.stderr
    assert r.returncode == 0 or "PASS" in output, (
        f"React Flight client tests failed:\n{output[-2000:]}"
    )


# [repo_tests] pass_to_pass
def test_repo_react_flight_debug_channel_tests():
    """React Flight debug channel tests pass (pass_to_pass)."""
    r = subprocess.run(
        [
            "yarn",
            "test",
            "packages/react-client/src/__tests__/ReactFlightDebugChannel-test.js",
            "--no-watchman",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
        env=ENV,
    )
    output = r.stdout + r.stderr
    assert r.returncode == 0 or "PASS" in output, (
        f"React Flight debug channel tests failed:\n{output[-2000:]}"
    )


# [repo_tests] pass_to_pass
def test_existing_async_info_test_passes():
    """Existing 'can track async information when awaited' test must still pass."""
    r = subprocess.run(
        [
            "yarn",
            "test",
            "packages/react-server/src/__tests__/ReactFlightAsyncDebugInfo-test.js",
            "--testNamePattern=can track async information when awaited",
            "--no-watchman",
        ],
        cwd=REPO,
        capture_output=True,
        timeout=110,
        env=ENV,
    )
    output = r.stdout.decode() + r.stderr.decode()
    assert r.returncode == 0 or "PASS" in output, (
        f"Existing async info test failed:\n{output[-3000:]}"
    )


# [repo_tests] pass_to_pass
def test_repo_react_client_all_tests():
    """All React Flight client tests pass (pass_to_pass)."""
    r = subprocess.run(
        [
            "yarn",
            "test",
            "packages/react-client/src/__tests__/",
            "--no-watchman",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180,
        env=ENV,
    )
    output = r.stdout + r.stderr
    assert r.returncode == 0 or "PASS" in output, (
        f"React Flight client tests failed:\n{output[-2000:]}"
    )


# [repo_tests] pass_to_pass
def test_repo_react_server_async_debug_tests():
    """React Flight async debug info tests pass (pass_to_pass)."""
    r = subprocess.run(
        [
            "yarn",
            "test",
            "packages/react-server/src/__tests__/ReactFlightAsyncDebugInfo-test.js",
            "--no-watchman",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
        env=ENV,
    )
    output = r.stdout + r.stderr
    assert r.returncode == 0 or "PASS" in output, (
        f"React Flight async debug info tests failed:\n{output[-2000:]}"
    )


# [repo_tests] pass_to_pass
def test_repo_extract_errors():
    """Error code extraction passes (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "extract-errors"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
        env=ENV,
    )
    assert r.returncode == 0, f"Extract errors failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_flags():
    """Feature flags check passes (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "flags"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
        env=ENV,
    )
    assert r.returncode == 0, f"Flags check failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"
