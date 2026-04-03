"""
Task: zulip-ai-document-reset-to-default
Repo: zulip/zulip @ f2946b9dd3ea604127f0213336704ae0e836319b
PR:   38368

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

from pathlib import Path

REPO = "/workspace/zulip"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core content tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_reset_page_exists():
    """New help center page for resetting user settings to org defaults."""
    page = Path(REPO) / "starlight_help/src/content/docs/reset-settings-for-users.mdx"
    assert page.exists(), "reset-settings-for-users.mdx must exist"
    content = page.read_text()
    # Page must describe the reset feature with key concepts
    assert "reset" in content.lower(), "Page should describe resetting settings"
    assert "default" in content.lower(), "Page should mention organization defaults"
    assert "AdminOnly" in content or "admin" in content.lower(), \
        "Page should indicate this is an admin feature"
    # Must have instructions for how to do it
    assert "NavigationSteps" in content or "settings" in content.lower(), \
        "Page should include navigation instructions"
    # Must mention privacy settings limitation
    assert "privacy" in content.lower(), \
        "Page should mention that privacy settings cannot be reset"


# [pr_diff] fail_to_pass
def test_shared_include_created():
    """Settings list extracted into a shared include file."""
    include = Path(REPO) / "starlight_help/src/content/include/_DefaultUserSettingsList.mdx"
    assert include.exists(), "_DefaultUserSettingsList.mdx must exist"
    content = include.read_text()
    # Must contain key settings categories
    assert "Language" in content or "language" in content, \
        "Include should list Language setting"
    assert "notification" in content.lower(), \
        "Include should list notification settings"
    assert "theme" in content.lower() or "Theme" in content, \
        "Include should list theme setting"
    assert "Home view" in content or "home view" in content.lower(), \
        "Include should list home view setting"


# [pr_diff] fail_to_pass
def test_sidebar_entry():
    """astro.config.mjs has sidebar entry for the new reset page."""
    config = Path(REPO) / "starlight_help/astro.config.mjs"
    content = config.read_text()
    assert "reset-settings-for-users" in content, \
        "astro.config.mjs should have sidebar entry for reset-settings-for-users"


# [pr_diff] fail_to_pass
def test_existing_page_uses_shared_include():
    """configure-default-new-user-settings.mdx imports the shared include."""
    page = Path(REPO) / "starlight_help/src/content/docs/configure-default-new-user-settings.mdx"
    content = page.read_text()
    assert "DefaultUserSettingsList" in content, \
        "configure-default page should import DefaultUserSettingsList"


# [pr_diff] fail_to_pass


# [pr_diff] fail_to_pass


# ---------------------------------------------------------------------------
# Fail-to-pass (config_edit) — CLAUDE.md update tests
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — preservation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_existing_page_preserved():
    """configure-default-new-user-settings.mdx still has valid structure."""
    page = Path(REPO) / "starlight_help/src/content/docs/configure-default-new-user-settings.mdx"
    assert page.exists(), "configure-default-new-user-settings.mdx must still exist"
    content = page.read_text()
    # Frontmatter preserved
    assert content.startswith("---"), "Page should have frontmatter"
    assert "Configure default settings for new users" in content, \
        "Page should preserve its title"
    # Key navigation still works
    assert "NavigationSteps" in content or "FlattenedSteps" in content, \
        "Page should still have step components"
    # Related articles section preserved
    assert "Related articles" in content, \
        "Page should still have Related articles section"
