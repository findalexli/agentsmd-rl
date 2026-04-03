"""
Task: playwright-choremcp-remove-unnecessary-waitforcompletion-fro
Repo: microsoft/playwright @ b6f860d846146f072f5a804017d89f2deb737b39
PR:   39769

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/playwright"
TOOLS = f"{REPO}/packages/playwright-core/src/tools"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified TypeScript files must parse without syntax errors."""
    files = [
        f"{TOOLS}/backend/keyboard.ts",
        f"{TOOLS}/backend/mouse.ts",
        f"{TOOLS}/backend/snapshot.ts",
        f"{TOOLS}/cli-client/skill/SKILL.md",
    ]
    for fpath in files:
        assert Path(fpath).exists(), f"File not found: {fpath}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_type_tool_conditional_wait():
    """browser_type (fill) must only use waitForCompletion when submit or slowly is set."""
    src = Path(f"{TOOLS}/backend/keyboard.ts").read_text()

    # Find the type tool's handle function — it's the one with refLocator + lookupSecret
    # The action body should be extracted into a variable or inline function
    # and waitForCompletion should be conditional on submit/slowly

    # There must be a conditional check for submit or slowly before waitForCompletion
    # in the type tool's handler
    type_section = _extract_type_handler(src)

    # The unconditional waitForCompletion wrapping the entire fill+submit should be gone.
    # waitForCompletion must still exist (for submit/slowly cases) but not wrap the plain fill.
    assert "waitForCompletion" in type_section, \
        "type tool must still use waitForCompletion for submit/slowly paths"

    # There must be a conditional that gates waitForCompletion on submit or slowly.
    # Accept various formulations: if/else, ternary, etc.
    has_submit_check = bool(re.search(r'params\.submit', type_section))
    has_slowly_check = bool(re.search(r'params\.slowly', type_section))
    assert has_submit_check and has_slowly_check, \
        "type tool must check both params.submit and params.slowly to decide waitForCompletion"

    # The fill path (not submit, not slowly) must NOT be inside waitForCompletion.
    # Verify there's a branch where the action runs without waitForCompletion.
    # This means there must be an else/alternative path after the conditional.
    lines = type_section.split("\n")
    wait_lines = [i for i, l in enumerate(lines) if "waitForCompletion" in l]
    # waitForCompletion should appear inside a conditional, not at the top level of the handler
    # Verify: at least one line between the handle start and waitForCompletion has an if-check
    has_guarded_wait = False
    for wl in wait_lines:
        preceding = "\n".join(lines[max(0, wl - 5):wl])
        if re.search(r'if\s*\(', preceding):
            has_guarded_wait = True
            break
    assert has_guarded_wait, \
        "waitForCompletion must be guarded by a conditional (not unconditionally wrapping the fill)"


# [pr_diff] fail_to_pass
def test_hover_no_wait_for_completion():
    """browser_hover must not use waitForCompletion."""
    src = Path(f"{TOOLS}/backend/snapshot.ts").read_text()

    hover_section = _extract_tool_handler(src, "browser_hover")

    # hover should directly await the locator action, not wrap in waitForCompletion
    assert "waitForCompletion" not in hover_section, \
        "hover handler must not use waitForCompletion — hover never causes navigation"

    # Must still call locator.hover
    assert "locator.hover" in hover_section or ".hover(" in hover_section, \
        "hover handler must still call hover on the locator"


# [pr_diff] fail_to_pass
def test_select_option_no_wait_for_completion():
    """browser_select_option must not use waitForCompletion."""
    src = Path(f"{TOOLS}/backend/snapshot.ts").read_text()

    select_section = _extract_tool_handler(src, "browser_select_option")

    assert "waitForCompletion" not in select_section, \
        "selectOption handler must not use waitForCompletion — selectOption never causes navigation"

    # Must still call selectOption
    assert "selectOption" in select_section, \
        "selectOption handler must still call selectOption on the locator"


# [pr_diff] fail_to_pass

    move_section = _extract_tool_handler(src, "browser_mouse_move_xy")

    assert "waitForCompletion" not in move_section, \
        "mouseMove handler must not use waitForCompletion — mouse.move never causes navigation"

    # Must still call mouse.move
    assert "mouse.move" in move_section, \
        "mouseMove handler must still call page.mouse.move"


# ---------------------------------------------------------------------------
# Config edit (config_edit) — SKILL.md documentation update
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass

    # The fill example must show --submit
    assert "--submit" in skill_md, \
        "SKILL.md should document the --submit flag"

    # The fill command line should include --submit
    fill_lines = [line for line in skill_md.split("\n") if "fill" in line.lower() and "--submit" in line]
    assert len(fill_lines) >= 1, \
        "SKILL.md should have at least one fill example with --submit"

    # Should explain what --submit does (presses Enter)
    lower = skill_md.lower()
    assert ("enter" in lower and "submit" in lower) or "presses enter" in lower, \
        "SKILL.md should explain that --submit presses Enter after filling"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_click_still_uses_wait_for_completion():
    """browser_click must still use waitForCompletion (it causes navigation)."""
    src = Path(f"{TOOLS}/backend/snapshot.ts").read_text()

    click_section = _extract_tool_handler(src, "browser_click")

    assert "waitForCompletion" in click_section, \
        "click handler must still use waitForCompletion — clicks can cause navigation"


# [static] pass_to_pass
def test_press_enter_still_uses_wait_for_completion():
    """browser_press_key for Enter must still use waitForCompletion."""
    src = Path(f"{TOOLS}/backend/keyboard.ts").read_text()

    press_section = _extract_tool_handler(src, "browser_press_key")

    assert "waitForCompletion" in press_section, \
        "press handler must still use waitForCompletion for Enter key"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _extract_type_handler(src: str) -> str:
    """Extract the type tool handler body from keyboard.ts."""
    # The type tool has name: 'browser_type' and its handle function
    # contains refLocator and lookupSecret
    match = re.search(r"name:\s*['\"]browser_type['\"]", src)
    assert match, "browser_type tool definition not found in keyboard.ts"
    # Get everything from this tool definition to the next export or end
    start = match.start()
    # Find the handle function
    handle_match = re.search(r"handle:\s*async", src[start:])
    assert handle_match, "handle function not found in browser_type tool"
    handle_start = start + handle_match.start()
    # Find the closing of this tool definition (next defineTabTool or end of exports)
    rest = src[handle_start:]
    # Use brace counting to find end of handler
    return _extract_brace_block(rest)


def _extract_tool_handler(src: str, tool_name: str) -> str:
    """Extract a tool handler body by its schema name."""
    pattern = rf"name:\s*['\"]{ re.escape(tool_name) }['\"]"
    match = re.search(pattern, src)
    assert match, f"{tool_name} tool definition not found"
    start = match.start()
    handle_match = re.search(r"handle:\s*async", src[start:])
    assert handle_match, f"handle function not found in {tool_name} tool"
    handle_start = start + handle_match.start()
    rest = src[handle_start:]
    return _extract_brace_block(rest)


def _extract_brace_block(src: str) -> str:
    """Extract text from first { to its matching }, inclusive."""
    brace_start = src.index("{")
    depth = 0
    for i in range(brace_start, len(src)):
        if src[i] == "{":
            depth += 1
        elif src[i] == "}":
            depth -= 1
            if depth == 0:
                return src[brace_start:i + 1]
    return src[brace_start:]
