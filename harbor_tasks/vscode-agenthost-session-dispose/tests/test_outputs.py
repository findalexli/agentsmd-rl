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
def test_no_dispose_session_called():
    """disposeSession must not be called in the unsubscribe handler.

    The bug: AgentHostSessionHandler was calling disposeSession() when the
    UI chat session was disposed, destroying the backend session. The fix
    removes that erroneous call so the backend session persists.
    """
    content = Path(HANDLER).read_text()
    # The exact line removed by the fix
    assert "this._config.connection.disposeSession(resolvedSession)" not in content, (
        "disposeSession is still called on connection in the unsubscribe handler"
        " — the erroneous disposeSession() call was not removed"
    )


# [pr_diff] fail_to_pass
def test_mock_tracks_disposed_sessions():
    """MockAgentHostService must track disposeSession calls via disposedSessions array.

    The PR updates the mock so tests can verify whether disposeSession was
    called or not. Without this tracking, the behavioral assertion is impossible.
    """
    content = Path(TEST_FILE).read_text()
    assert "disposedSessions" in content, (
        "disposedSessions tracking property not found in MockAgentHostService"
        " — test mock was not updated to record disposeSession calls"
    )


# [pr_diff] fail_to_pass
def test_disposing_chat_does_not_dispose_backend():
    """Test case must assert that disposing the UI session does not dispose the backend.

    The PR adds a regression test with the description:
    'disposing chat session does not call disposeSession on connection'
    """
    content = Path(TEST_FILE).read_text()
    assert (
        "disposing chat session does not call disposeSession on connection" in content
    ), (
        "Required regression test not found:"
        " 'disposing chat session does not call disposeSession on connection'"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (agent_config) — import constraint from repo skill file
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — .github/skills/sessions/SKILL.md:24 @ 3d91bf7907bba3f8f511a70ba352b2006c7b653a
def test_no_import_from_sessions():
    """vs/workbench files must never import from vs/sessions (one-way dependency rule).

    Key constraint from sessions/SKILL.md: vs/sessions may import from
    vs/workbench, but vs/workbench must NEVER import from vs/sessions.
    """
    content = Path(HANDLER).read_text()
    bad = re.findall(r"""from\s+['"][^'"]*vs/sessions[^'"]*['"]""", content)
    assert not bad, (
        f"Handler imports from vs/sessions, violating the one-way import constraint: {bad}"
    )
