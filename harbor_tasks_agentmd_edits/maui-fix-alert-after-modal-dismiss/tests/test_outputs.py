"""
Task: maui-fix-alert-after-modal-dismiss
Repo: dotnet/maui @ 39325cec7d8a6de66e4608471b7843c7dfe3b4e1
PR:   32872

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/maui"

ALERT_MANAGER_PATH = (
    Path(REPO)
    / "src/Controls/src/Core/Platform/AlertManager/AlertManager.iOS.cs"
)
COPILOT_PATH = Path(REPO) / ".github/copilot-instructions.md"
SKILL_PATH = Path(REPO) / ".github/skills/pr-finalize/SKILL.md"
EXAMPLE_PATH = Path(REPO) / ".github/skills/pr-finalize/references/complete-example.md"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

def test_syntax_check():
    """Modified C# and markdown files have basic syntax sanity."""
    # C# brace balance
    content = ALERT_MANAGER_PATH.read_text()
    opens = content.count("{")
    closes = content.count("}")
    assert opens == closes, (
        f"AlertManager.iOS.cs: unbalanced braces ({opens} open vs {closes} close)"
    )

    # Markdown files should not have leftover merge conflict markers
    for fpath in [COPILOT_PATH, SKILL_PATH, EXAMPLE_PATH]:
        md = fpath.read_text()
        assert "<<<<<<" not in md, f"{fpath.name}: merge conflict marker found"
        assert ">>>>>>" not in md, f"{fpath.name}: merge conflict marker found"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests for the code fix
# ---------------------------------------------------------------------------

def test_isbeingdismissed_check_in_while_loop():
    """GetTopUIViewController must check IsBeingDismissed before following
    the PresentedViewController chain.

    Without this check, during modal dismissal, PresentedViewController
    remains non-null until the animation completes, causing the method to
    return a view controller that is being dismissed. iOS silently ignores
    presentation requests from dismissing view controllers.
    """
    content = ALERT_MANAGER_PATH.read_text()

    # Extract GetTopUIViewController method
    method_match = re.search(
        r"static\s+UIViewController\s+GetTopUIViewController\s*\(",
        content,
    )
    assert method_match, "GetTopUIViewController method not found"

    # Find the while loop in the method
    after_method = content[method_match.start():]
    while_match = re.search(
        r"while\s*\((.*?)\)\s*\{",
        after_method,
        re.DOTALL,
    )
    assert while_match, "while loop not found in GetTopUIViewController"

    condition = while_match.group(1)

    # Must check PresentedViewController is not null
    assert "PresentedViewController" in condition, (
        "While condition must reference PresentedViewController"
    )
    # Must check IsBeingDismissed
    assert "IsBeingDismissed" in condition, (
        "While condition must check IsBeingDismissed to avoid following "
        "dismissing view controllers"
    )
    # Must negate IsBeingDismissed (stop when being dismissed)
    assert re.search(r"!\s*\w+\.IsBeingDismissed", condition), (
        "IsBeingDismissed check must be negated (stop at dismissing VC)"
    )


