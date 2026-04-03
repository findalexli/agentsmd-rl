"""
Task: playwright-mcp-skill-mode-commands
Repo: microsoft/playwright @ 1e81675f850280d2cbaa0bbb01a7f066532d0e01
PR:   38932

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import re
from pathlib import Path

REPO = "/workspace/playwright"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified TypeScript files must parse without syntax errors."""
    files = [
        "packages/playwright/src/mcp/browser/config.ts",
        "packages/playwright/src/mcp/browser/response.ts",
        "packages/playwright/src/mcp/browser/tab.ts",
        "packages/playwright/src/mcp/browser/tools/evaluate.ts",
        "packages/playwright/src/mcp/browser/tools/tool.ts",
        "packages/playwright/src/mcp/program.ts",
        "packages/playwright/src/mcp/terminal/commands.ts",
    ]
    for f in files:
        p = Path(REPO) / f
        assert p.exists(), f"{f} must exist"
        content = p.read_text()
        # Basic syntax: balanced braces (rough check for TS)
        assert content.count("{") == content.count("}"), (
            f"{f} has unbalanced braces"
        )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_command_names_renamed():
    """Terminal commands must use short names: press, keydown, keyup,
    mousemove, mousedown, mouseup, mousewheel (no hyphens)."""
    commands_ts = Path(REPO) / "packages/playwright/src/mcp/terminal/commands.ts"
    content = commands_ts.read_text()

    # New names must be present as declared command names
    new_names = ["'press'", "'keydown'", "'keyup'", "'mousemove'", "'mousedown'", "'mouseup'", "'mousewheel'"]
    for name in new_names:
        assert f"name: {name}" in content, (
            f"commands.ts should declare command with name: {name}"
        )

    # Old hyphenated names must NOT be declared
    old_names = ["'key-press'", "'key-down'", "'key-up'", "'mouse-move'", "'mouse-down'", "'mouse-up'", "'mouse-wheel'"]
    for name in old_names:
        assert f"name: {name}" not in content, (
            f"commands.ts should not still use old name: {name}"
        )


# [pr_diff] fail_to_pass
def test_modal_state_cleared_by_is_object():
    """The ModalState clearedBy field must be an object type
    { tool: string; skill: string }, not a plain string."""
    tool_ts = Path(REPO) / "packages/playwright/src/mcp/browser/tools/tool.ts"
    content = tool_ts.read_text()

    # The type definition should have clearedBy as an object with tool and skill
    assert "clearedBy: { tool: string; skill: string }" in content or \
           "clearedBy: {tool: string; skill: string}" in content or \
           ("clearedBy:" in content and "tool: string" in content and "skill: string" in content), \
        "tool.ts clearedBy must be typed as { tool: string; skill: string }"

    # It must NOT be typed as just 'string'
    # Match "clearedBy: string" but not "clearedBy: { tool: string..."
    lines = content.split("\n")
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("clearedBy:") and "string" in stripped:
            assert "{" in stripped, (
                f"clearedBy must be an object type, not plain string: {stripped}"
            )


# [pr_diff] fail_to_pass
def test_render_modal_states_accepts_config():
    """renderModalStates function must accept a config parameter."""
    tab_ts = Path(REPO) / "packages/playwright/src/mcp/browser/tab.ts"
    content = tab_ts.read_text()

    # Function signature should include config parameter
    # Match: export function renderModalStates(config: FullConfig, modalStates: ModalState[])
    assert re.search(
        r"function\s+renderModalStates\s*\(\s*config\s*:", content
    ), "renderModalStates must accept config as first parameter"

    # Should use config.skillMode to determine output format
    assert "config.skillMode" in content or "skillMode" in content, (
        "renderModalStates should use skillMode from config"
    )


# [pr_diff] fail_to_pass
def test_render_modal_uses_skill_name():
    """When skillMode is active, modal state message should use the skill name
    instead of the tool name."""
    tab_ts = Path(REPO) / "packages/playwright/src/mcp/browser/tab.ts"
    content = tab_ts.read_text()

    # The rendering must reference .skill for skill mode output
    assert "clearedBy.skill" in content or "state.clearedBy.skill" in content, (
        "renderModalStates should use clearedBy.skill in skill mode"
    )
    # And .tool for non-skill mode
    assert "clearedBy.tool" in content or "state.clearedBy.tool" in content, (
        "renderModalStates should use clearedBy.tool in non-skill mode"
    )


