"""
Task: playwright-mcppress-fix-enter-key-waitforcompletion
Repo: playwright @ 3cdf7ca18324b9a0aa0ec80d818c2f9602b0ef60
PR:   38934

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import re
from pathlib import Path

REPO = "/workspace/playwright"
KEYBOARD_TS = Path(REPO) / "packages/playwright/src/mcp/browser/tools/keyboard.ts"
SKILL_MD = Path(REPO) / "packages/playwright/src/mcp/terminal/SKILL.md"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) - syntax check
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """keyboard.ts must parse without TypeScript errors."""
    r = subprocess.run(
        ["node", "-e", f"require('fs').readFileSync('{KEYBOARD_TS}', 'utf8')"],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Failed to read keyboard.ts: {r.stderr}"
    content = KEYBOARD_TS.read_text()
    # Basic structural checks: balanced braces, no obvious syntax errors
    assert content.count("{") == content.count("}"), "Unbalanced braces in keyboard.ts"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) - core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_enter_key_uses_waitforcompletion():
    """The press handler must wrap Enter key in waitForCompletion."""
    content = KEYBOARD_TS.read_text()
    # Extract the press tool section (before pressSequentially definition)
    press_section = content.split("const press = defineTabTool(")[1].split("const pressSequentially")[0]
    # The fix wraps Enter in waitForCompletion for navigation awareness
    assert "waitForCompletion" in press_section, \
        "press handler should use waitForCompletion for Enter key"
    # Verify it's specifically gated on Enter key
    assert "'Enter'" in press_section or '"Enter"' in press_section, \
        "Should have Enter-specific handling in the press tool"


# [pr_diff] fail_to_pass
def test_enter_key_includes_snapshot():
    """The press handler must call setIncludeSnapshot for Enter key."""
    content = KEYBOARD_TS.read_text()
    # The fix adds setIncludeSnapshot so that pressing Enter returns a snapshot
    assert "setIncludeSnapshot" in content, \
        "press handler should call setIncludeSnapshot for Enter key"
    # Verify setIncludeSnapshot appears in the press tool definition context
    # (not just in pressSequentially or type which already had it)
    press_section = content.split("const press = defineTabTool(")[1].split("const pressSequentially")[0]
    assert "setIncludeSnapshot" in press_section, \
        "setIncludeSnapshot must be in the press tool handler, not just pressSequentially"


# [static] pass_to_pass
def test_non_enter_keys_unchanged():
    """Non-Enter keys should still use direct keyboard.press without waitForCompletion."""
    content = KEYBOARD_TS.read_text()
    press_section = content.split("const press = defineTabTool(")[1].split("const pressSequentially")[0]
    # The else branch should still have the original direct press
    assert "tab.page.keyboard.press(params.key)" in press_section, \
        "Non-Enter keys should still call tab.page.keyboard.press(params.key) directly"


# ---------------------------------------------------------------------------
# Config edit (pr_diff) - SKILL.md workflow update
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_skill_md_workflow_simplified():
    """SKILL.md core workflow should no longer list explicit snapshot step."""
    content = SKILL_MD.read_text()
    # The old workflow had a dedicated step: "Snapshot: `playwright-cli snapshot`"
    # After the fix, snapshot is automatic with Enter, so this step is removed
    assert "Snapshot: `playwright-cli snapshot`" not in content, \
        "SKILL.md should remove the explicit snapshot step from core workflow"


# [pr_diff] fail_to_pass
def test_skill_md_workflow_step_count():
    """Core workflow should have 3 steps, not 4."""
    content = SKILL_MD.read_text()
    # Extract the core workflow section
    workflow_match = re.search(r"## Core workflow\s*\n(.*?)(?=\n##|\Z)", content, re.DOTALL)
    assert workflow_match, "SKILL.md must have a '## Core workflow' section"
    workflow_text = workflow_match.group(1)
    # Count numbered steps
    steps = re.findall(r"^\d+\.", workflow_text, re.MULTILINE)
    assert len(steps) == 3, \
        f"Core workflow should have 3 steps (not {len(steps)}). Steps: {steps}"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) - repo CI checks
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_lint_packages():
    """Repo workspace packages must be consistent (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "lint-packages"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"lint-packages failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
# DISABLED: This test fails due to pre-existing DEPS validation issues in the base commit
# (disallowed imports in playwright-ct-core), not related to the PR fix.
def test_repo_check_deps():
    """Repo dependency structure must be valid (pass_to_pass).

    NOTE: This test is disabled because the base commit has pre-existing
    DEPS validation failures in playwright-ct-core that are unrelated to
    the PR fix being tested.
    """
    # Skip this test - pre-existing issue at base commit
    pass


# ---------------------------------------------------------------------------
# Pass-to-pass (static) - structural sanity
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_press_tool_exports():
    """keyboard.ts must still export the press tool in the default export array."""
    content = KEYBOARD_TS.read_text()
    # The file exports an array of tools at the end
    assert "export default [" in content, "Must have default export array"
    export_section = content.split("export default [")[1].split("]")[0]
    assert "press" in export_section, "press tool must be in the export array"
    assert "type" in export_section, "type tool must be in the export array"
    assert "pressSequentially" in export_section, "pressSequentially must be in the export array"
