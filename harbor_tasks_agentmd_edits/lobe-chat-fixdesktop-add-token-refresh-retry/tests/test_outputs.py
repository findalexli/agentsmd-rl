"""Tests for lobehub/lobe-chat#10575: token refresh retry mechanism.

The PR adds retry logic to desktop OIDC token refresh so transient network
errors don't immediately log users out.  It also updates CLAUDE.md to change
the Linear issue workflow from "Done" to "In Review" when a PR is created.
"""

import json
import re
import subprocess
from pathlib import Path

REPO = Path("/workspace/lobe-chat")


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
# p2p — pass-to-pass checks
# ===================================================================


def test_auth_ctr_existing_methods_preserved():
    """Core AuthCtr methods must still exist after the changes."""
    source = REPO / "apps/desktop/src/main/controllers/AuthCtr.ts"
    content = source.read_text()

    for method in ["startAutoRefresh", "refreshAccessToken", "initializeAutoRefresh"]:
        assert method in content, f"AuthCtr must still define {method}"


def test_async_retry_dependency():
    """async-retry must be listed as a dependency in desktop package.json."""
    pkg = json.loads((REPO / "apps/desktop/package.json").read_text())
    all_deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}

    assert "async-retry" in all_deps, "async-retry must be a dependency"
    assert "@types/async-retry" in all_deps, "@types/async-retry must be a dev dependency"
