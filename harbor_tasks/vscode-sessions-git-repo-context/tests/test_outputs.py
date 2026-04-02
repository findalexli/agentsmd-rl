"""
Task: vscode-sessions-git-repo-context
Repo: microsoft/vscode @ b15c078a6d22d9d2fd182d80658e6d9a6a1b8559

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = Path("/workspace/vscode")
CHANGES_VIEW = REPO / "src/vs/sessions/contrib/changes/browser/changesView.ts"
SESSIONS_ACTIONS = REPO / "src/vs/sessions/contrib/sessions/browser/views/sessionsViewActions.ts"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — TypeScript compilation
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_typescript_compiles():
    """Modified TypeScript files must compile without errors."""
    r = subprocess.run(
        ["npm", "run", "compile-check-ts-native"],
        cwd=REPO,
        capture_output=True,
        timeout=300,
    )
    assert r.returncode == 0, (
        f"TypeScript compilation failed:\n{r.stderr.decode()[-2000:]}"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — context key definition
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_has_git_repository_context_key_defined():
    """sessions.hasGitRepository RawContextKey must be defined in changesView.ts."""
    content = CHANGES_VIEW.read_text()
    assert "hasGitRepositoryContextKey" in content, (
        "hasGitRepositoryContextKey not found in changesView.ts"
    )
    assert "'sessions.hasGitRepository'" in content, (
        "Context key string 'sessions.hasGitRepository' not found in changesView.ts"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — observable declaration and implementation
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_active_session_has_git_repository_obs_declared():
    """activeSessionHasGitRepositoryObs IObservable<boolean> must be declared in ChangesViewModel."""
    content = CHANGES_VIEW.read_text()
    assert "activeSessionHasGitRepositoryObs" in content, (
        "activeSessionHasGitRepositoryObs not found in changesView.ts"
    )
    assert "IObservable<boolean>" in content, (
        "IObservable<boolean> type not found in changesView.ts"
    )


# [pr_diff] fail_to_pass
def test_active_session_has_git_repository_obs_uses_derived_and_repository_path():
    """activeSessionHasGitRepositoryObs must be implemented via derived() and check repositoryPath."""
    content = CHANGES_VIEW.read_text()
    assert "this.activeSessionHasGitRepositoryObs = derived(" in content, (
        "activeSessionHasGitRepositoryObs not assigned via derived() in changesView.ts"
    )
    # The observable must derive its value from repositoryPath presence
    assert "repositoryPath" in content, (
        "repositoryPath not referenced — implementation must check session metadata.repositoryPath"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — context key binding
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_bind_context_key_for_git_repository():
    """bindContextKey must wire hasGitRepositoryContextKey into ChangesViewPane's scoped context."""
    content = CHANGES_VIEW.read_text()
    assert "bindContextKey(hasGitRepositoryContextKey" in content, (
        "bindContextKey for hasGitRepositoryContextKey not found in changesView.ts"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — markAsDone action presentation
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_mark_as_done_action_presentation():
    """changesView.ts must return showIcon+showLabel presentation for agentSession.markAsDone."""
    content = CHANGES_VIEW.read_text()
    assert "agentSession.markAsDone" in content, (
        "'agentSession.markAsDone' not found in changesView.ts"
    )
    idx = content.index("agentSession.markAsDone")
    surrounding = content[max(0, idx - 50) : idx + 200]
    assert "showIcon" in surrounding, (
        "showIcon not set in the agentSession.markAsDone presentation block"
    )
    assert "showLabel" in surrounding, (
        "showLabel not set in the agentSession.markAsDone presentation block"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — sessionsViewActions.ts changes
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_sessions_window_context_import():
    """IsSessionsWindowContext must be imported in sessionsViewActions.ts."""
    content = SESSIONS_ACTIONS.read_text()
    assert "IsSessionsWindowContext" in content, (
        "IsSessionsWindowContext not imported in sessionsViewActions.ts"
    )


# [pr_diff] fail_to_pass
def test_mark_as_done_menu_registration_with_context_conditions():
    """MarkAsDone must be registered in ChatEditingSessionChangesToolbar with IsSessionsWindowContext and sessions.hasPullRequest."""
    content = SESSIONS_ACTIONS.read_text()
    assert "ChatEditingSessionChangesToolbar" in content, (
        "ChatEditingSessionChangesToolbar registration not found in sessionsViewActions.ts"
    )
    idx = content.index("ChatEditingSessionChangesToolbar")
    surrounding = content[idx : idx + 500]
    assert "IsSessionsWindowContext" in surrounding, (
        "IsSessionsWindowContext condition missing from ChatEditingSessionChangesToolbar block"
    )
    assert "sessions.hasPullRequest" in surrounding, (
        "sessions.hasPullRequest condition missing from ChatEditingSessionChangesToolbar block"
    )