# [pr_diff] fail_to_pass
def test_eval_auto_wraps_expression():
    """evaluate tool must auto-wrap expressions that don't contain '=>'
    into an arrow function."""
    evaluate_ts = Path(REPO) / "packages/playwright/src/mcp/browser/tools/evaluate.ts"
    content = evaluate_ts.read_text()

    # Check for the arrow-wrapping logic
    assert "=>" in content, "evaluate.ts must reference arrow syntax"

    # The wrapping pattern: if no => in function, wrap it
    assert re.search(r"!.*includes\s*\(\s*['\"]=>['\"]\s*\)", content) or \
           re.search(r"indexOf\s*\(\s*['\"]=>['\"]\s*\)", content), \
        "evaluate.ts must check if function param contains '=>'"

    # Should wrap in arrow function like: () => (expression)
    assert "() =>" in content or "`() =>" in content or \
           "=> (" in content, \
        "evaluate.ts must wrap non-arrow expressions in () => (...)"


# [pr_diff] fail_to_pass
def test_help_json_uses_new_command_names():
    """help.json must reference the new command names (press, keydown, etc.)
    instead of the old hyphenated names (key-press, key-down, etc.)."""
    help_json = Path(REPO) / "packages/playwright/src/mcp/terminal/help.json"
    content = help_json.read_text()
    data = json.loads(content)

    # New command names must be keys in commands object
    commands = data.get("commands", {})
    for name in ["press", "keydown", "keyup", "mousemove", "mousedown", "mouseup", "mousewheel"]:
        assert name in commands, f"help.json commands must include '{name}'"

    # Old names must be gone
    for name in ["key-press", "key-down", "key-up", "mouse-move", "mouse-down", "mouse-up", "mouse-wheel"]:
        assert name not in commands, f"help.json commands must not include old name '{name}'"


# [pr_diff] fail_to_pass


# ---------------------------------------------------------------------------
# Config edit (config_edit) — SKILL.md creation
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass

    content = skill_md.read_text()
    # Must have YAML frontmatter
    assert content.startswith("---"), "SKILL.md must start with YAML frontmatter"
    assert content.count("---") >= 2, "SKILL.md must have opening and closing frontmatter"

    # Frontmatter must include name and description
    frontmatter_end = content.index("---", 3)
    frontmatter = content[3:frontmatter_end]
    assert "name:" in frontmatter, "SKILL.md frontmatter must include name"
    assert "description:" in frontmatter, "SKILL.md frontmatter must include description"


# [config_edit] fail_to_pass

    content = skill_md.read_text()

    # Must document the new command names
    for cmd in ["press", "keydown", "keyup", "mousemove", "mousedown", "mouseup", "mousewheel"]:
        assert f"playwright-cli {cmd}" in content or f" {cmd} " in content or f" {cmd}\n" in content, (
            f"SKILL.md must document the '{cmd}' command"
        )

    # Must cover core workflow concepts
    assert "snapshot" in content.lower(), "SKILL.md should mention snapshot workflow"
    assert "open" in content, "SKILL.md should document the open command"
    assert "click" in content, "SKILL.md should document the click command"


# [config_edit] fail_to_pass

    content = skill_md.read_text().lower()

    # Must cover multiple categories
    categories_found = 0
    for category in ["keyboard", "mouse", "navigation", "tab", "screenshot", "session"]:
        if category in content:
            categories_found += 1

    assert categories_found >= 4, (
        f"SKILL.md should cover at least 4 command categories, found {categories_found}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass — build script
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_build_script_copies_md_files():
    """Build script must copy .md files from terminal directory."""
    build_js = Path(REPO) / "utils/build/build.js"
    content = build_js.read_text()

    assert "terminal" in content and "*.md" in content, (
        "build.js must copy terminal/*.md files"
    )
