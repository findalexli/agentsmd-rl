"""
Task: wasp-add-coding-agent-plugin-docs
Repo: wasp-lang/wasp @ a9d31fbab364485fcd01d9edf1c729d1cc78e564
PR:   3966

Replace the deprecated "Wasp AI / Mage" documentation section with a new
"AI & Coding Agents" section documenting the wasp-agent-plugins.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

from pathlib import Path

REPO = "/workspace/wasp"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_sidebar_preserves_other_categories():
    """Sidebar must still contain core doc categories."""
    content = Path(f"{REPO}/web/sidebars.ts").read_text()
    assert "Getting Started" in content, "Sidebar missing 'Getting Started' category"
    assert "Tutorial" in content, "Sidebar missing 'Tutorial' category"
    assert "Authentication" in content, "Sidebar missing 'Authentication' category"
    assert "Deployment" in content, "Sidebar missing 'Deployment' category"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests for code changes
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_sidebar_category_renamed():
    """Sidebar AI category must be renamed from 'Wasp AI' to something mentioning agents."""
    content = Path(f"{REPO}/web/sidebars.ts").read_text()
    # The old label should be gone
    assert '"Wasp AI"' not in content and "'Wasp AI'" not in content, \
        "Sidebar still has old 'Wasp AI' label"
    # The new label should reference AI and agents/coding
    lower = content.lower()
    assert "agent" in lower or "coding" in lower, \
        "Sidebar AI category should reference agents or coding"


# [pr_diff] fail_to_pass
def test_sidebar_references_agent_plugin_page():
    """Sidebar must list the coding-agent-plugin docs page."""
    content = Path(f"{REPO}/web/sidebars.ts").read_text()
    assert "coding-agent-plugin" in content, \
        "Sidebar should reference 'coding-agent-plugin' page"
    # Old page references should be gone
    assert "creating-new-app" not in content, \
        "Sidebar should not reference removed 'creating-new-app'"
    assert "developing-existing-app" not in content, \
        "Sidebar should not reference removed 'developing-existing-app'"


# [pr_diff] fail_to_pass
def test_agent_plugin_page_created():
    """A new docs page for the coding agent plugin must exist with key content."""
    page = Path(f"{REPO}/web/docs/wasp-ai/coding-agent-plugin.md")
    assert page.exists(), "coding-agent-plugin.md must be created"
    content = page.read_text()
    assert len(content) > 200, "Page should have substantial content"
    lower = content.lower()
    assert "plugin" in lower or "skill" in lower, \
        "Page should describe the agent plugin/skills"
    assert "wasp" in lower, "Page should mention Wasp"


# [pr_diff] fail_to_pass
def test_agent_plugin_page_has_installation_instructions():
    """The agent plugin page must include installation instructions for multiple agents."""
    page = Path(f"{REPO}/web/docs/wasp-ai/coding-agent-plugin.md")
    assert page.exists(), "coding-agent-plugin.md must exist"
    content = page.read_text()
    lower = content.lower()
    # Must document installation for Claude Code
    assert "claude" in lower, "Should mention Claude Code"
    # Must document installation for other agents
    assert "cursor" in lower or "codex" in lower or "copilot" in lower, \
        "Should mention at least one other coding agent"
    # Must have actual install commands
    assert "install" in lower or "npx" in lower or "npm" in lower, \
        "Should include installation commands"


# [pr_diff] fail_to_pass
def test_quick_start_includes_agent_setup():
    """Quick-start page should reference agent plugin setup."""
    content = Path(f"{REPO}/web/docs/introduction/quick-start.md").read_text()
    lower = content.lower()
    assert "agent" in lower and ("plugin" in lower or "skill" in lower), \
        "Quick start should mention agent plugin or skills"
    # Should NOT still reference the old Wasp AI link
    assert "creating-new-app" not in content, \
        "Quick start should not link to removed creating-new-app page"


# [pr_diff] fail_to_pass
def test_old_wasp_ai_pages_removed():
    """Old Wasp AI / Mage documentation pages must be deleted."""
    assert not Path(f"{REPO}/web/docs/wasp-ai/creating-new-app.md").exists(), \
        "creating-new-app.md should be deleted"
    assert not Path(f"{REPO}/web/docs/wasp-ai/developing-existing-app.md").exists(), \
        "developing-existing-app.md should be deleted"


# ---------------------------------------------------------------------------
# Config-edit (config_edit) — README.md config file update tests
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass
