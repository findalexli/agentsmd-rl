"""
Task: vscode-sessions-git-repo-context
Repo: microsoft/vscode @ b15c078a6d22d9d2fd182d80658e6d9a6a1b8559
PR:   306346

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

from pathlib import Path

REPO = Path("/workspace/vscode")
CHANGES_VIEW = REPO / "src/vs/sessions/contrib/changes/browser/changesView.ts"
CODE_REVIEW = REPO / "src/vs/sessions/contrib/codeReview/browser/codeReview.contributions.ts"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — context key definition in changesView.ts
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_has_git_repository_context_key_defined():
    """sessions.hasGitRepository RawContextKey must be defined in changesView.ts."""
    content = CHANGES_VIEW.read_text()
    assert "hasGitRepositoryContextKey" in content, (
        "hasGitRepositoryContextKey not found in changesView.ts"
    )
    assert "'sessions.hasGitRepository'" in content or '"sessions.hasGitRepository"' in content, (
        "Context key string 'sessions.hasGitRepository' not found in changesView.ts"
    )


# [pr_diff] fail_to_pass
def test_context_key_is_raw_context_key_boolean():
    """hasGitRepositoryContextKey must be a RawContextKey<boolean>."""
    content = CHANGES_VIEW.read_text()
    # The constant must be created via new RawContextKey
    assert "RawContextKey" in content, "RawContextKey not used"
    # Find the hasGitRepositoryContextKey definition line
    for line in content.splitlines():
        if "hasGitRepositoryContextKey" in line and "RawContextKey" in line:
            assert "boolean" in line, (
                f"hasGitRepositoryContextKey should be RawContextKey<boolean>, got: {line.strip()}"
            )
            break
    else:
        assert False, "hasGitRepositoryContextKey not defined with RawContextKey"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — context key binding in ChangesViewPane
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_bind_context_key_for_git_repository():
    """bindContextKey must wire hasGitRepositoryContextKey in ChangesViewPane."""
    content = CHANGES_VIEW.read_text()
    assert "bindContextKey(hasGitRepositoryContextKey" in content, (
        "bindContextKey for hasGitRepositoryContextKey not found in changesView.ts"
    )


# [pr_diff] fail_to_pass
def test_git_repository_binding_checks_repository_obs():
    """The hasGitRepository binding must derive from the repository observable."""
    content = CHANGES_VIEW.read_text()
    idx = content.find("bindContextKey(hasGitRepositoryContextKey")
    assert idx != -1, "bindContextKey for hasGitRepositoryContextKey not found"
    # The binding implementation should reference the repository observable within ~400 chars
    block = content[idx : idx + 400]
    assert "activeSessionRepositoryObs" in block or "RepositoryObs" in block, (
        "hasGitRepository binding does not reference the repository observable. "
        f"Block: {block[:200]}"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — codeReview.contributions.ts condition
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_code_review_has_git_repository_condition():
    """codeReview.contributions.ts must include sessions.hasGitRepository condition."""
    content = CODE_REVIEW.read_text()
    assert "sessions.hasGitRepository" in content, (
        "sessions.hasGitRepository not found in codeReview.contributions.ts"
    )


# [pr_diff] fail_to_pass
def test_code_review_git_repo_in_context_key_expr():
    """sessions.hasGitRepository must be in a ContextKeyExpr for the code review when clause."""
    content = CODE_REVIEW.read_text()
    idx = content.find("sessions.hasGitRepository")
    assert idx != -1, "sessions.hasGitRepository not found"
    # It should be inside a ContextKeyExpr call
    block = content[max(0, idx - 300) : idx + 100]
    assert "ContextKeyExpr" in block, (
        "sessions.hasGitRepository is not inside a ContextKeyExpr expression"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — no regressions
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_existing_context_keys_intact():
    """Existing context keys (hasPullRequest, hasOpenPullRequest, etc.) must still be present."""
    content = CHANGES_VIEW.read_text()
    for key in [
        "sessions.hasPullRequest",
        "sessions.hasOpenPullRequest",
        "sessions.hasIncomingChanges",
        "sessions.hasOutgoingChanges",
        "sessions.isolationMode",
    ]:
        assert key in content, f"Existing context key '{key}' was removed from changesView.ts"


# [static] pass_to_pass
def test_code_review_sessions_window_context_intact():
    """IsSessionsWindowContext must still be present in codeReview.contributions.ts."""
    content = CODE_REVIEW.read_text()
    assert "IsSessionsWindowContext" in content, (
        "IsSessionsWindowContext was removed from codeReview.contributions.ts"
    )
