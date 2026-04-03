"""
Task: vscode-chat-tip-sessions-window
Repo: microsoft/vscode @ 67fdb3ee04fbd04430cd47702977eaa51bd14c40
PR:   306611

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/vscode"
FILE = Path(f"{REPO}/src/vs/workbench/contrib/chat/browser/chatTipCatalog.ts")


def _file_content():
    return FILE.read_text()


def _tip_block():
    """Return the full tip object block for tip.openSessionsWindow."""
    content = _file_content()
    # Find the id line
    idx = content.find("tip.openSessionsWindow")
    if idx == -1:
        return ""
    # Find the opening brace before the id
    start = content.rfind("{", 0, idx)
    if start == -1:
        return ""
    # Find matching closing brace by counting brace depth
    depth = 0
    for i in range(start, len(content)):
        if content[i] == "{":
            depth += 1
        elif content[i] == "}":
            depth -= 1
            if depth == 0:
                return content[start : i + 1]
    # Fallback: grab generous slice
    return content[start : idx + 1200]


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_tip_id_exists():
    """TIP_CATALOG must contain a tip with id 'tip.openSessionsWindow'."""
    content = _file_content()
    assert "'tip.openSessionsWindow'" in content, (
        "tip.openSessionsWindow tip ID not found in TIP_CATALOG"
    )


# [pr_diff] fail_to_pass
def test_tip_tier_qol():
    """The sessions window tip must have tier ChatTipTier.Qol."""
    block = _tip_block()
    assert block, "tip.openSessionsWindow block not found"
    assert "ChatTipTier.Qol" in block, (
        "Sessions window tip must have tier ChatTipTier.Qol"
    )


# [pr_diff] fail_to_pass
def test_command_link_present():
    """buildMessage must link to workbench.action.openSessionsWindow."""
    block = _tip_block()
    assert block, "tip.openSessionsWindow block not found"
    assert "command:workbench.action.openSessionsWindow" in block, (
        "Tip message must contain a command link to workbench.action.openSessionsWindow"
    )


# [pr_diff] fail_to_pass
def test_command_link_descriptive_title():
    """Command link must include the title 'Open Sessions Window'."""
    block = _tip_block()
    assert block, "tip.openSessionsWindow block not found"
    # The markdown link title should contain "Open Sessions Window"
    assert "Open Sessions Window" in block, (
        "Command link must include descriptive title 'Open Sessions Window'"
    )


# [pr_diff] fail_to_pass
def test_exclude_when_commands_executed():
    """Tip must be excluded once the sessions window command is executed."""
    block = _tip_block()
    assert block, "tip.openSessionsWindow block not found"
    assert "excludeWhenCommandsExecuted" in block, (
        "Missing excludeWhenCommandsExecuted property"
    )
    assert "workbench.action.openSessionsWindow" in block, (
        "excludeWhenCommandsExecuted must reference workbench.action.openSessionsWindow"
    )


# [pr_diff] fail_to_pass
def test_dismiss_when_commands_clicked():
    """Tip must be dismissed once the sessions window command is clicked."""
    block = _tip_block()
    assert block, "tip.openSessionsWindow block not found"
    assert "dismissWhenCommandsClicked" in block, (
        "Missing dismissWhenCommandsClicked property"
    )


# [pr_diff] fail_to_pass
def test_when_clause_non_stable():
    """Tip must only appear on non-stable builds via ProductQualityContext."""
    block = _tip_block()
    assert block, "tip.openSessionsWindow block not found"
    assert "ProductQualityContext" in block, (
        "when clause must reference ProductQualityContext"
    )
    assert re.search(r"notEqualsTo\(['\"]stable['\"]\)", block), (
        "when clause must include ProductQualityContext.notEqualsTo('stable')"
    )


# [pr_diff] fail_to_pass
def test_when_clause_not_sessions_window():
    """Tip must be hidden when the user is already in a Sessions Window."""
    block = _tip_block()
    assert block, "tip.openSessionsWindow block not found"
    assert "IsSessionsWindowContext" in block, (
        "when clause must reference IsSessionsWindowContext"
    )
    assert "negate()" in block, (
        "when clause must negate IsSessionsWindowContext"
    )


# [pr_diff] fail_to_pass
def test_required_imports():
    """ProductQualityContext and IsSessionsWindowContext must be imported."""
    content = _file_content()
    assert re.search(r"import\s*\{[^}]*ProductQualityContext[^}]*\}", content), (
        "Missing import for ProductQualityContext"
    )
    assert re.search(r"import\s*\{[^}]*IsSessionsWindowContext[^}]*\}", content), (
        "Missing import for IsSessionsWindowContext"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — regression
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_existing_tips_preserved():
    """Pre-existing tip IDs in TIP_CATALOG must still be present."""
    content = _file_content()
    expected_tips = [
        "tip.switchToAuto",
        "tip.createPrompt",
        "tip.planMode",
        "tip.attachFiles",
        "tip.subagents",
    ]
    for tip_id in expected_tips:
        assert tip_id in content, f"Existing tip removed: {tip_id}"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from .github/copilot-instructions.md
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — .github/copilot-instructions.md:83 @ 67fdb3ee04fbd04430cd47702977eaa51bd14c40
def test_user_facing_string_localized():
    """User-facing tip message must use localize() from vs/nls."""
    block = _tip_block()
    assert block, "tip.openSessionsWindow block not found"
    assert "localize(" in block, (
        "User-facing strings must be externalized using localize() (copilot-instructions.md)"
    )


# [agent_config] fail_to_pass — .github/copilot-instructions.md:62 @ 67fdb3ee04fbd04430cd47702977eaa51bd14c40
def test_uses_tabs_not_spaces():
    """New code must use tabs for indentation, not spaces."""
    content = _file_content()
    idx = content.find("tip.openSessionsWindow")
    if idx == -1:
        raise AssertionError("tip.openSessionsWindow not found")
    # Get lines around the tip block
    start = content.rfind("{", 0, idx)
    end = content.find("}", idx)
    if start == -1 or end == -1:
        raise AssertionError("Could not find tip block boundaries")
    block_lines = content[start:end].split("\n")
    indented = [l for l in block_lines if l and l[0] in (" ", "\t")]
    assert indented, "No indented lines found in tip block"
    space_indented = [l for l in indented if l[0] == " "]
    assert not space_indented, (
        f"Must use tabs, not spaces for indentation (copilot-instructions.md). "
        f"Found {len(space_indented)} space-indented lines"
    )


# [agent_config] fail_to_pass — .github/copilot-instructions.md:119 @ 67fdb3ee04fbd04430cd47702977eaa51bd14c40
def test_no_duplicate_imports():
    """Never duplicate imports — reuse existing imports if present."""
    content = _file_content()
    import_lines = [l.strip() for l in content.split("\n") if l.strip().startswith("import ")]
    # Check no two import lines are identical
    seen = set()
    for line in import_lines:
        assert line not in seen, (
            f"Duplicate import found: {line} (copilot-instructions.md)"
        )
        seen.add(line)
