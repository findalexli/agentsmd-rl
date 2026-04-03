"""
Task: workerd-improve-containerclient-tests
Repo: cloudflare/workerd @ e5eaa43c16c57bab977e5b53f4e57ca4418d084d
PR:   6217

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/workerd"
TEST_JS = Path(REPO) / "src/workerd/server/tests/container-client/test.js"
README = Path(REPO) / "src/workerd/server/tests/container-client/README.md"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified JS files must parse without syntax errors."""
    r = subprocess.run(
        ["node", "--check", str(TEST_JS)],
        capture_output=True,
        timeout=30,
    )
    assert r.returncode == 0, (
        f"test.js has syntax errors:\n{r.stderr.decode()}"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_ws_promise_not_wrapped():
    """WebSocket message listener must not be wrapped in a new Promise() constructor."""
    content = TEST_JS.read_text()
    lines = content.split("\n")
    # Find the addEventListener('message') call in testInterceptWebSocket
    # and verify it's NOT wrapped inside a `new Promise((resolve) => { ... })` block
    in_ws_test = False
    for i, line in enumerate(lines):
        if "testInterceptWebSocket" in line:
            in_ws_test = True
        if in_ws_test and "addEventListener" in line and "'message'" in line:
            # Look at the 10 lines before this for a new Promise wrapper
            context = "\n".join(lines[max(0, i - 10):i])
            assert "new Promise" not in context, (
                "WebSocket message listener should not be wrapped in new Promise() — "
                "use Promise.withResolvers() or another modern pattern"
            )
            return
        if in_ws_test and "ws.close()" in line:
            break
    # If addEventListener('message') is gone entirely, the test structure changed
    # which is also acceptable (they may have used a completely different approach)
    assert "addEventListener" in content and "'message'" in content, (
        "testInterceptWebSocket should still listen for WebSocket messages"
    )


# [pr_diff] fail_to_pass
def test_ws_has_timeout():
    """WebSocket test must have a timeout for the WebSocket message wait."""
    content = TEST_JS.read_text()
    lines = content.split("\n")
    # Find the testInterceptWebSocket method and check for a timeout mechanism
    # within that method's body (between its definition and ws.close())
    in_ws_test = False
    has_timeout = False
    for line in lines:
        if "testInterceptWebSocket" in line:
            in_ws_test = True
        if in_ws_test:
            # Look for setTimeout, AbortSignal.timeout, or a timeout variable
            # that guards the WebSocket message promise
            if "setTimeout" in line or "Promise.race" in line:
                has_timeout = True
                break
            if "Websocket message not received" in line or "timed out" in line.lower():
                has_timeout = True
                break
        if in_ws_test and "ws.close()" in line:
            break
    assert has_timeout, (
        "testInterceptWebSocket should have a timeout to avoid hanging when "
        "the WebSocket message is never received"
    )


# [pr_diff] fail_to_pass
def test_verbose_retry_logging_removed():
    """Verbose console.info retry logging should be removed from TCP port retry loop."""
    content = TEST_JS.read_text()
    # The old code had console.info logging the retry attempt with the error message
    # inside the retry loop for getTcpPort
    assert "Retrying getTcpPort" not in content, (
        "Verbose 'Retrying getTcpPort' console.info should be removed"
    )


# ---------------------------------------------------------------------------
# Config edit (config_edit) — README documentation updates
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# ---------------------------------------------------------------------------
# Agent config (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass
