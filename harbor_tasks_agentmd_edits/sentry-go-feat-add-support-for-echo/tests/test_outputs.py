"""
Task: sentry-go-feat-add-support-for-echo
Repo: getsentry/sentry-go @ 6ba06389e351fc94be995c2c59382575c88f1b82
PR:   1183

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/sentry-go"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_echo_package_builds():
    """echo package must compile without errors."""
    r = subprocess.run(
        ["go", "build", "./..."],
        cwd=f"{REPO}/echo",
        capture_output=True,
        timeout=120,
    )
    assert r.returncode == 0, (
        f"go build failed:\n{r.stderr.decode()}"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_go_mod_requires_echo_v5():
    """go.mod must depend on echo/v5, not echo/v4."""
    go_mod = Path(f"{REPO}/echo/go.mod").read_text()
    assert "github.com/labstack/echo/v5" in go_mod, (
        "echo/go.mod should require echo/v5"
    )
    assert "github.com/labstack/echo/v4" not in go_mod, (
        "echo/go.mod should not reference echo/v4"
    )


# [pr_diff] fail_to_pass
def test_pointer_context_public_api():
    """Public API functions must accept *echo.Context (pointer), not echo.Context (interface)."""
    src = Path(f"{REPO}/echo/sentryecho.go").read_text()
    # All three public functions must use pointer receiver
    assert "func GetHubFromContext(ctx *echo.Context)" in src, (
        "GetHubFromContext must accept *echo.Context"
    )
    assert "func SetHubOnContext(ctx *echo.Context" in src, (
        "SetHubOnContext must accept *echo.Context"
    )
    assert "func GetSpanFromContext(ctx *echo.Context)" in src, (
        "GetSpanFromContext must accept *echo.Context"
    )


# [pr_diff] fail_to_pass
def test_unwrap_response_for_status():
    """Must use echo.UnwrapResponse to get response status (v5 API change)."""
    src = Path(f"{REPO}/echo/sentryecho.go").read_text()
    assert "UnwrapResponse" in src, (
        "sentryecho.go must use echo.UnwrapResponse for status extraction"
    )
    # Must not use the old v4 pattern of directly accessing ctx.Response().Status
    assert "ctx.Response().Status" not in src, (
        "Must not use ctx.Response().Status directly (v4 pattern)"
    )


# [pr_diff] fail_to_pass
def test_http_status_coder_interface():
    """Must use HTTPStatusCoder interface instead of *echo.HTTPError for error status."""
    src = Path(f"{REPO}/echo/sentryecho.go").read_text()
    assert "HTTPStatusCoder" in src, (
        "sentryecho.go must use echo.HTTPStatusCoder interface"
    )
    assert "*echo.HTTPError" not in src, (
        "Must not use *echo.HTTPError (v4 pattern); use HTTPStatusCoder interface"
    )


# [pr_diff] fail_to_pass
def test_handler_nil_guard_in_tests():
    """Test registration loop must skip nil handlers (v5 panics on nil handler)."""
    test_src = Path(f"{REPO}/echo/sentryecho_test.go").read_text()
    assert "Handler == nil" in test_src or "Handler != nil" in test_src, (
        "sentryecho_test.go must guard against nil handlers in route registration"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — regression
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_echo_tests_pass():
    """Upstream echo test suite must pass."""
    r = subprocess.run(
        ["go", "test", "-count=1", "-timeout=120s", "-v", "./..."],
        cwd=f"{REPO}/echo",
        capture_output=True,
        timeout=180,
    )
    assert r.returncode == 0, (
        f"go test failed:\n{r.stdout.decode()[-2000:]}\n{r.stderr.decode()[-2000:]}"
    )


# ---------------------------------------------------------------------------
# Config-edit — README.md documentation update
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# ---------------------------------------------------------------------------
# Agent config compliance
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — CLAUDE.md:73 @ 6ba06389
