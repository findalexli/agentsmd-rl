"""
Task: vscode-sessions-archived-view
Repo: microsoft/vscode @ 3d5035e98791181f4fb04962a8a7b127106d2626
PR:   306265

Bug: Clicking an archived session causes the view to immediately bounce back to
the new-session screen because _onSessionsChanged() calls openNewSessionView()
synchronously on every archive-state change.

Fix: Remove the immediate check from _onSessionsChanged; instead add an autorun
observer in setActiveSession() that fires only when the *active* session becomes
archived *after* being opened.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

# AST-only checks throughout: TypeScript cannot be imported/executed in Python.
# Full tsc compilation requires the entire VS Code build graph.

from pathlib import Path

REPO = "/workspace/vscode"
TARGET = Path(f"{REPO}/src/vs/sessions/contrib/sessions/browser/sessionsManagementService.ts")


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core fix checks
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
# AST-only because: TypeScript cannot be executed directly in Python
def test_disposable_store_imported():
    """DisposableStore must be imported from lifecycle.js to manage active session disposables."""
    content = TARGET.read_text()
    lifecycle_lines = [
        ln for ln in content.splitlines()
        if "import" in ln and "lifecycle.js" in ln
    ]
    assert lifecycle_lines, "No import found from lifecycle.js"
    assert any("DisposableStore" in ln for ln in lifecycle_lines), (
        f"DisposableStore not imported from lifecycle.js. Import lines: {lifecycle_lines}"
    )


# [pr_diff] fail_to_pass
# AST-only because: TypeScript cannot be executed directly in Python
def test_autorun_imported():
    """autorun must be imported from observable.js for reactive archive-state observation."""
    content = TARGET.read_text()
    observable_lines = [
        ln for ln in content.splitlines()
        if "import" in ln and "observable.js" in ln
    ]
    assert observable_lines, "No import found from observable.js"
    assert any("autorun" in ln for ln in observable_lines), (
        f"autorun not imported from observable.js. Import lines: {observable_lines}"
    )


# [pr_diff] fail_to_pass
# AST-only because: TypeScript cannot be executed directly in Python
def test_active_session_disposables_field():
    """_activeSessionDisposables DisposableStore field must be registered on the class."""
    content = TARGET.read_text()
    assert "_activeSessionDisposables" in content, (
        "_activeSessionDisposables field not found in file"
    )
    field_lines = [
        ln for ln in content.splitlines()
        if "_activeSessionDisposables" in ln and "DisposableStore" in ln
    ]
    assert field_lines, "_activeSessionDisposables not initialized as a DisposableStore"
    assert any("_register" in ln for ln in field_lines), (
        "_activeSessionDisposables must be registered via this._register() for proper disposal"
    )


# [pr_diff] fail_to_pass
# AST-only because: TypeScript cannot be executed directly in Python
def test_buggy_immediate_archive_check_removed():
    """Immediate isArchived.get() check must be removed from _onSessionsChanged (was the bug source)."""
    content = TARGET.read_text()
    # The buggy code read isArchived via .get() synchronously in _onSessionsChanged
    # and immediately called openNewSessionView() — causing the view to bounce back.
    assert "updated?.isArchived.get()" not in content, (
        "Buggy immediate archive check (updated?.isArchived.get()) still present in "
        "_onSessionsChanged. This triggers openNewSessionView() synchronously, causing "
        "the view flicker when an archived session is clicked."
    )


# [pr_diff] fail_to_pass
# AST-only because: TypeScript cannot be executed directly in Python
def test_early_return_unchanged_session():
    """setActiveSession must early-return when called with the already-active session."""
    content = TARGET.read_text()
    # Guard prevents re-entry when session ID unchanged (avoids redundant disposable churn)
    assert "_activeSession.get()?.sessionId === session?.sessionId" in content, (
        "Missing idempotency guard in setActiveSession: should early-return when the "
        "incoming session is already the active one (prevents disposable churn)"
    )


# [pr_diff] fail_to_pass
# AST-only because: TypeScript cannot be executed directly in Python
def test_archive_state_observed_reactively():
    """Archive state must be watched via autorun so openNewSessionView fires only on change."""
    content = TARGET.read_text()
    assert "session.isArchived.read(reader)" in content, (
        "session.isArchived.read(reader) not found — archive state not observed "
        "reactively. Use autorun so openNewSessionView() fires only when the active "
        "session transitions from unarchived → archived."
    )
    lines = content.splitlines()
    for i, ln in enumerate(lines):
        if "session.isArchived.read(reader)" in ln:
            context = "\n".join(lines[max(0, i - 6) : i + 2])
            assert "autorun" in context, (
                f"session.isArchived.read(reader) found but not inside an autorun block.\n"
                f"Context:\n{context}"
            )
            break


# [pr_diff] fail_to_pass
# AST-only because: TypeScript cannot be executed directly in Python
def test_active_session_disposables_cleared_on_set():
    """_activeSessionDisposables.clear() must be called each time setActiveSession runs."""
    content = TARGET.read_text()
    assert "_activeSessionDisposables.clear()" in content, (
        "_activeSessionDisposables.clear() not called in setActiveSession. "
        "Without this, autorun observers from previous sessions accumulate and "
        "cause stale openNewSessionView() calls."
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (agent_config) — VS Code coding standards
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — .github/copilot-instructions.md:130 @ 3d5035e98791181f4fb04962a8a7b127106d2626
# AST-only because: TypeScript cannot be executed directly in Python
def test_copyright_header():
    """All VS Code files must include the Microsoft copyright header."""
    content = TARGET.read_text()
    header = content[:300]
    assert "Microsoft Corporation" in header, (
        "Microsoft copyright header missing from start of file"
    )
    assert "Licensed under the MIT License" in header, (
        "MIT License notice missing from copyright header"
    )


# [agent_config] pass_to_pass — .github/copilot-instructions.md:72 @ 3d5035e98791181f4fb04962a8a7b127106d2626
# AST-only because: TypeScript cannot be executed directly in Python
def test_tabs_not_spaces():
    """VS Code source files must use tabs for indentation, not spaces."""
    content = TARGET.read_text()
    bad_lines = [
        (i + 1, ln)
        for i, ln in enumerate(content.splitlines())
        if ln.startswith("    ")  # 4+ leading spaces = space-indented
    ]
    assert not bad_lines, (
        f"Found {len(bad_lines)} lines with space indentation (must use tabs). "
        f"First offenders: {bad_lines[:3]}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — structural gate
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_file_parses_as_valid_typescript():
    """Modified file must be syntactically valid (no unclosed braces, broken imports)."""
    # AST-only because: TypeScript cannot be executed directly in Python;
    # full tsc compilation requires the entire VS Code build graph.
    content = TARGET.read_text()
    lines = content.splitlines()
    # Basic structural checks: file is non-empty, has class definition, imports
    assert len(lines) > 100, "File appears truncated or mostly deleted"
    assert "class SessionsManagementService" in content, (
        "SessionsManagementService class definition missing — file may be corrupted"
    )
    # Check brace balance (rough proxy for syntax validity)
    opens = content.count("{")
    closes = content.count("}")
    assert opens == closes, (
        f"Unbalanced braces: {opens} opens vs {closes} closes — likely syntax error"
    )
    # Ensure import section is intact
    import_lines = [ln for ln in lines if ln.strip().startswith("import ")]
    assert len(import_lines) >= 5, (
        f"Expected at least 5 import statements, found {len(import_lines)} — imports may be broken"
    )
