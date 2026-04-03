"""
Task: electron-docs-add-api-history-gi
Repo: electron/electron @ 378659c535b2b0a92bdbe82a790fa0799e53df9f
PR:   #50194

Add API history YAML blocks to Electron API docs (G-I range) and create
a docs/CLAUDE.md guide for the API history migration workflow.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

import yaml

REPO = "/workspace/electron"


def _extract_yaml_history_blocks(text: str) -> list[str]:
    """Extract all YAML history blocks from markdown content."""
    pattern = r"<!--\s*\n```YAML history\n(.*?)```\s*\n-->"
    return re.findall(pattern, text, re.DOTALL)


def _has_history_block_for_method(text: str, method_heading: str, pr_number: int) -> bool:
    """Check if a YAML history block with the given PR exists after the method heading."""
    # Find the method heading position
    idx = text.find(method_heading)
    if idx == -1:
        return False
    # Look at the content between this heading and the next heading (or end)
    rest = text[idx + len(method_heading):]
    next_heading = re.search(r"\n#{1,4} ", rest)
    section = rest[:next_heading.start()] if next_heading else rest
    return f"pull/{pr_number}" in section and "YAML history" in section


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — existing content preserved
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_existing_api_descriptions_preserved():
    """Core API descriptions in modified docs are not clobbered."""
    gs = Path(f"{REPO}/docs/api/global-shortcut.md").read_text()
    assert "globalShortcut" in gs, "global-shortcut.md missing module name"
    assert "register/unregister a global keyboard shortcut" in gs, \
        "global-shortcut.md missing module description"

    iap = Path(f"{REPO}/docs/api/in-app-purchase.md").read_text()
    assert "inAppPurchase" in iap, "in-app-purchase.md missing module name"
    assert "Mac App Store" in iap, "in-app-purchase.md missing platform description"

    ipc = Path(f"{REPO}/docs/api/ipc-main.md").read_text()
    assert "ipcMain" in ipc, "ipc-main.md missing module name"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — API history YAML blocks added
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_global_shortcut_register_has_history():
    """globalShortcut.register must have a YAML history block referencing PR #534."""
    text = Path(f"{REPO}/docs/api/global-shortcut.md").read_text()
    assert _has_history_block_for_method(
        text, "### `globalShortcut.register(accelerator, callback)`", 534
    ), "globalShortcut.register missing YAML history block with PR #534"


# [pr_diff] fail_to_pass
def test_global_shortcut_register_all_has_history():
    """globalShortcut.registerAll must have a YAML history block referencing PR #15542."""
    text = Path(f"{REPO}/docs/api/global-shortcut.md").read_text()
    assert _has_history_block_for_method(
        text, "### `globalShortcut.registerAll(accelerators, callback)`", 15542
    ), "globalShortcut.registerAll missing YAML history block with PR #15542"


# [pr_diff] fail_to_pass
def test_in_app_purchase_purchaseproduct_has_changes():
    """inAppPurchase.purchaseProduct must have changes entries including promisification PR #17355."""
    text = Path(f"{REPO}/docs/api/in-app-purchase.md").read_text()
    blocks = _extract_yaml_history_blocks(text)
    found_changes = False
    for block in blocks:
        parsed = yaml.safe_load(block)
        if parsed and "changes" in parsed:
            for change in parsed["changes"]:
                if "17355" in change.get("pr-url", ""):
                    found_changes = True
                    assert "description" in change, "changes entry must have a description"
                    assert "Promise" in change["description"] or "promise" in change["description"], \
                        "promisification change should mention Promise"
                    break
    assert found_changes, "inAppPurchase.purchaseProduct missing changes entry for PR #17355"


# [pr_diff] fail_to_pass
def test_ipc_main_handle_has_history():
    """ipcMain.handle must have a YAML history block referencing PR #18449."""
    text = Path(f"{REPO}/docs/api/ipc-main.md").read_text()
    assert _has_history_block_for_method(
        text, "### `ipcMain.handle(channel, listener)`", 18449
    ), "ipcMain.handle missing YAML history block with PR #18449"


# [pr_diff] fail_to_pass
def test_image_view_class_has_history():
    """ImageView class must have a YAML history block referencing PR #46760."""
    text = Path(f"{REPO}/docs/api/image-view.md").read_text()
    assert _has_history_block_for_method(
        text, "## Class: ImageView extends `View`", 46760
    ), "ImageView class missing YAML history block with PR #46760"


# [pr_diff] fail_to_pass


# [pr_diff] fail_to_pass


# ---------------------------------------------------------------------------
# Config edit tests — docs/CLAUDE.md and root CLAUDE.md
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# [config_edit] fail_to_pass
