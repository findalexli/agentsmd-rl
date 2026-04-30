"""Tests for lobehub/lobe-chat#10575: token refresh retry mechanism.

The PR adds retry logic to desktop OIDC token refresh so transient network
errors don't immediately log users out. It also updates CLAUDE.md to change
the Linear issue workflow from "Done" to "In Review" when a PR is created.
"""

import json
import os
import re
import subprocess
from pathlib import Path

REPO = Path("/workspace/lobe-chat")

# Track if we've installed dependencies
deps_installed = False


def _ensure_deps():
    """Ensure pnpm is enabled and dependencies are installed."""
    global deps_installed
    if deps_installed:
        return

    # Enable pnpm via corepack
    subprocess.run(["corepack", "enable", "pnpm"], capture_output=True, check=False)

    # Check if node_modules exists
    if not (REPO / "node_modules").exists():
        # Install root dependencies
        subprocess.run(
            ["pnpm", "install", "-s"],
            capture_output=True,
            timeout=300,
            cwd=REPO,
        )

    # Check if desktop node_modules exists
    if not (REPO / "apps/desktop/node_modules").exists():
        # Install desktop dependencies
        subprocess.run(
            ["pnpm", "install", "-s"],
            capture_output=True,
            timeout=300,
            cwd=REPO / "apps/desktop",
        )

    deps_installed = True


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _run_node(script: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Write *script* to a temp .mjs file and execute with node."""
    script_path = REPO / "_eval_tmp.mjs"
    script_path.write_text(script)
    try:
        return subprocess.run(
            ["node", str(script_path)],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    finally:
        script_path.unlink(missing_ok=True)


def _extract_error_constants():
    """Return (oidc_array_src, deterministic_array_src) from RemoteServerConfigCtr.ts."""
    source = REPO / "apps/desktop/src/main/controllers/RemoteServerConfigCtr.ts"
    content = source.read_text()

    oidc_m = re.search(
        r"NON_RETRYABLE_OIDC_ERRORS\s*=\s*\[([^\]]+)\]", content
    )
    det_m = re.search(
        r"DETERMINISTIC_FAILURES\s*=\s*\[([^\]]+)\]", content
    )
    assert oidc_m, "NON_RETRYABLE_OIDC_ERRORS constant not found"
    assert det_m, "DETERMINISTIC_FAILURES constant not found"
    return oidc_m.group(1), det_m.group(1)


def _build_error_check_script(test_inputs: dict) -> str:
    """Create a standalone node script that tests isNonRetryableError."""
    oidc_src, det_src = _extract_error_constants()
    return (
        "const NON_RETRYABLE_OIDC_ERRORS = ["
        + oidc_src
        + "];\n"
        "const DETERMINISTIC_FAILURES = ["
        + det_src
        + "];\n"
        "function isNonRetryableError(error) {\n"
        "  if (!error) return false;\n"
        "  const lowerError = error.toLowerCase();\n"
        "  if (NON_RETRYABLE_OIDC_ERRORS.some(c => lowerError.includes(c))) return true;\n"
        "  if (DETERMINISTIC_FAILURES.some(m => lowerError.includes(m))) return true;\n"
        "  return false;\n"
        "}\n"
        "const inputs = "
        + json.dumps(test_inputs)
        + ";\n"
        "const out = {};\n"
        "for (const [k, v] of Object.entries(inputs)) out[k] = isNonRetryableError(v);\n"
        "console.log(JSON.stringify(out));\n"
    )


# ===================================================================
# f2p — code behavior tests
# ===================================================================


def test_oidc_error_codes_detected():
    """isNonRetryableError must flag OIDC error codes as non-retryable."""
    script = _build_error_check_script(
        {
            "grant": "invalid_grant",
            "client": "Token refresh failed: invalid_client",
            "denied": "access_denied by resource owner",
            "scope": "invalid_scope in request",
            "unauth": "unauthorized_client",
        }
    )
    r = _run_node(script)
    assert r.returncode == 0, f"node failed: {r.stderr}"
    results = json.loads(r.stdout.strip())
    for key, val in results.items():
        assert val is True, f"{key} should be non-retryable, got {val}"


def test_deterministic_failures_detected():
    """Deterministic failures (missing token, bad config) must be non-retryable."""
    script = _build_error_check_script(
        {
            "no_token": "no refresh token available",
            "inactive": "remote server is not active or configured",
            "missing": "missing tokens in refresh response",
        }
    )
    r = _run_node(script)
    assert r.returncode == 0, f"node failed: {r.stderr}"
    results = json.loads(r.stdout.strip())
    for key, val in results.items():
        assert val is True, f"{key} should be non-retryable, got {val}"


def test_transient_errors_are_retryable():
    """Network / transient errors must NOT be flagged as non-retryable."""
    script = _build_error_check_script(
        {
            "network": "Network error",
            "timeout": "ETIMEDOUT connection reset",
            "refused": "Connection refused by peer",
            "dns": "getaddrinfo ENOTFOUND server.example.com",
            "fetch": "fetch failed",
            "null": None,
            "empty": "",
        }
    )
    r = _run_node(script)
    assert r.returncode == 0, f"node failed: {r.stderr}"
    results = json.loads(r.stdout.strip())
    for key, val in results.items():
        assert val is False, f"{key} should be retryable, got {val}"


def test_error_matching_case_insensitive():
    """Error matching must be case-insensitive."""
    script = _build_error_check_script(
        {
            "upper_grant": "INVALID_GRANT",
            "mixed": "Invalid_Grant",
            "caps_token": "NO REFRESH TOKEN AVAILABLE",
        }
    )
    r = _run_node(script)
    assert r.returncode == 0, f"node failed: {r.stderr}"
    results = json.loads(r.stdout.strip())
    for key, val in results.items():
        assert val is True, f"{key} should match case-insensitively, got {val}"


def test_retry_mechanism_parameters():
    """performTokenRefreshWithRetry must use correct exponential backoff config."""
    source = REPO / "apps/desktop/src/main/controllers/RemoteServerConfigCtr.ts"
    content = source.read_text()

    assert "performTokenRefreshWithRetry" in content, (
        "performTokenRefreshWithRetry method must exist"
    )
    assert "retries: 3" in content, "Retry count must be 3"
    assert "minTimeout: 1000" in content, "Min backoff must be 1000ms"
    assert "maxTimeout: 4000" in content, "Max backoff must be 4000ms"
    assert "factor: 2" in content, "Backoff factor must be 2"
    assert "async-retry" in content, "async-retry import must be present"


def test_grace_period_in_adapter():
    """adapter.ts must define a 180-second grace period for consumed RefreshTokens."""
    source = REPO / "src/libs/oidc-provider/adapter.ts"
    content = source.read_text()

    assert "REFRESH_TOKEN_GRACE_PERIOD_SECONDS" in content, (
        "REFRESH_TOKEN_GRACE_PERIOD_SECONDS constant must exist"
    )
    assert re.search(r"REFRESH_TOKEN_GRACE_PERIOD_SECONDS\s*=\s*180", content), (
        "Grace period must be 180 seconds"
    )
    assert "gracePeriodEnd" in content, (
        "Grace period comparison logic must be implemented"
    )


def test_is_non_retryable_error_method_exists():
    """RemoteServerConfigCtr must expose isNonRetryableError method for AuthCtr to use."""
    source = REPO / "apps/desktop/src/main/controllers/RemoteServerConfigCtr.ts"
    content = source.read_text()

    # Check method signature exists and is public
    assert "isNonRetryableError(error?: string): boolean" in content, (
        "isNonRetryableError method with correct signature must exist"
    )

    # Verify AuthCtr actually calls this method
    auth_source = REPO / "apps/desktop/src/main/controllers/AuthCtr.ts"
    auth_content = auth_source.read_text()
    assert "isNonRetryableError" in auth_content, (
        "AuthCtr must call isNonRetryableError to decide whether to clear tokens"
    )


# ===================================================================
# f2p — config / documentation update test (REQUIRED)
# ===================================================================


def test_claude_md_in_review_workflow():
    """CLAUDE.md must instruct setting issue status to 'In Review' (not 'Done') when PR is created."""
    claude_md = REPO / "CLAUDE.md"
    content = claude_md.read_text()

    # The updated workflow should say "In Review" when PR is created
    assert '"In Review"' in content or "'In Review'" in content, (
        "CLAUDE.md should instruct setting issue status to 'In Review' when PR is created"
    )
    # Should explain that "Done" is only after merge
    lower = content.lower()
    assert "merged" in lower, (
        "CLAUDE.md should explain that 'Done' status is only after PR is merged"
    )
    # The workflow steps should include creating a PR
    assert "create pr" in lower or "pr if needed" in lower, (
        "Workflow should include creating a PR before updating status"
    )


# ===================================================================
# f2p — dependency check
# ===================================================================


def test_async_retry_dependency():
    """async-retry and @types/async-retry must be added to desktop package.json."""
    pkg = json.loads((REPO / "apps/desktop/package.json").read_text())
    all_deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}

    assert "async-retry" in all_deps, "async-retry must be a dependency"
    assert "@types/async-retry" in all_deps, "@types/async-retry must be a dev dependency"


# ===================================================================
# p2p — pass-to-pass checks (repo CI/CD gates)
# ===================================================================


def test_repo_lint_ts():
    """Repo's TypeScript linting passes (pass_to_pass)."""
    _ensure_deps()
    r = subprocess.run(
        ["pnpm", "run", "lint:ts"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    # Allow warnings but no errors
    assert r.returncode == 0, f"Lint failed:\n{r.stdout[-1000:]}{r.stderr[-500:]}"


def test_repo_desktop_tests():
    """Repo's desktop tests pass (pass_to_pass)."""
    _ensure_deps()
    r = subprocess.run(
        ["pnpm", "test", "--", "--run"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO / "apps/desktop",
    )
    assert r.returncode == 0, f"Desktop tests failed:\n{r.stderr[-500:]}"


def test_repo_desktop_controller_tests():
    """Repo's desktop controller tests (RemoteServerConfigCtr) pass (pass_to_pass)."""
    _ensure_deps()
    r = subprocess.run(
        ["pnpm", "test", "--", "--run", "--silent=passed-only", "src/main/controllers/__tests__/RemoteServerConfigCtr.test.ts"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO / "apps/desktop",
    )
    assert r.returncode == 0, f"Desktop controller tests failed:\n{r.stderr[-500:]}"


def test_repo_oidc_provider_tests():
    """Repo's OIDC provider tests pass (pass_to_pass)."""
    _ensure_deps()
    r = subprocess.run(
        ["npx", "vitest", "run", "--silent=passed-only", "src/libs/oidc-provider/"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"OIDC provider tests failed:\n{r.stderr[-500:]}"


def test_repo_store_tests():
    """Repo's store tests pass (pass_to_pass)."""
    _ensure_deps()
    r = subprocess.run(
        ["npx", "vitest", "run", "--silent=passed-only", "src/store"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Store tests failed:\n{r.stderr[-500:]}"


# ===================================================================
# p2p — pass-to-pass checks (task-specific)
# ===================================================================


def test_typescript_compiles():
    """Modified TypeScript files must compile without errors."""
    # Run TypeScript compiler in noEmit mode to check for syntax errors
    # We check just the desktop package since that's where most changes are
    r = subprocess.run(
        ["npx", "tsc", "--noEmit", "--skipLibCheck"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO / "apps/desktop",
    )
    # Note: We allow non-zero exit codes due to missing dependencies in test environment
    # but we should not see syntax errors in our modified files
    assert "RemoteServerConfigCtr.ts" not in r.stderr, (
        f"RemoteServerConfigCtr.ts has TypeScript errors: {r.stderr}"
    )
    assert "AuthCtr.ts" not in r.stderr, (
        f"AuthCtr.ts has TypeScript errors: {r.stderr}"
    )


def test_auth_ctr_existing_methods_preserved():
    """Core AuthCtr methods must still exist after the changes."""
    source = REPO / "apps/desktop/src/main/controllers/AuthCtr.ts"
    content = source.read_text()

    for method in ["startAutoRefresh", "refreshAccessToken", "initializeAutoRefresh"]:
        assert method in content, f"AuthCtr must still define {method}"


def test_not_stub():
    """isNonRetryableError must have real logic, not just return false."""
    source = REPO / "apps/desktop/src/main/controllers/RemoteServerConfigCtr.ts"
    content = source.read_text()

    # Extract the isNonRetryableError method body - find the whole method
    # The method signature is "isNonRetryableError(error?: string): boolean {"
    # We need to capture everything between the opening { and the matching closing }
    start_match = re.search(r"isNonRetryableError\(error\?: string\): boolean \{", content)
    assert start_match, "Could not find isNonRetryableError method signature"

    start_pos = start_match.end()  # Position right after opening brace

    # Find matching closing brace by counting
    brace_count = 1
    pos = start_pos
    while brace_count > 0 and pos < len(content):
        if content[pos] == '{':
            brace_count += 1
        elif content[pos] == '}':
            brace_count -= 1
        pos += 1

    method_body = content[start_pos:pos-1]  # Exclude the final closing brace

    # Should have actual logic, not just a simple return
    assert "NON_RETRYABLE_OIDC_ERRORS" in method_body, (
        "Method must reference NON_RETRYABLE_OIDC_ERRORS"
    )
    assert "DETERMINISTIC_FAILURES" in method_body, (
        "Method must reference DETERMINISTIC_FAILURES"
    )
    assert ".some(" in method_body, "Method must use array.some() for checking"
