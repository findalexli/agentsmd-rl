"""
Task: vscode-agenthost-session-dispose
Repo: microsoft/vscode @ 3d91bf7907bba3f8f511a70ba352b2006c7b653a
PR:   306574

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/vscode"
HANDLER = (
    f"{REPO}/src/vs/workbench/contrib/chat/browser"
    "/agentSessions/agentHost/agentHostSessionHandler.ts"
)
TEST_FILE = (
    f"{REPO}/src/vs/workbench/contrib/chat/test/browser"
    "/agentSessions/agentHostChatContribution.test.ts"
)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — compilation
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_ts_compile():
    """TypeScript compilation must succeed after changes."""
    r = subprocess.run(
        ["npm", "run", "compile-check-ts-native"],
        cwd=REPO,
        capture_output=True,
        timeout=300,
    )
    assert r.returncode == 0, (
        f"TypeScript compile failed:\n{r.stderr.decode()[:3000]}"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral fix
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_no_dispose_session_on_connection():
    """disposeSession must not be called on the connection in the unsubscribe handler.

    The bug: AgentHostSessionHandler called connection.disposeSession() when
    the UI chat session was disposed, destroying the backend session.
    The fix removes that call while keeping unsubscribe calls intact.

    We verify both that disposeSession is gone AND that the handler block
    was not simply deleted (unsubscribe calls must still be present).
    """
    content = Path(HANDLER).read_text()

    # The handler must still unsubscribe from both client state and connection
    assert "_clientState.unsubscribe(" in content, (
        "Handler is missing _clientState.unsubscribe() — "
        "the unsubscribe block appears to have been deleted entirely"
    )
    assert "_config.connection.unsubscribe(" in content, (
        "Handler is missing connection.unsubscribe() — "
        "the unsubscribe block appears to have been deleted entirely"
    )

    # disposeSession must NOT be called on the connection
    # AST-only because: TypeScript code, cannot execute in Python
    assert "this._config.connection.disposeSession(" not in content, (
        "disposeSession is still called on the connection — "
        "the erroneous call was not removed"
    )


# [pr_diff] fail_to_pass
def test_mock_tracks_disposed_sessions():
    """MockAgentHostService must record disposeSession calls in a trackable array.

    The PR updates the mock so disposeSession() pushes onto a disposedSessions
    array rather than being a no-op, enabling the regression test to verify
    whether disposeSession was called.
    """
    content = Path(TEST_FILE).read_text()

    # Must have a disposedSessions array (declared as property, not just a comment)
    # Matches both `disposedSessions = []` and `disposedSessions: URI[] = []`
    assert re.search(r'disposedSessions\b.*\[\]', content), (
        "MockAgentHostService must declare a disposedSessions array property "
        "to track disposeSession calls"
    )

    # The disposeSession method must push to the array (not remain a no-op)
    assert re.search(
        r'disposeSession.*?\{[^}]*disposedSessions[^}]*\.push',
        content,
        re.DOTALL,
    ), (
        "disposeSession override must push session URIs to disposedSessions — "
        "a no-op stub won't enable the regression test"
    )


# [pr_diff] fail_to_pass
def test_regression_test_asserts_no_dispose():
    """A regression test must assert disposing UI session doesn't dispose backend.

    The test should: create a session, dispose the chat session, then assert
    that disposedSessions has length 0. We check for the actual assertion
    pattern, not just a test description string.
    """
    content = Path(TEST_FILE).read_text()

    # Must assert that disposedSessions.length is 0 after disposal
    has_assertion = re.search(
        r'disposedSessions\s*\.\s*length\s*,\s*0', content
    )
    assert has_assertion, (
        "Missing regression test assertion: must verify "
        "disposedSessions.length === 0 after disposing the chat session"
    )

    # Must actually dispose a chat session before the assertion
    # Look for .dispose() call in the same test block
    has_dispose = re.search(
        r'chatSession\.dispose\(\)|\.dispose\(\).*\n.*disposedSessions',
        content,
        re.DOTALL,
    )
    assert has_dispose, (
        "Regression test must call .dispose() on a chat session "
        "before asserting disposedSessions is empty"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (agent_config) — rules from repo config files
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — .github/skills/sessions/SKILL.md:24 @ 3d91bf7907bba3f8f511a70ba352b2006c7b653a
def test_no_import_from_sessions():
    """vs/workbench files must never import from vs/sessions (one-way dependency rule).

    From sessions/SKILL.md: vs/sessions may import from vs/workbench,
    but vs/workbench must NEVER import from vs/sessions.
    """
    content = Path(HANDLER).read_text()
    bad = re.findall(r"""from\s+['"][^'"]*vs/sessions[^'"]*['"]""", content)
    assert not bad, (
        f"Handler imports from vs/sessions, violating one-way dependency: {bad}"
    )
