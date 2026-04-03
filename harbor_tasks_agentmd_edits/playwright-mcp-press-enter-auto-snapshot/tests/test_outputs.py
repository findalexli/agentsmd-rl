"""
Task: playwright-mcp-press-enter-auto-snapshot
Repo: microsoft/playwright @ 3cdf7ca18324b9a0aa0ec80d818c2f9602b0ef60
PR:   38934

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/playwright"
KEYBOARD_TS = Path(REPO) / "packages/playwright/src/mcp/browser/tools/keyboard.ts"
SKILL_MD = Path(REPO) / "packages/playwright/src/mcp/terminal/SKILL.md"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified TypeScript and Markdown files exist and are non-empty."""
    for f in [KEYBOARD_TS, SKILL_MD]:
        assert f.exists(), f"{f.name} does not exist"
        content = f.read_text()
        assert len(content) > 100, f"{f.name} appears truncated or empty"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_enter_key_has_special_handling():
    """The press handler must branch on Enter key to add wait-for-completion logic."""
    src = KEYBOARD_TS.read_text()

    # Find the press tool's handle function (first handle: async in the file)
    # The press tool is defined first, before pressSequentially
    press_match = re.search(
        r"const press\s*=\s*defineTabTool\(\{.*?handle:\s*async\s*\(.*?\)\s*=>\s*\{(.*?)\n\s*\},\n\}\);",
        src,
        re.DOTALL,
    )
    assert press_match, "Could not find the press tool's handle function"
    press_body = press_match.group(1)

    # Must have conditional logic for Enter key
    assert re.search(r"""['"]Enter['"]""", press_body), \
        "press handler must check for the 'Enter' key specifically"

    # Must use waitForCompletion for Enter
    assert "waitForCompletion" in press_body, \
        "press handler must use waitForCompletion when Enter is pressed"


# [pr_diff] fail_to_pass
def test_enter_key_triggers_snapshot():
    """Pressing Enter must call setIncludeSnapshot so the caller gets an updated page state."""
    src = KEYBOARD_TS.read_text()

    # Find press tool handle body
    press_match = re.search(
        r"const press\s*=\s*defineTabTool\(\{.*?handle:\s*async\s*\(.*?\)\s*=>\s*\{(.*?)\n\s*\},\n\}\);",
        src,
        re.DOTALL,
    )
    assert press_match, "Could not find the press tool's handle function"
    press_body = press_match.group(1)

    assert "setIncludeSnapshot" in press_body, \
        "press handler must call setIncludeSnapshot when Enter is pressed"


# [pr_diff] fail_to_pass
def test_non_enter_keys_still_press_directly():
    """Non-Enter keys should still call page.keyboard.press without waitForCompletion."""
    src = KEYBOARD_TS.read_text()

    press_match = re.search(
        r"const press\s*=\s*defineTabTool\(\{.*?handle:\s*async\s*\(.*?\)\s*=>\s*\{(.*?)\n\s*\},\n\}\);",
        src,
        re.DOTALL,
    )
    assert press_match, "Could not find the press tool's handle function"
    press_body = press_match.group(1)

    # There must be a branch that does the simple press (for non-Enter keys)
    # Check there's both the waitForCompletion path AND a direct press path
    assert press_body.count("keyboard.press") >= 2, \
        "press handler must have separate paths: waitForCompletion for Enter, direct press for other keys"


# ---------------------------------------------------------------------------
# Config file update checks (config_edit) — fail_to_pass
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass

    # Extract the core workflow section
    workflow_match = re.search(
        r"## Core workflow\s*\n(.*?)(?=\n## |\Z)",
        content,
        re.DOTALL,
    )
    assert workflow_match, "Could not find '## Core workflow' section in SKILL.md"
    workflow = workflow_match.group(1)

    # The old workflow had "Snapshot: `playwright-cli snapshot`" as step 2
    # After the fix, there should be no numbered step that says "Snapshot"
    numbered_lines = re.findall(r"^\d+\.\s+(.*)$", workflow, re.MULTILINE)
    for line in numbered_lines:
        assert not re.match(r"Snapshot:", line, re.IGNORECASE), \
            f"Core workflow should not have a separate Snapshot step, found: '{line}'"


# [config_edit] fail_to_pass

    workflow_match = re.search(
        r"## Core workflow\s*\n(.*?)(?=\n## |\Z)",
        content,
        re.DOTALL,
    )
    assert workflow_match, "Could not find '## Core workflow' section in SKILL.md"
    workflow = workflow_match.group(1)

    numbered_steps = re.findall(r"^\d+\.", workflow, re.MULTILINE)
    assert len(numbered_steps) <= 3, \
        f"Core workflow should have at most 3 steps (auto-snapshot removes the need for a manual step), found {len(numbered_steps)}"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub / regression
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_press_tool_still_exported():
    """The press tool must still be part of the default export array."""
    src = KEYBOARD_TS.read_text()
    # The file exports an array including press
    export_match = re.search(r"export default\s*\[([^\]]+)\]", src)
    assert export_match, "keyboard.ts must have a default export array"
    exports = export_match.group(1)
    assert "press" in exports, "press tool must be in the default export"


# [static] pass_to_pass
def test_press_sequentially_submit_unchanged():
    """pressSequentially with submit:true should still waitForCompletion + setIncludeSnapshot."""
    src = KEYBOARD_TS.read_text()
    # Find the pressSequentially handle body
    ps_match = re.search(
        r"const pressSequentially\s*=\s*defineTabTool\(\{.*?handle:\s*async\s*\(.*?\)\s*=>\s*\{(.*?)\n\s*\},\n\}\);",
        src,
        re.DOTALL,
    )
    assert ps_match, "Could not find pressSequentially handle function"
    ps_body = ps_match.group(1)
    assert "waitForCompletion" in ps_body, \
        "pressSequentially must still use waitForCompletion for submit"
    assert "setIncludeSnapshot" in ps_body, \
        "pressSequentially must still call setIncludeSnapshot for submit"
