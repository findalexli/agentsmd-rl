"""
Task: ghost-added-welcomeemailsdesigncustomization-feature-flag
Repo: TryGhost/Ghost @ 85880f6f4b77a7624cd3b4482db107a508103777
PR:   26663

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/Ghost"

LABS_JS = Path(REPO) / "ghost/core/core/shared/labs.js"
PRIVATE_FEATURES_TSX = (
    Path(REPO)
    / "apps/admin-x-settings/src/components/settings/advanced/labs/private-features.tsx"
)
SKILL_DIR = Path(REPO) / ".claude/skills/add-private-feature-flag"
SKILL_FILE = SKILL_DIR / "SKILL.md"

FLAG_NAME = "welcomeEmailsDesignCustomization"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — existing flags must not be removed
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_existing_private_flags_preserved():
    """Existing PRIVATE_FEATURES entries must still be present in labs.js."""
    content = LABS_JS.read_text()
    expected_flags = [
        "transistor",
        "retentionOffers",
        "welcomeEmailEditor",
        "membersForward",
    ]
    for flag in expected_flags:
        assert (
            f"'{flag}'" in content or f'"{flag}"' in content
        ), f"Existing flag '{flag}' missing from PRIVATE_FEATURES in labs.js"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — code behavioral tests
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_flag_registered_in_labs_js():
    """welcomeEmailsDesignCustomization must be in PRIVATE_FEATURES array."""
    content = LABS_JS.read_text()
    # Find the PRIVATE_FEATURES array content
    match = re.search(
        r"PRIVATE_FEATURES\s*=\s*\[(.*?)\]", content, re.DOTALL
    )
    assert match, "PRIVATE_FEATURES array not found in labs.js"
    array_content = match.group(1)
    assert FLAG_NAME in array_content, (
        f"'{FLAG_NAME}' not found in PRIVATE_FEATURES array"
    )


# [pr_diff] fail_to_pass
def test_ui_toggle_added():
    """private-features.tsx must have a toggle entry for the new flag."""
    content = PRIVATE_FEATURES_TSX.read_text()
    assert FLAG_NAME in content, (
        f"'{FLAG_NAME}' not found in private-features.tsx"
    )
    # Verify the entry has a title and description (not just the flag string)
    # Find the block containing our flag
    idx = content.index(FLAG_NAME)
    # Look at the surrounding ~200 chars for title/description
    block = content[max(0, idx - 200) : idx + 100]
    assert "title" in block.lower() or "Title" in block, (
        "UI toggle entry missing 'title' field"
    )
    assert "description" in block.lower() or "Description" in block, (
        "UI toggle entry missing 'description' field"
    )


# [pr_diff] fail_to_pass
def test_flag_name_consistent_across_files():
    """Flag string must be identical in labs.js and private-features.tsx."""
    labs_content = LABS_JS.read_text()
    tsx_content = PRIVATE_FEATURES_TSX.read_text()
    # Extract all quoted strings from PRIVATE_FEATURES
    labs_match = re.search(
        r"PRIVATE_FEATURES\s*=\s*\[(.*?)\]", labs_content, re.DOTALL
    )
    assert labs_match, "PRIVATE_FEATURES array not found"
    labs_flags = set(re.findall(r"'(\w+)'", labs_match.group(1)))
    # The new flag must appear in both
    assert FLAG_NAME in labs_flags, f"'{FLAG_NAME}' not in labs.js PRIVATE_FEATURES"
    # In TSX, look for flag: 'flagName' pattern
    tsx_flags = set(re.findall(r"""flag:\s*['"](\w+)['"]""", tsx_content))
    assert FLAG_NAME in tsx_flags, f"'{FLAG_NAME}' not in private-features.tsx flags"


# ---------------------------------------------------------------------------
# Fail-to-pass (config_edit) — skill file creation tests
# ---------------------------------------------------------------------------


# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# [config_edit] fail_to_pass