def test_while_loop_preserves_traversal():
    """The while loop must still traverse the VC hierarchy for normal
    (non-dismissing) presented view controllers.

    The fix should only stop traversal when a VC is being dismissed,
    not remove the traversal entirely.
    """
    content = ALERT_MANAGER_PATH.read_text()

    # Extract the while loop block
    while_match = re.search(
        r"while\s*\(.*?\)\s*\{(.*?)^\t\t\t\t\}",
        content,
        re.DOTALL | re.MULTILINE,
    )
    assert while_match, "while loop block not found"

    body = while_match.group(1)

    # Must still have the traversal assignment
    assert "topUIViewController" in body, (
        "While loop body must still traverse by assigning topUIViewController"
    )
    assert "PresentedViewController" in body, (
        "While loop body must still use PresentedViewController for traversal"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — config/documentation update tests
# ---------------------------------------------------------------------------

def test_copilot_instructions_removes_opening_prs_section():
    """copilot-instructions.md must not have the 'Opening PRs' section
    that required a NOTE block at the top of PR descriptions.

    The NOTE block was an obsolete requirement that has been removed.
    The '### Opening PRs' heading and its NOTE block content should not
    appear in the file.
    """
    content = COPILOT_PATH.read_text()

    assert "### Opening PRs" not in content, (
        "copilot-instructions.md should not have '### Opening PRs' section"
    )
    # The specific NOTE block template should not be present
    assert "test the resulting artifacts" not in content, (
        "copilot-instructions.md should not contain the NOTE block template "
        "about testing PR artifacts"
    )


def test_skill_md_removes_note_from_description_requirements():
    """pr-finalize SKILL.md must not require the NOTE block in PR
    descriptions. The 'Description Requirements' section should list
    steps starting with template sections, not with the NOTE block.
    """
    content = SKILL_PATH.read_text()

    # Find the Description Requirements section
    desc_match = re.search(
        r"## Description Requirements(.*?)(?=\n## |\Z)",
        content,
        re.DOTALL,
    )
    assert desc_match, "## Description Requirements section not found in SKILL.md"

    desc_section = desc_match.group(1)

    # Should NOT mention "Start with the required NOTE block"
    assert "Start with the required NOTE block" not in desc_section, (
        "SKILL.md description requirements should not instruct to start "
        "with the NOTE block"
    )
    # Should NOT contain the NOTE block template in the description example
    assert "test the resulting artifacts" not in desc_section, (
        "SKILL.md description section should not contain the NOTE block template"
    )


def test_complete_example_removes_note_block():
    """complete-example.md must not include the NOTE block in the
    example PR description. The example should start directly with
    the Root Cause or Description of Change section.
    """
    content = EXAMPLE_PATH.read_text()

    # The example should not contain the NOTE block
    assert "test the resulting artifacts" not in content, (
        "complete-example.md should not contain the NOTE block template"
    )
    # The example should still have substantive content
    assert "Root Cause" in content or "Description of Change" in content, (
        "complete-example.md should still contain example PR sections"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub / regression
# ---------------------------------------------------------------------------

def test_existing_alert_manager_logic_intact():
    """The rest of GetTopUIViewController must remain intact — it must
    still return a UIViewController and use RootViewController as the
    starting point.
    """
    content = ALERT_MANAGER_PATH.read_text()

    method_match = re.search(
        r"static\s+UIViewController\s+GetTopUIViewController\s*\(.*?\)\s*\{(.*?)^\t\t\t\t\}",
        content,
        re.DOTALL | re.MULTILINE,
    )
    assert method_match, "GetTopUIViewController method not found"

    body = method_match.group(1)

    assert "RootViewController" in body, (
        "GetTopUIViewController must still start from RootViewController"
    )
    assert "return" in body, (
        "GetTopUIViewController must still return a UIViewController"
    )


def test_copilot_instructions_key_sections_intact():
    """Key sections of copilot-instructions.md must remain intact after
    removing the Opening PRs section. The Code Review Instructions,
    Repository Overview, and Custom Agents sections must still exist.
    """
    content = COPILOT_PATH.read_text()

    assert "## Code Review Instructions" in content, (
        "Code Review Instructions section must remain"
    )
    assert "## Repository Overview" in content, (
        "Repository Overview section must remain"
    )
    assert "## Custom Agents and Skills" in content, (
        "Custom Agents and Skills section must remain"
    )


def test_skill_md_never_approve_rule_intact():
    """The CRITICAL rule about never approving PRs must remain in SKILL.md.
    Removing the NOTE block should not affect this important safety rule.
    """
    content = SKILL_PATH.read_text()

    assert "NEVER" in content and "approve" in content.lower(), (
        "SKILL.md must retain the NEVER approve rule"
    )
    assert "Code Review" in content, (
        "SKILL.md must retain the Code Review section"
    )
