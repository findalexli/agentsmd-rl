"""
Task: socialify-upgrade-simpleicons-to-version-1630
Repo: wei/socialify @ a4782705076144332a7ca53d4d35afdcd0ddb93e
PR:   765

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/socialify"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified TypeScript files must parse without errors."""
    for relpath in [
        "common/icons/customIcons.ts",
        "common/icons/languageMapping.ts",
    ]:
        fpath = Path(REPO) / relpath
        assert fpath.exists(), f"{relpath} must exist"
        content = fpath.read_text()
        # Basic syntax: balanced braces, no obvious truncation
        assert content.count("{") == content.count("}"), (
            f"{relpath}: mismatched braces"
        )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests: custom icon fallbacks
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_custom_heroku_icon_defined():
    """customIcons.ts must export a Heroku icon with correct data fields."""
    content = (Path(REPO) / "common/icons/customIcons.ts").read_text()
    # Must have an exported const for Heroku
    assert re.search(r"export\s+const\s+\w*[Hh]eroku", content), (
        "customIcons.ts should export a Heroku custom icon"
    )
    # Must contain the Heroku hex color
    assert "430098" in content, "Heroku icon should have hex color 430098"
    # Must contain an SVG path for Heroku
    assert re.search(r"slug:\s*['\"]heroku['\"]", content), (
        "Heroku icon should have slug 'heroku'"
    )


# [pr_diff] fail_to_pass
def test_custom_openai_icon_defined():
    """customIcons.ts must export an OpenAI icon with correct data fields."""
    content = (Path(REPO) / "common/icons/customIcons.ts").read_text()
    assert re.search(r"export\s+const\s+\w*[Oo]pen[Aa][Ii]", content), (
        "customIcons.ts should export an OpenAI custom icon"
    )
    assert "412991" in content, "OpenAI icon should have hex color 412991"
    assert re.search(r"slug:\s*['\"]openai['\"]", content), (
        "OpenAI icon should have slug 'openai'"
    )


# [pr_diff] fail_to_pass
def test_custom_slack_icon_defined():
    """customIcons.ts must export a Slack icon with correct data fields."""
    content = (Path(REPO) / "common/icons/customIcons.ts").read_text()
    assert re.search(r"export\s+const\s+\w*[Ss]lack", content), (
        "customIcons.ts should export a Slack custom icon"
    )
    assert "4A154B" in content, "Slack icon should have hex color 4A154B"
    assert re.search(r"slug:\s*['\"]slack['\"]", content), (
        "Slack icon should have slug 'slack'"
    )


# [pr_diff] fail_to_pass
def test_language_mapping_uses_custom_fallbacks():
    """languageMapping.ts must map Heroku, OpenAI, Slack to custom icons."""
    content = (Path(REPO) / "common/icons/languageMapping.ts").read_text()

    # Should NOT import siHeroku, siOpenai, siSlack from simple-icons
    assert "siHeroku" not in content, (
        "languageMapping should not import siHeroku (removed in simple-icons v16)"
    )
    assert "siOpenai" not in content, (
        "languageMapping should not import siOpenai (removed in simple-icons v16)"
    )
    assert "siSlack" not in content, (
        "languageMapping should not import siSlack (removed in simple-icons v16)"
    )

    # Should import custom versions from customIcons
    assert re.search(r"import\s*\{[^}]*\w*[Hh]eroku[^}]*\}\s*from\s*['\"]\.\/customIcons['\"]", content, re.DOTALL), (
        "languageMapping should import a Heroku icon from customIcons"
    )

    # The mapping object should reference custom icons for these three
    # Check that Heroku key maps to something from customIcons (not si*)
    heroku_mapping = re.search(r"Heroku:\s*(\w+)", content)
    assert heroku_mapping, "Heroku must be in the mapping"
    assert not heroku_mapping.group(1).startswith("si"), (
        "Heroku mapping should use a custom icon, not si* import"
    )


# ---------------------------------------------------------------------------
# Config edit tests (config_edit) — agent config / doc updates
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass

    assert ".github/skills" in content, (
        "AGENTS.md should document the .github/skills/ directory"
    )
    # Should mention the upgrade-simple-icons skill specifically
    assert "upgrade-simple-icons" in content or "simple-icons" in content.lower(), (
        "AGENTS.md should reference the simple-icons upgrade skill"
    )


# [config_edit] fail_to_pass

    # Find any SKILL.md that documents simple-icons upgrade
    skill_files = list(skills_dir.rglob("SKILL.md")) + list(skills_dir.rglob("*.md"))
    assert len(skill_files) > 0, (
        ".github/skills/ should contain at least one skill document"
    )

    # At least one skill file must document the simple-icons upgrade process
    found = False
    for sf in skill_files:
        content = sf.read_text()
        if "simple-icons" in content.lower() or "simpleicons" in content.lower():
            found = True
            # Should document key workflow steps
            assert "pnpm" in content.lower() or "npm" in content.lower() or "install" in content.lower(), (
                "Skill doc should mention package installation step"
            )
            assert "custom" in content.lower() or "fallback" in content.lower() or "mapping" in content.lower(), (
                "Skill doc should mention custom icon fallback or mapping process"
            )
            break
    assert found, (
        "A skill document under .github/skills/ must cover the simple-icons upgrade workflow"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_existing_custom_icons_preserved():
    """Pre-existing custom icons (Amazon, AWS, C#, Java, etc.) must still be defined."""
    content = (Path(REPO) / "common/icons/customIcons.ts").read_text()

    for icon_name in ["customAmazon", "customAWS", "customCsharp", "customJava",
                      "customMicrosoft", "customPowershell", "customVisualStudio", "customVSCode"]:
        assert icon_name in content, (
            f"Pre-existing icon {icon_name} must still be exported from customIcons.ts"
        )


# [static] pass_to_pass
def test_language_mapping_structure():
    """languageMapping.ts must still export LANGUAGE_ICON_MAPPING with key entries."""
    content = (Path(REPO) / "common/icons/languageMapping.ts").read_text()
    assert "LANGUAGE_ICON_MAPPING" in content, (
        "languageMapping.ts must export LANGUAGE_ICON_MAPPING"
    )
    # Spot-check that common mappings still exist
    for lang in ["JavaScript", "Python", "TypeScript", "Go", "Rust", "Java"]:
        assert re.search(rf"['\"]?{lang}['\"]?\s*:", content), (
            f"LANGUAGE_ICON_MAPPING should still contain {lang}"
        )
