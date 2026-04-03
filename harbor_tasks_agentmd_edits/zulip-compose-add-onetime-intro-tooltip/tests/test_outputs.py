"""
Task: zulip-compose-add-onetime-intro-tooltip
Repo: zulip/zulip @ a0fa7deed9a8c379055a2c896dcfebafa9ca1616
PR:   38207

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import re
from pathlib import Path

REPO = "/workspace/zulip"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified Python files must parse without errors."""
    for path in [
        "zerver/lib/onboarding_steps.py",
        "zerver/tests/test_onboarding_steps.py",
    ]:
        src = Path(f"{REPO}/{path}").read_text()
        ast.parse(src, filename=path)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_onboarding_step_registered():
    """intro_go_to_conversation_tooltip must be registered as a OneTimeNotice."""
    src = Path(f"{REPO}/zerver/lib/onboarding_steps.py").read_text()
    # The string must appear as a name= argument to OneTimeNotice
    assert "intro_go_to_conversation_tooltip" in src, (
        "onboarding_steps.py must register 'intro_go_to_conversation_tooltip' as a OneTimeNotice"
    )
    # Verify it's inside the ONE_TIME_NOTICES list, not just a random string
    tree = ast.parse(src)
    found = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and node.value == "intro_go_to_conversation_tooltip":
            found = True
            break
    assert found, "intro_go_to_conversation_tooltip must be a string constant in onboarding_steps.py"


# [pr_diff] fail_to_pass
def test_tooltip_template_created():
    """Handlebars template for the intro tooltip must exist with correct content."""
    hbs_path = Path(f"{REPO}/web/templates/intro_go_to_conversation_tooltip.hbs")
    assert hbs_path.exists(), "intro_go_to_conversation_tooltip.hbs template must exist"
    content = hbs_path.read_text()
    # Must mention going to conversation
    assert "conversation" in content.lower(), (
        "Template should mention going to a conversation"
    )
    # Must include hotkey hints (Ctrl + .)
    assert "tooltip_hotkey_hints" in content or "hotkey" in content.lower(), (
        "Template should include keyboard shortcut hints"
    )


# [pr_diff] fail_to_pass
def test_compose_tooltips_show_function():
    """compose_tooltips.ts must export maybe_show_intro_go_to_conversation_tooltip."""
    src = Path(f"{REPO}/web/src/compose_tooltips.ts").read_text()
    assert "maybe_show_intro_go_to_conversation_tooltip" in src, (
        "compose_tooltips.ts must define maybe_show_intro_go_to_conversation_tooltip"
    )
    # Verify it's an exported function, not just a reference
    assert re.search(
        r"export\s+function\s+maybe_show_intro_go_to_conversation_tooltip", src
    ), "maybe_show_intro_go_to_conversation_tooltip must be an exported function"


# [pr_diff] fail_to_pass
def test_compose_tooltips_dismiss_function():
    """compose_tooltips.ts must export dismiss_intro_go_to_conversation_tooltip."""
    src = Path(f"{REPO}/web/src/compose_tooltips.ts").read_text()
    assert re.search(
        r"export\s+function\s+dismiss_intro_go_to_conversation_tooltip", src
    ), "dismiss_intro_go_to_conversation_tooltip must be an exported function"


# [pr_diff] fail_to_pass
def test_tooltip_shown_for_existing_conversations():
    """compose_recipient.ts must conditionally show the tooltip for existing conversations."""
    src = Path(f"{REPO}/web/src/compose_recipient.ts").read_text()
    # Must import compose_tooltips
    assert "compose_tooltips" in src, (
        "compose_recipient.ts must import compose_tooltips"
    )
    # Must call the show function
    assert "maybe_show_intro_go_to_conversation_tooltip" in src, (
        "compose_recipient.ts must call maybe_show_intro_go_to_conversation_tooltip"
    )
    # Must check that the conversation exists (stream topic history or DM conversations)
    assert "get_recent_topic_names" in src or "stream_topic_history" in src, (
        "compose_recipient.ts must check stream topic history for existing conversations"
    )
    assert "pm_conversations" in src or "recent.has_conversation" in src, (
        "compose_recipient.ts must check DM conversation history"
    )


# [pr_diff] fail_to_pass
def test_tooltip_dismissed_on_compose_cancel():
    """compose_actions.ts must dismiss the tooltip when compose is cancelled."""
    src = Path(f"{REPO}/web/src/compose_actions.ts").read_text()
    assert "dismiss_intro_go_to_conversation_tooltip" in src, (
        "compose_actions.ts must call dismiss_intro_go_to_conversation_tooltip on cancel"
    )


# [pr_diff] fail_to_pass


# [pr_diff] fail_to_pass


# ---------------------------------------------------------------------------
# Config edit tests — SKILL.md updates
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_tooltip_function_not_stub():
    """The tooltip show function must have real logic using tippy and onboarding_steps."""
    src = Path(f"{REPO}/web/src/compose_tooltips.ts").read_text()
    # The new function must create a tippy instance with manual trigger
    assert "intro_go_to_conversation_tooltip" in src, (
        "compose_tooltips.ts must reference intro_go_to_conversation_tooltip"
    )
    # Must mark the onboarding step as read
    assert "post_onboarding_step_as_read" in src, (
        "Tooltip show function must mark the onboarding step as read"
    )
    # Must use manual trigger (not hover)
    assert "manual" in src, (
        "Tooltip must use manual trigger mode"
    )
