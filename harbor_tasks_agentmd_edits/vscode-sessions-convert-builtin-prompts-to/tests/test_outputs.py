"""
Task: vscode-sessions-convert-builtin-prompts-to
Repo: microsoft/vscode @ 6e1a95ed840d8dc312792b228f0e8b2d365a60ae
PR:   305347

Convert built-in prompts to skills, add UI Integration badge, update docs.
All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/vscode"

# Key file paths
COMMON_INTERFACE = Path(REPO) / "src/vs/workbench/contrib/chat/common/aiCustomizationWorkspaceService.ts"
SESSIONS_SERVICE = Path(REPO) / "src/vs/sessions/contrib/chat/browser/aiCustomizationWorkspaceService.ts"
PROMPTS_SERVICE = Path(REPO) / "src/vs/sessions/contrib/chat/browser/promptsService.ts"
LIST_WIDGET = Path(REPO) / "src/vs/workbench/contrib/chat/browser/aiCustomization/aiCustomizationListWidget.ts"
CORE_SERVICE = Path(REPO) / "src/vs/workbench/contrib/chat/browser/aiCustomization/aiCustomizationWorkspaceService.ts"
AI_CUSTOMIZATIONS_MD = Path(REPO) / "src/vs/sessions/AI_CUSTOMIZATIONS.md"

SKILL_NAMES = [
    "act-on-feedback",
    "create-draft-pr",
    "create-pr",
    "generate-run-commands",
    "merge-changes",
    "update-pr",
]


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Key TypeScript files parse without obvious syntax errors."""
    for fpath in [COMMON_INTERFACE, SESSIONS_SERVICE, PROMPTS_SERVICE, LIST_WIDGET, CORE_SERVICE]:
        content = fpath.read_text()
        assert content.strip(), f"{fpath.name} is empty"
        opens = content.count("{")
        closes = content.count("}")
        assert abs(opens - closes) < 5, (
            f"{fpath.name}: brace imbalance ({opens} open vs {closes} close)"
        )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core code behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_interface_has_skill_ui_integrations():
    """IAICustomizationWorkspaceService interface must declare getSkillUIIntegrations."""
    content = COMMON_INTERFACE.read_text()
    assert "getSkillUIIntegrations" in content, (
        "Interface must declare getSkillUIIntegrations method"
    )
    assert "ReadonlyMap<string, string>" in content, (
        "getSkillUIIntegrations must return ReadonlyMap<string, string>"
    )


# [pr_diff] fail_to_pass
def test_sessions_service_has_skill_ui_mappings():
    """Sessions workspace service must provide skill-to-UI mappings."""
    content = SESSIONS_SERVICE.read_text()
    assert "getSkillUIIntegrations" in content, (
        "Sessions service must implement getSkillUIIntegrations"
    )
    assert "act-on-feedback" in content, (
        "Sessions service must map 'act-on-feedback' skill to its UI integration"
    )
    assert "generate-run-commands" in content, (
        "Sessions service must map 'generate-run-commands' skill to its UI integration"
    )


# [pr_diff] fail_to_pass
def test_prompts_service_no_builtin_prompts():
    """AgenticPromptsService must not have the old built-in prompts system."""
    content = PROMPTS_SERVICE.read_text()
    assert "BUILTIN_PROMPTS_URI" not in content, (
        "promptsService.ts must not reference BUILTIN_PROMPTS_URI (old system)"
    )
    assert "discoverBuiltinPrompts" not in content, (
        "promptsService.ts must not have discoverBuiltinPrompts method"
    )
    assert "_builtinPromptsCache" not in content, (
        "promptsService.ts must not have _builtinPromptsCache field"
    )
    assert "BUILTIN_SKILLS_URI" in content, (
        "promptsService.ts must still have BUILTIN_SKILLS_URI for skill discovery"
    )


# [pr_diff] fail_to_pass
def test_list_widget_shows_ui_badge():
    """The list widget must display UI Integration badges on skills."""
    content = LIST_WIDGET.read_text()
    assert "getSkillUIIntegrations" in content, (
        "List widget must call getSkillUIIntegrations"
    )
    assert "UI Integration" in content, (
        "List widget must display 'UI Integration' badge text"
    )
    assert "badgeTooltip" in content, (
        "List widget must set badgeTooltip from UI integrations map"
    )


# [pr_diff] fail_to_pass
def test_core_service_implements_empty_integrations():
    """Core VS Code workspace service must implement getSkillUIIntegrations (empty map)."""
    content = CORE_SERVICE.read_text()
    assert "getSkillUIIntegrations" in content, (
        "Core service must implement getSkillUIIntegrations"
    )
    assert re.search(r"new Map\(\)", content), (
        "Core service should return an empty Map (no UI integrations in core)"
    )


# [pr_diff] fail_to_pass


# [pr_diff] fail_to_pass
def test_old_prompt_files_removed():
    """Old .prompt.md files in vs/sessions/prompts/ must be removed."""
    prompts_dir = Path(REPO) / "src/vs/sessions/prompts"
    if not prompts_dir.exists():
        return  # Directory removed entirely — good
    prompt_files = list(prompts_dir.glob("*.prompt.md"))
    assert len(prompt_files) == 0, (
        f"Old prompt files should be removed, found: {[f.name for f in prompt_files]}"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (config_edit) — documentation update tests
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# ---------------------------------------------------------------------------
# Pass-to-pass (agent_config) — existing config rules
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass
