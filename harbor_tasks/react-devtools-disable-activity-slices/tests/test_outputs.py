"""
Task: react-devtools-disable-activity-slices
Repo: facebook/react @ 3ce1316b05968d2a8cffe42a110f2726f2c44c3e
PR:   35685

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

from pathlib import Path

REPO = "/workspace/react"
CONFIG_DIR = f"{REPO}/packages/react-devtools-shared/src/config"
SUSPENSE_TAB = f"{REPO}/packages/react-devtools-shared/src/devtools/views/SuspenseTab/SuspenseTab.js"

FB_CONFIGS = [
    f"{CONFIG_DIR}/DevToolsFeatureFlags.core-fb.js",
    f"{CONFIG_DIR}/DevToolsFeatureFlags.extension-fb.js",
]

OSS_CONFIGS = [
    f"{CONFIG_DIR}/DevToolsFeatureFlags.core-oss.js",
    f"{CONFIG_DIR}/DevToolsFeatureFlags.extension-oss.js",
    f"{CONFIG_DIR}/DevToolsFeatureFlags.default.js",
]

ALL_CONFIGS = FB_CONFIGS + OSS_CONFIGS


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_flag_false_in_fb_configs():
    """Facebook build configs (core-fb, extension-fb) must set enableActivitySlices = false."""
    for path in FB_CONFIGS:
        content = Path(path).read_text()
        assert "export const enableActivitySlices: boolean = false;" in content, (
            f"Missing 'export const enableActivitySlices: boolean = false;' in {path}"
        )


# [pr_diff] fail_to_pass
def test_flag_dev_in_oss_configs():
    """OSS build configs (core-oss, extension-oss, default) must set enableActivitySlices = __DEV__."""
    for path in OSS_CONFIGS:
        content = Path(path).read_text()
        assert "export const enableActivitySlices: boolean = __DEV__;" in content, (
            f"Missing 'export const enableActivitySlices: boolean = __DEV__;' in {path}"
        )


# [pr_diff] fail_to_pass
def test_suspense_tab_imports_flag():
    """SuspenseTab.js must import enableActivitySlices from react-devtools-feature-flags."""
    content = Path(SUSPENSE_TAB).read_text()
    assert "enableActivitySlices" in content, (
        "SuspenseTab.js does not reference enableActivitySlices"
    )
    assert "react-devtools-feature-flags" in content, (
        "SuspenseTab.js does not import from 'react-devtools-feature-flags'"
    )
    # Verify the import specifically brings in enableActivitySlices
    lines = content.splitlines()
    import_lines = [l for l in lines if "enableActivitySlices" in l and "import" in l]
    assert import_lines, (
        "No import statement found for enableActivitySlices in SuspenseTab.js"
    )


# [pr_diff] fail_to_pass
def test_suspense_tab_uses_flag():
    """SuspenseTab.js must gate activityListDisabled on !enableActivitySlices."""
    content = Path(SUSPENSE_TAB).read_text()
    assert "!enableActivitySlices" in content, (
        "SuspenseTab.js does not use '!enableActivitySlices' in disabled check"
    )
    assert "activityListDisabled" in content, (
        "SuspenseTab.js does not define activityListDisabled"
    )
    # The disabled flag must combine both conditions
    lines = content.splitlines()
    disabled_line = next(
        (l for l in lines if "activityListDisabled" in l and "=" in l and "!enableActivitySlices" in l),
        None,
    )
    assert disabled_line is not None, (
        "activityListDisabled assignment does not reference !enableActivitySlices"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (agent_config) — rule: new flags must be in ALL fork files
# Source: .claude/skills/feature-flags/SKILL.md:45 @ 3ce1316b
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass
def test_flag_present_in_all_fork_files():
    """enableActivitySlices must be declared in every one of the 5 fork config files."""
    for path in ALL_CONFIGS:
        content = Path(path).read_text()
        assert "enableActivitySlices" in content, (
            f"enableActivitySlices flag missing from {path} — "
            "all fork files must declare every new flag"
        )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — regression guard
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_flag_files_maintain_structure():
    """All 5 feature flag config files still export enableLogger (existing flag, not removed)."""
    for path in ALL_CONFIGS:
        content = Path(path).read_text()
        assert "enableLogger" in content, (
            f"enableLogger flag missing from {path} — config file structure was corrupted"
        )
