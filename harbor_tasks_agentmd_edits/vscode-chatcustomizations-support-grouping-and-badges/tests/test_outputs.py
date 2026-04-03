"""
Task: vscode-chatcustomizations-support-grouping-and-badges
Repo: vscode @ 958f822bbea8a409fb7f6bc22cfc1594b61f61fd
PR:   305813

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/vscode"

# Key file paths
HARNESS_SERVICE = Path(REPO) / "src/vs/workbench/contrib/chat/common/customizationHarnessService.ts"
LIST_WIDGET = Path(REPO) / "src/vs/workbench/contrib/chat/browser/aiCustomization/aiCustomizationListWidget.ts"
MAIN_THREAD = Path(REPO) / "src/vs/workbench/api/browser/mainThreadChatAgents2.ts"
EXT_HOST_PROTOCOL = Path(REPO) / "src/vs/workbench/api/common/extHost.protocol.ts"
EXT_HOST_AGENTS = Path(REPO) / "src/vs/workbench/api/common/extHostChatAgents2.ts"
PROPOSED_API = Path(REPO) / "src/vscode-dts/vscode.proposed.chatSessionCustomizationProvider.d.ts"
SKILL_MD = Path(REPO) / ".github/skills/chat-customizations-editor/SKILL.md"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_modified_files_exist():
    """All files touched by this feature must exist and be non-empty."""
    for f in [HARNESS_SERVICE, LIST_WIDGET, MAIN_THREAD, EXT_HOST_PROTOCOL,
              EXT_HOST_AGENTS, PROPOSED_API, SKILL_MD]:
        assert f.exists(), f"{f.name} does not exist"
        assert f.stat().st_size > 100, f"{f.name} appears empty or truncated"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — code behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_interface_new_fields():
    """IExternalCustomizationItem must declare groupKey, badge, badgeTooltip."""
    content = HARNESS_SERVICE.read_text()
    # Find the IExternalCustomizationItem interface
    match = re.search(
        r'interface\s+IExternalCustomizationItem\s*\{(.*?)\n\}',
        content, re.DOTALL
    )
    assert match, "IExternalCustomizationItem interface not found in customizationHarnessService.ts"
    body = match.group(1)
    assert "groupKey" in body, "IExternalCustomizationItem missing groupKey field"
    assert re.search(r'\bbadge\b', body), "IExternalCustomizationItem missing badge field"
    assert "badgeTooltip" in body, "IExternalCustomizationItem missing badgeTooltip field"


# [pr_diff] fail_to_pass
def test_five_layer_field_sync():
    """groupKey/badge/badgeTooltip must propagate through all 5 API layers."""
    # Layer 1: Proposed extension API (.d.ts)
    proposed = PROPOSED_API.read_text()
    for field in ["groupKey", "badge", "badgeTooltip"]:
        assert field in proposed, f"Proposed API .d.ts missing {field}"

    # Layer 2: IPC DTO (extHost.protocol.ts)
    protocol = EXT_HOST_PROTOCOL.read_text()
    dto_match = re.search(
        r'interface\s+IChatSessionCustomizationItemDto\s*\{(.*?)\n\}',
        protocol, re.DOTALL
    )
    assert dto_match, "IChatSessionCustomizationItemDto not found"
    dto_body = dto_match.group(1)
    for field in ["groupKey", "badge", "badgeTooltip"]:
        assert field in dto_body, f"IChatSessionCustomizationItemDto missing {field}"

    # Layer 3: ExtHost mapping (extHostChatAgents2.ts)
    ext_host = EXT_HOST_AGENTS.read_text()
    for field in ["groupKey", "badge", "badgeTooltip"]:
        assert field in ext_host, f"extHostChatAgents2.ts missing {field} passthrough"

    # Layer 4: MainThread mapping (mainThreadChatAgents2.ts)
    main = MAIN_THREAD.read_text()
    for field in ["groupKey", "badge", "badgeTooltip"]:
        assert field in main, f"mainThreadChatAgents2.ts missing {field} passthrough"

    # Layer 5: Internal interface — already checked by test_interface_new_fields


# [pr_diff] fail_to_pass
def test_infer_storage_from_uri():
    """List widget must have inferStorageFromUri that detects workspace vs user storage."""
    content = LIST_WIDGET.read_text()
    assert "inferStorageFromUri" in content, "inferStorageFromUri method not found"

    # Extract method region for deeper checks
    idx = content.index("inferStorageFromUri")
    method_region = content[idx:idx + 1500]

    # Must distinguish workspace (local) from user storage
    assert "PromptsStorage.local" in method_region or "local" in method_region, \
        "inferStorageFromUri should return local storage for workspace folders"
    assert "PromptsStorage.user" in method_region or "promptsHome" in method_region, \
        "inferStorageFromUri should detect user data prompts home"


# [pr_diff] fail_to_pass

    # groupKey-based grouping logic must exist
    assert "groupKey" in content, "groupKey not referenced in list widget"

    # Must build group headers from groupKey values
    assert "group-header" in content, "No group-header entries built from groupKey"

    # Must handle items without groupKey (ungrouped fallback)
    assert "ungrouped" in content.lower(), \
        "No fallback for items without groupKey (expected ungrouped handling)"

    # Must use a Map for grouping (O(1) lookups)
    assert "groupsMap" in content or "Map<string" in content, \
        "Expected Map-based grouping for groupKey items"


# ---------------------------------------------------------------------------
# Fail-to-pass (config_edit) — SKILL.md update tests
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass

    # Must document the extension API for customization providers
    assert "chatSessionCustomizationProvider" in content or "Extension API" in content, \
        "SKILL.md should document the chatSessionCustomizationProvider Extension API"

    # Must mention the internal interface
    assert "IExternalCustomizationItem" in content, \
        "SKILL.md should reference IExternalCustomizationItem"

    # Must document the IPC DTO layer
    assert "IChatSessionCustomizationItemDto" in content or "extHost.protocol" in content, \
        "SKILL.md should document the IPC DTO layer (extHost.protocol.ts)"

    # Must warn about keeping layers in sync when adding fields
    sync_mentioned = (
        "update all" in content.lower()
        or "five layers" in content.lower()
        or "all five" in content.lower()
        or "kept in sync" in content.lower()
    )
    assert sync_mentioned, \
        "SKILL.md should warn about updating all layers when adding new fields"


# [config_edit] fail_to_pass

    # Each layer should be mentioned (by file name or type name)
    layers = [
        ("proposed API", ["chatSessionCustomizationProvider.d.ts", "ChatSessionCustomizationItem"]),
        ("IPC DTO", ["extHost.protocol", "IChatSessionCustomizationItemDto"]),
        ("ExtHost", ["extHostChatAgents2", "provideChatSessionCustomizations"]),
        ("MainThread", ["mainThreadChatAgents2"]),
        ("internal interface", ["customizationHarnessService", "IExternalCustomizationItem"]),
    ]
    for layer_name, markers in layers:
        found = any(m in content for m in markers)
        assert found, f"SKILL.md missing reference to {layer_name} layer (expected one of: {markers})"
