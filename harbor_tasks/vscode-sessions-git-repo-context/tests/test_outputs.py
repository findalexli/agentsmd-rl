"""
Task: vscode-sessions-git-repo-context
Repo: microsoft/vscode @ b15c078a6d22d9d2fd182d80658e6d9a6a1b8559
PR:   306346

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import json
from pathlib import Path

REPO = Path("/workspace/vscode")
CHANGES_VIEW = REPO / "src/vs/sessions/contrib/changes/browser/changesView.ts"
CODE_REVIEW = REPO / "src/vs/sessions/contrib/codeReview/browser/codeReview.contributions.ts"


def _run_node(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute JavaScript code via Node in the repo directory."""
    return subprocess.run(
        ["node", "-e", code],
        capture_output=True, text=True, timeout=timeout, cwd=str(REPO),
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — context key definition in changesView.ts
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_has_git_repository_context_key_defined():
    """sessions.hasGitRepository RawContextKey must be defined in changesView.ts."""
    r = _run_node("""
const fs = require('fs');
const src = fs.readFileSync('src/vs/sessions/contrib/changes/browser/changesView.ts', 'utf8');

// Must have the constant name
if (!src.includes('hasGitRepositoryContextKey')) {
    console.error('hasGitRepositoryContextKey not found');
    process.exit(1);
}

// Must reference the context key string
if (!src.includes('sessions.hasGitRepository')) {
    console.error('Context key string sessions.hasGitRepository not found');
    process.exit(1);
}

// Must be a RawContextKey instantiation
const lines = src.split('\\n');
let found = false;
for (const line of lines) {
    if (line.includes('hasGitRepositoryContextKey') && line.includes('RawContextKey')) {
        found = true;
        break;
    }
}
if (!found) {
    console.error('hasGitRepositoryContextKey not defined with RawContextKey');
    process.exit(1);
}

console.log('OK');
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "OK" in r.stdout


# [pr_diff] fail_to_pass
def test_context_key_is_raw_context_key_boolean():
    """hasGitRepositoryContextKey must be a RawContextKey<boolean>."""
    r = _run_node("""
const fs = require('fs');
const src = fs.readFileSync('src/vs/sessions/contrib/changes/browser/changesView.ts', 'utf8');
const lines = src.split('\\n');

let found = false;
for (const line of lines) {
    if (line.includes('hasGitRepositoryContextKey') && line.includes('RawContextKey')) {
        if (!line.includes('boolean')) {
            console.error('hasGitRepositoryContextKey should be RawContextKey<boolean>, got: ' + line.trim());
            process.exit(1);
        }
        found = true;
        break;
    }
}
if (!found) {
    console.error('hasGitRepositoryContextKey not defined with RawContextKey');
    process.exit(1);
}

console.log('OK');
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "OK" in r.stdout


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — context key binding in ChangesViewPane
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_bind_context_key_for_git_repository():
    """bindContextKey must wire hasGitRepositoryContextKey in ChangesViewPane."""
    r = _run_node("""
const fs = require('fs');
const src = fs.readFileSync('src/vs/sessions/contrib/changes/browser/changesView.ts', 'utf8');

// Look for bindContextKey call with hasGitRepositoryContextKey
if (!src.includes('bindContextKey(hasGitRepositoryContextKey')) {
    console.error('bindContextKey for hasGitRepositoryContextKey not found');
    process.exit(1);
}

// Must be inside a method (i.e., this.renderDisposables.add context)
const idx = src.indexOf('bindContextKey(hasGitRepositoryContextKey');
const surrounding = src.substring(Math.max(0, idx - 200), idx);
if (!surrounding.includes('renderDisposables')) {
    console.error('bindContextKey call not in renderDisposables context');
    process.exit(1);
}

console.log('OK');
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "OK" in r.stdout


# [pr_diff] fail_to_pass
def test_git_repository_binding_checks_repository_obs():
    """The hasGitRepository binding must derive from the repository observable."""
    r = _run_node("""
const fs = require('fs');
const src = fs.readFileSync('src/vs/sessions/contrib/changes/browser/changesView.ts', 'utf8');

const idx = src.indexOf('bindContextKey(hasGitRepositoryContextKey');
if (idx === -1) {
    console.error('bindContextKey for hasGitRepositoryContextKey not found');
    process.exit(1);
}

// Check the binding block references the repository observable
const block = src.substring(idx, idx + 400);
if (!block.includes('activeSessionRepositoryObs') && !block.includes('RepositoryObs')) {
    console.error('hasGitRepository binding does not reference repository observable');
    process.exit(1);
}

// Must return a boolean check (undefined comparison)
if (!block.includes('undefined')) {
    console.error('Binding does not check for undefined (should return repository !== undefined)');
    process.exit(1);
}

console.log('OK');
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "OK" in r.stdout


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — codeReview.contributions.ts condition
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_code_review_has_git_repository_condition():
    """codeReview.contributions.ts must include sessions.hasGitRepository condition."""
    r = _run_node("""
const fs = require('fs');
const src = fs.readFileSync('src/vs/sessions/contrib/codeReview/browser/codeReview.contributions.ts', 'utf8');

if (!src.includes('sessions.hasGitRepository')) {
    console.error('sessions.hasGitRepository not found in codeReview.contributions.ts');
    process.exit(1);
}

console.log('OK');
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "OK" in r.stdout


# [pr_diff] fail_to_pass
def test_code_review_git_repo_in_context_key_expr():
    """sessions.hasGitRepository must be in a ContextKeyExpr for the code review when clause."""
    r = _run_node("""
const fs = require('fs');
const src = fs.readFileSync('src/vs/sessions/contrib/codeReview/browser/codeReview.contributions.ts', 'utf8');

const idx = src.indexOf('sessions.hasGitRepository');
if (idx === -1) {
    console.error('sessions.hasGitRepository not found');
    process.exit(1);
}

// Verify it's inside a ContextKeyExpr.and() or ContextKeyExpr.equals() block
const preceding = src.substring(Math.max(0, idx - 500), idx);
if (!preceding.includes('ContextKeyExpr')) {
    console.error('sessions.hasGitRepository is not inside a ContextKeyExpr expression');
    process.exit(1);
}

// Must use ContextKeyExpr.equals pattern
const surrounding = src.substring(Math.max(0, idx - 100), idx + 200);
if (!surrounding.includes("ContextKeyExpr.equals")) {
    console.error('sessions.hasGitRepository not used with ContextKeyExpr.equals');
    process.exit(1);
}

// Must be within a 'when' clause context
if (!preceding.includes('when:') && !preceding.includes('when :')) {
    console.error('sessions.hasGitRepository not inside a when clause');
    process.exit(1);
}

console.log('OK');
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "OK" in r.stdout


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
