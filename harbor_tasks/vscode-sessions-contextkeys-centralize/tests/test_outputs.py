"""
Task: vscode-sessions-contextkeys-centralize
Repo: microsoft/vscode @ dfd3b4dcb3884a3de67abfa72adfb54ba462797d

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/vscode"
CONTEXTKEYS     = f"{REPO}/src/vs/sessions/common/contextkeys.ts"
MGMT_SERVICE    = f"{REPO}/src/vs/sessions/contrib/sessions/browser/sessionsManagementService.ts"
COPILOT_ACTIONS = f"{REPO}/src/vs/sessions/contrib/copilotChatSessions/browser/copilotChatSessionsActions.ts"
CHAT_CONTRIB    = f"{REPO}/src/vs/sessions/contrib/chat/browser/chat.contribution.ts"
RUN_SCRIPT      = f"{REPO}/src/vs/sessions/contrib/chat/browser/runScriptAction.ts"
SESSIONS_LIST   = f"{REPO}/src/vs/sessions/contrib/sessions/browser/views/sessionsList.ts"
SESSIONS_TITLE  = f"{REPO}/src/vs/sessions/contrib/sessions/browser/sessionsTitleBarWidget.ts"
VIEW_ACTIONS    = f"{REPO}/src/vs/sessions/contrib/sessions/browser/views/sessionsViewActions.ts"

MODIFIED_FILES = [
    CONTEXTKEYS, MGMT_SERVICE, COPILOT_ACTIONS,
    CHAT_CONTRIB, RUN_SCRIPT, SESSIONS_LIST, SESSIONS_TITLE, VIEW_ACTIONS,
]


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_typescript_compiles():
    """TypeScript compilation must succeed after the refactor."""
    # AST-only would miss type errors; compile instead
    r = subprocess.run(
        ["npm", "run", "compile-check-ts-native"],
        cwd=REPO, capture_output=True, timeout=240,
    )
    assert r.returncode == 0, (
        f"TypeScript compilation failed:\n"
        f"{r.stdout.decode()[-3000:]}\n{r.stderr.decode()[-1000:]}"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_context_keys_centralized():
    """All 6 session context keys must be exported from contextkeys.ts."""
    src = Path(CONTEXTKEYS).read_text()
    expected = [
        "IsNewChatSessionContext",
        "ActiveSessionProviderIdContext",
        "ActiveSessionTypeContext",
        "IsActiveSessionBackgroundProviderContext",
        "ActiveSessionHasGitRepositoryContext",
        "ChatSessionProviderIdContext",
    ]
    missing = [k for k in expected if f"export const {k}" not in src]
    assert not missing, f"Keys missing from contextkeys.ts: {missing}"


# [pr_diff] fail_to_pass
def test_keys_removed_from_management_service():
    """RawContextKey definitions must be removed from sessionsManagementService.ts."""
    src = Path(MGMT_SERVICE).read_text()
    assert "new RawContextKey" not in src, (
        "RawContextKey still locally defined in sessionsManagementService.ts — "
        "keys should be imported from contextkeys.ts instead"
    )


# [pr_diff] fail_to_pass
def test_key_removed_from_copilot_actions():
    """ActiveSessionHasGitRepositoryContext must not be locally defined in copilotChatSessionsActions.ts."""
    src = Path(COPILOT_ACTIONS).read_text()
    assert "new RawContextKey" not in src, (
        "RawContextKey still locally defined in copilotChatSessionsActions.ts — "
        "should import ActiveSessionHasGitRepositoryContext from contextkeys.ts"
    )


# [pr_diff] fail_to_pass
def test_hardcoded_strings_replaced():
    """Hardcoded context key string literals must be replaced with .key property access."""
    copilot_src = Path(COPILOT_ACTIONS).read_text()
    for bad in [
        "ContextKeyExpr.equals('activeSessionType'",
        "ContextKeyExpr.equals('activeSessionProviderId'",
        "ContextKeyExpr.equals('chatSessionProviderId'",
    ]:
        assert bad not in copilot_src, (
            f"Hardcoded string literal still in copilotChatSessionsActions.ts: {bad!r}\n"
            "Use .key property of the centralized context key constant instead."
        )

    for filepath in [SESSIONS_LIST, SESSIONS_TITLE]:
        src = Path(filepath).read_text()
        assert "'chatSessionProviderId'" not in src, (
            f"Hardcoded 'chatSessionProviderId' string still in {filepath} — "
            "use ChatSessionProviderIdContext.key instead"
        )


# [pr_diff] fail_to_pass
def test_consumer_imports_updated():
    """All consumer files must import centralized context keys from contextkeys.js."""
    checks = [
        (CHAT_CONTRIB,    "from '../../../common/contextkeys.js'"),
        (RUN_SCRIPT,      "from '../../../common/contextkeys.js'"),
        (VIEW_ACTIONS,    "from '../../../../common/contextkeys.js'"),
        (COPILOT_ACTIONS, "from '../../../common/contextkeys.js'"),
        (SESSIONS_LIST,   "from '../../../../common/contextkeys.js'"),
        (SESSIONS_TITLE,  "from '../../../common/contextkeys.js'"),
    ]
    for filepath, expected_import in checks:
        src = Path(filepath).read_text()
        assert expected_import in src, (
            f"{filepath} does not import from contextkeys.js — "
            f"expected a line containing: {expected_import}"
        )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from .github/copilot-instructions.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — .github/copilot-instructions.md:89 @ dfd3b4dcb3884a3de67abfa72adfb54ba462797d
def test_no_duplicate_imports():
    """No file should have multiple import statements from the same contextkeys module."""
    # Rule: "Never duplicate imports. Always reuse existing imports if they are present."
    for filepath in [CHAT_CONTRIB, RUN_SCRIPT, VIEW_ACTIONS, COPILOT_ACTIONS, SESSIONS_LIST, SESSIONS_TITLE]:
        src = Path(filepath).read_text()
        lines = src.splitlines()
        contextkey_imports = [
            l for l in lines
            if l.strip().startswith("import") and "contextkeys.js'" in l
        ]
        assert len(contextkey_imports) <= 1, (
            f"Duplicate imports from contextkeys.js in {filepath}:\n" +
            "\n".join(contextkey_imports)
        )


# [agent_config] pass_to_pass — .github/copilot-instructions.md:114 @ dfd3b4dcb3884a3de67abfa72adfb54ba462797d
def test_microsoft_copyright_header():
    """All modified TypeScript files must include the Microsoft copyright header."""
    # Rule: "All files must include Microsoft copyright header"
    for filepath in MODIFIED_FILES:
        src = Path(filepath).read_text()
        # Check in first 500 chars where the header always appears
        assert "Microsoft Corporation" in src[:500], (
            f"Missing Microsoft copyright header in {filepath}"
        )
