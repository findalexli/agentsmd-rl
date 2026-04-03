"""
Task: opencode-home-footer-plugin-slot
Repo: anomalyco/opencode @ 8e4bab51812fccf3b69713904159a4394b3a29ab
PR:   20057

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/opencode"
HOME_TSX = Path(REPO) / "packages/opencode/src/cli/cmd/tui/routes/home.tsx"
INTERNAL_TS = Path(REPO) / "packages/opencode/src/cli/cmd/tui/plugin/internal.ts"
SLOT_MAP = Path(REPO) / "packages/plugin/src/tui.ts"
FEATURE_PLUGINS = Path(REPO) / "packages/opencode/src/cli/cmd/tui/feature-plugins"


def _find_footer_plugin() -> Path | None:
    """Locate the footer plugin file under feature-plugins/home/."""
    candidates = [
        FEATURE_PLUGINS / "home" / "footer.tsx",
        FEATURE_PLUGINS / "home" / "footer.ts",
        FEATURE_PLUGINS / "home" / "home-footer.tsx",
        FEATURE_PLUGINS / "home" / "home-footer.ts",
    ]
    for c in candidates:
        if c.exists():
            return c
    # Fallback: any .tsx/.ts under feature-plugins/home/ with "footer" in name
    home_dir = FEATURE_PLUGINS / "home"
    if home_dir.is_dir():
        for f in home_dir.iterdir():
            if "footer" in f.name.lower() and f.suffix in (".tsx", ".ts"):
                return f
    return None


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_home_tsx_footer_logic_extracted():
    """home.tsx must no longer contain inline MCP counting/display logic."""
    src = HOME_TSX.read_text()
    # These patterns are present in the base commit and must be removed
    assert not re.search(r"connectedMcpCount", src), \
        "home.tsx still has connectedMcpCount — footer logic not extracted"
    assert not re.search(r"mcpError", src), \
        "home.tsx still has mcpError — footer logic not extracted"
    assert not re.search(r"Installation\.VERSION", src), \
        "home.tsx still renders version inline — should be in footer plugin"


# [pr_diff] fail_to_pass
def test_home_tsx_uses_slot_for_footer():
    """home.tsx must render the footer via the plugin slot system."""
    src = HOME_TSX.read_text()
    has_slot_ref = "home_footer" in src
    has_slot_component = bool(re.search(r"Slot", src))
    assert has_slot_ref and has_slot_component, \
        "home.tsx does not use TuiPluginRuntime.Slot for home_footer"


# [pr_diff] fail_to_pass
def test_footer_plugin_exists_with_content():
    """Footer plugin must exist with JSX rendering of directory, MCP, and version."""
    # AST-only because: TypeScript/SolidJS TSX cannot be imported in Python
    footer = _find_footer_plugin()
    assert footer is not None, \
        "No footer plugin file found under feature-plugins/home/"
    src = footer.read_text()
    # Must have non-trivial code (at least 20 real lines)
    code_lines = [
        l for l in src.splitlines()
        if l.strip() and not l.strip().startswith("//") and not l.strip().startswith("*")
    ]
    assert len(code_lines) >= 20, \
        f"Footer plugin only has {len(code_lines)} code lines (need 20+)"
    # Must contain JSX
    assert re.search(r"<[A-Z][A-Za-z]*[\s/>]", src), \
        "Footer plugin has no JSX component rendering"
    # Must reference at least 2 of: directory/cwd, mcp, version
    has_dir = bool(re.search(r"directory|cwd|dir|path", src, re.IGNORECASE))
    has_mcp = bool(re.search(r"mcp", src, re.IGNORECASE))
    has_version = bool(re.search(r"version", src, re.IGNORECASE))
    count = sum([has_dir, has_mcp, has_version])
    assert count >= 2, \
        f"Footer plugin only covers {count}/3 footer concerns (need 2+: dir, mcp, version)"


# [pr_diff] fail_to_pass
def test_footer_plugin_has_slot_registration():
    """Footer plugin must have default export and register home_footer slot."""
    # AST-only because: TypeScript/SolidJS TSX cannot be imported in Python
    footer = _find_footer_plugin()
    assert footer is not None, "No footer plugin file found"
    src = footer.read_text()
    # Default export
    has_default = bool(
        re.search(r"export\s+default\b", src)
        or re.search(r"export\s*\{[^}]*as\s+default", src)
    )
    assert has_default, "Footer plugin missing default export"
    # Slot registration
    assert "home_footer" in src, \
        "Footer plugin does not reference home_footer slot"
    assert bool(re.search(r"register|slots|init\s*[:(]", src)), \
        "Footer plugin has no slot registration call"


# [pr_diff] fail_to_pass
def test_slot_map_declares_home_footer():
    """TuiSlotMap in tui.ts must declare the home_footer slot."""
    src = SLOT_MAP.read_text()
    assert "home_footer" in src, \
        "home_footer slot not declared in TuiSlotMap (packages/plugin/src/tui.ts)"


# [pr_diff] fail_to_pass
def test_internal_registry_includes_footer():
    """internal.ts must import/register the home footer plugin."""
    src = INTERNAL_TS.read_text()
    has_ref = bool(re.search(
        r"home/footer|home-footer|HomeFooter|homeFooter|feature-plugins.*footer",
        src, re.IGNORECASE,
    ))
    assert has_ref, \
        "Footer plugin not imported/registered in internal.ts"


# [pr_diff] fail_to_pass
def test_home_tsx_hint_removed():
    """home.tsx must not pass hint prop to Prompt (MCP hint moved to footer plugin)."""
    src = HOME_TSX.read_text()
    assert not re.search(r"hint\s*=\s*\{", src), \
        "home.tsx still passes hint prop to Prompt — redundant MCP display not removed"
    # Also verify useDirectory and useTheme are no longer imported (now in footer plugin)
    assert not re.search(r"useDirectory", src), \
        "home.tsx still imports useDirectory — should be removed after footer extraction"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression checks
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_home_tsx_preserves_core_components():
    """home.tsx must still render Logo and Prompt components."""
    src = HOME_TSX.read_text()
    assert re.search(r"Logo", src), "home.tsx missing Logo component"
    assert re.search(r"Prompt", src), "home.tsx missing Prompt component"


# [pr_diff] pass_to_pass
def test_existing_plugins_and_slots_preserved():
    """Existing internal plugins and TuiSlotMap slots must be preserved."""
    # Check internal.ts still has Tips and SidebarFooter
    internal = INTERNAL_TS.read_text()
    assert re.search(r"Tips", internal, re.IGNORECASE), \
        "HomeTips plugin lost from internal.ts"
    assert re.search(r"Sidebar.*Footer|Footer.*Sidebar|SidebarFooter", internal, re.IGNORECASE), \
        "SidebarFooter plugin lost from internal.ts"
    # Check existing slots preserved in tui.ts
    slot_src = SLOT_MAP.read_text()
    for slot in ("home_logo", "home_prompt", "home_bottom"):
        assert slot in slot_src, f"Existing slot '{slot}' missing from TuiSlotMap"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — AGENTS.md:13 @ 8e4bab51812fccf3b69713904159a4394b3a29ab
def test_footer_plugin_no_any_type():
    """Footer plugin must not use the `any` type (AGENTS.md rule)."""
    # AST-only because: TypeScript TSX cannot be imported in Python
    footer = _find_footer_plugin()
    assert footer is not None, "No footer plugin file found"
    src = footer.read_text()
    # Match `: any`, `as any`, `<any>`, but not inside comments or strings
    lines = src.splitlines()
    for i, line in enumerate(lines, 1):
        stripped = line.lstrip()
        if stripped.startswith("//") or stripped.startswith("*"):
            continue
        if re.search(r":\s*any\b|as\s+any\b|<any>", line):
            assert False, f"Footer plugin uses `any` type at line {i}: {line.strip()}"


# [agent_config] fail_to_pass — AGENTS.md:84 @ 8e4bab51812fccf3b69713904159a4394b3a29ab
def test_footer_plugin_no_else_statements():
    """Footer plugin must not use `else` statements — prefer early returns (AGENTS.md rule)."""
    # AST-only because: TypeScript TSX cannot be imported in Python
    footer = _find_footer_plugin()
    assert footer is not None, "No footer plugin file found"
    src = footer.read_text()
    lines = src.splitlines()
    for i, line in enumerate(lines, 1):
        stripped = line.lstrip()
        if stripped.startswith("//") or stripped.startswith("*"):
            continue
        # Match standalone else or } else {
        if re.search(r"\belse\b", line):
            assert False, f"Footer plugin uses `else` at line {i}: {line.strip()}"


# [agent_config] fail_to_pass — AGENTS.md:12 @ 8e4bab51812fccf3b69713904159a4394b3a29ab
def test_footer_plugin_no_try_catch():
    """Footer plugin must not use try/catch blocks (AGENTS.md rule)."""
    # AST-only because: TypeScript TSX cannot be imported in Python
    footer = _find_footer_plugin()
    assert footer is not None, "No footer plugin file found"
    src = footer.read_text()
    lines = src.splitlines()
    for i, line in enumerate(lines, 1):
        stripped = line.lstrip()
        if stripped.startswith("//") or stripped.startswith("*"):
            continue
        if re.search(r"\btry\s*\{", line) or re.search(r"\bcatch\s*\(", line):
            assert False, f"Footer plugin uses try/catch at line {i}: {line.strip()} — avoid try/catch"


# [agent_config] fail_to_pass — AGENTS.md:17 @ 8e4bab51812fccf3b69713904159a4394b3a29ab
def test_footer_plugin_no_for_loops():
    """Footer plugin must prefer functional array methods over for loops (AGENTS.md rule)."""
    # AST-only because: TypeScript TSX cannot be imported in Python
    footer = _find_footer_plugin()
    assert footer is not None, "No footer plugin file found"
    src = footer.read_text()
    lines = src.splitlines()
    for i, line in enumerate(lines, 1):
        stripped = line.lstrip()
        if stripped.startswith("//") or stripped.startswith("*"):
            continue
        if re.search(r"\bfor\s*\(", line):
            assert False, f"Footer plugin uses for loop at line {i}: {line.strip()} — prefer functional array methods"


# [agent_config] fail_to_pass — AGENTS.md:70 @ 8e4bab51812fccf3b69713904159a4394b3a29ab
def test_footer_plugin_const_over_let():
    """Footer plugin must prefer const over let (AGENTS.md rule)."""
    # AST-only because: TypeScript TSX cannot be imported in Python
    footer = _find_footer_plugin()
    assert footer is not None, "No footer plugin file found"
    src = footer.read_text()
    lines = src.splitlines()
    for i, line in enumerate(lines, 1):
        stripped = line.lstrip()
        if stripped.startswith("//") or stripped.startswith("*"):
            continue
        if re.search(r"\blet\s+\w+", line):
            assert False, f"Footer plugin uses `let` at line {i}: {line.strip()} — prefer const"
