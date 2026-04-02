"""
Task: vscode-remote-agent-host-model-picker
Repo: microsoft/vscode @ de413b282f0b15a6618a15a79d4680b720ef9dc8

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

from pathlib import Path

REPO = "/workspace/vscode"
ACTIONS_FILE = Path(f"{REPO}/src/vs/sessions/contrib/copilotChatSessions/browser/copilotChatSessionsActions.ts")
REMOTE_FILE = Path(f"{REPO}/src/vs/sessions/contrib/remoteAgentHost/browser/remoteAgentHost.contribution.ts")


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral fixes
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_context_key_uses_constant():
    """IsActiveSessionRemoteAgentHost must use ActiveSessionProviderIdContext.key, not a hardcoded string."""
    content = ACTIONS_FILE.read_text()
    # The constant form must be present
    assert "ContextKeyExpr.regex(ActiveSessionProviderIdContext.key" in content, \
        "IsActiveSessionRemoteAgentHost should use ActiveSessionProviderIdContext.key not a string literal"
    # No line should mix IsActiveSessionRemoteAgentHost with a raw string literal
    for line in content.splitlines():
        if "IsActiveSessionRemoteAgentHost" in line and "ContextKeyExpr.regex" in line:
            assert "'activeSessionProviderId'" not in line, \
                f"IsActiveSessionRemoteAgentHost still uses hardcoded string literal: {line.strip()}"


# [pr_diff] fail_to_pass
def test_no_hardcoded_provider_id_in_regex():
    """ContextKeyExpr.regex must not be called with the hardcoded 'activeSessionProviderId' string."""
    content = ACTIONS_FILE.read_text()
    assert "ContextKeyExpr.regex('activeSessionProviderId'" not in content, \
        "ContextKeyExpr.regex should use ActiveSessionProviderIdContext.key, not the raw string"


# [pr_diff] fail_to_pass
def test_refresh_models_after_new_connection():
    """refreshModels() must be chained after _authenticateWithConnection for new connections."""
    content = REMOTE_FILE.read_text()
    assert (
        "_authenticateWithConnection(loggedConnection).then(() => loggedConnection.refreshModels())" in content
    ), "_authenticateWithConnection must chain .then(() => loggedConnection.refreshModels())"


# [pr_diff] fail_to_pass
def test_authenticate_all_connections_refresh():
    """_authenticateAllConnections must chain refreshModels() after each authentication."""
    content = REMOTE_FILE.read_text()
    assert "connState.loggedConnection.refreshModels()" in content, \
        "_authenticateAllConnections should chain connState.loggedConnection.refreshModels()"


# [pr_diff] fail_to_pass
def test_coalesce_import_present():
    """coalesce must be imported from arrays.js in the actions file."""
    content = ACTIONS_FILE.read_text()
    assert "import { coalesce } from '../../../../base/common/arrays.js'" in content, \
        "coalesce import missing — needed for multi-select session bridge"


# [pr_diff] fail_to_pass
def test_context_menu_bridge_supports_arrays():
    """CommandsRegistry handler in bridge must accept ISession | ISession[] for multi-select."""
    content = ACTIONS_FILE.read_text()
    assert "context?: ISession | ISession[]" in content, \
        "Context menu bridge should support ISession | ISession[] not just ISession"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression / anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_authenticate_function_intact():
    """_authenticateWithConnection and _authenticateAllConnections must still exist (not deleted)."""
    content = REMOTE_FILE.read_text()
    assert "_authenticateWithConnection" in content, \
        "_authenticateWithConnection should still be defined"
    assert "private _authenticateAllConnections" in content, \
        "_authenticateAllConnections should still be defined"


# [static] pass_to_pass
def test_bridge_class_uses_agent_session_service():
    """agentSessionsService.getSession must still be called in the context menu bridge (no regression)."""
    content = ACTIONS_FILE.read_text()
    assert "agentSessionsService.getSession" in content, \
        "agentSessionsService.getSession should still be called in CopilotSessionContextMenuBridge"
