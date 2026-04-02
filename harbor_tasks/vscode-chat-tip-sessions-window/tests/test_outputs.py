"""
Task: vscode-chat-tip-sessions-window
Repo: microsoft/vscode @ 67fdb3ee04fbd04430cd47702977eaa51bd14c40

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

from pathlib import Path

REPO = "/workspace/vscode"
FILE = Path(f"{REPO}/src/vs/workbench/contrib/chat/browser/chatTipCatalog.ts")


def _file_content():
    return FILE.read_text()


def _tip_block():
    """Return ~600 chars of content starting at tip.openSessionsWindow."""
    content = _file_content()
    idx = content.find("tip.openSessionsWindow")
    if idx == -1:
        return ""
    # include some context before the id line and enough after for all fields
    start = max(0, content.rfind("{", 0, idx) - 2)
    return content[start : idx + 600]


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_tip_id_exists():
    """TIP_CATALOG must contain a tip with id 'tip.openSessionsWindow'."""
    content = _file_content()
    assert "id: 'tip.openSessionsWindow'" in content, (
        "tip.openSessionsWindow tip ID not found in TIP_CATALOG"
    )


# [pr_diff] fail_to_pass
def test_tip_tier_qol():
    """The sessions window tip must have tier ChatTipTier.Qol."""
    block = _tip_block()
    assert block, "tip.openSessionsWindow block not found"
    assert "tier: ChatTipTier.Qol" in block, (
        "Sessions window tip must have tier: ChatTipTier.Qol"
    )


# [pr_diff] fail_to_pass
def test_command_link_present():
    """buildMessage must link to workbench.action.openSessionsWindow."""
    block = _tip_block()
    assert block, "tip.openSessionsWindow block not found"
    assert "workbench.action.openSessionsWindow" in block, (
        "Tip must reference command workbench.action.openSessionsWindow"
    )


# [pr_diff] fail_to_pass
def test_command_link_descriptive_title():
    """Command link must include the title 'Open Sessions Window'."""
    block = _tip_block()
    assert block, "tip.openSessionsWindow block not found"
    assert '"Open Sessions Window"' in block, (
        "Command link must include descriptive title 'Open Sessions Window'"
    )


# [pr_diff] fail_to_pass
def test_exclude_when_commands_executed():
    """Tip must be excluded once the sessions window command is executed."""
    block = _tip_block()
    assert block, "tip.openSessionsWindow block not found"
    assert "excludeWhenCommandsExecuted: ['workbench.action.openSessionsWindow']" in block, (
        "Missing excludeWhenCommandsExecuted: ['workbench.action.openSessionsWindow']"
    )


# [pr_diff] fail_to_pass
def test_dismiss_when_commands_clicked():
    """Tip must be dismissed once the sessions window command is clicked."""
    block = _tip_block()
    assert block, "tip.openSessionsWindow block not found"
    assert "dismissWhenCommandsClicked: ['workbench.action.openSessionsWindow']" in block, (
        "Missing dismissWhenCommandsClicked: ['workbench.action.openSessionsWindow']"
    )


# [pr_diff] fail_to_pass
def test_when_clause_non_stable():
    """Tip must only appear on non-stable builds via ProductQualityContext."""
    block = _tip_block()
    assert block, "tip.openSessionsWindow block not found"
    assert "ProductQualityContext.notEqualsTo" in block, (
        "when clause must include ProductQualityContext.notEqualsTo('stable')"
    )


# [pr_diff] fail_to_pass
def test_when_clause_not_sessions_window():
    """Tip must be hidden when the user is already in a Sessions Window."""
    block = _tip_block()
    assert block, "tip.openSessionsWindow block not found"
    assert "IsSessionsWindowContext.negate()" in block, (
        "when clause must include IsSessionsWindowContext.negate()"
    )


# [pr_diff] fail_to_pass
def test_required_imports():
    """ProductQualityContext and IsSessionsWindowContext must be imported."""
    content = _file_content()
    assert "import { ProductQualityContext }" in content, (
        "Missing import for ProductQualityContext"
    )
    assert "import { IsSessionsWindowContext }" in content, (
        "Missing import for IsSessionsWindowContext"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — regression
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_existing_tips_preserved():
    """Pre-existing tip IDs in TIP_CATALOG must still be present."""
    content = _file_content()
    for tip_id in [
        "id: 'tip.createAgentInstructions'",
        "id: 'tip.agentMode'",
        "id: 'tip.createPrompt'",
    ]:
        assert tip_id in content, f"Existing tip removed: {tip_id}"
