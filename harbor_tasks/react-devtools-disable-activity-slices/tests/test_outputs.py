"""
Task: react-devtools-disable-activity-slices
Repo: facebook/react @ 3ce1316b05968d2a8cffe42a110f2726f2c44c3e
PR:   35685

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import re
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
# Fail-to-pass (pr_diff) — behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_flag_false_in_fb_configs():
    """Facebook build configs (core-fb, extension-fb) export enableActivitySlices = false."""
    for path in FB_CONFIGS:
        content = Path(path).read_text()
        # Find the export line and check it's set to false (exact match for Flow type syntax)
        pattern = r'export\s+const\s+enableActivitySlices\s*:\s*boolean\s*=\s*false\s*;'
        assert re.search(pattern, content), (
            f"enableActivitySlices should be 'export const enableActivitySlices: boolean = false;' in {path}"
        )


# [pr_diff] fail_to_pass
def test_flag_dev_in_oss_configs():
    """OSS configs export enableActivitySlices = __DEV__ (enabled in dev, disabled in prod)."""
    for path in OSS_CONFIGS:
        content = Path(path).read_text()
        # Find the export line and check it's set to __DEV__
        pattern = r'export\s+const\s+enableActivitySlices\s*:\s*boolean\s*=\s*__DEV__\s*;'
        assert re.search(pattern, content), (
            f"enableActivitySlices should be 'export const enableActivitySlices: boolean = __DEV__;' in {path}"
        )


# [pr_diff] fail_to_pass
def test_suspense_tab_imports_flag():
    """SuspenseTab.js imports enableActivitySlices from react-devtools-feature-flags."""
    content = Path(SUSPENSE_TAB).read_text()
    # Check for the import of enableActivitySlices from the feature flags module
    pattern = r'import\s*\{[^}]*enableActivitySlices[^}]*\}\s*from\s*[\'"]react-devtools-feature-flags[\'"];'
    assert re.search(pattern, content), (
        "No import of enableActivitySlices from react-devtools-feature-flags in SuspenseTab.js"
    )


# [pr_diff] fail_to_pass
def test_suspense_tab_uses_flag():
    """activityListDisabled expression correctly gates on !enableActivitySlices."""
    content = Path(SUSPENSE_TAB).read_text()

    # Extract the activityListDisabled assignment expression
    match = re.search(r'const\s+activityListDisabled\s*=\s*(.+?);', content)
    assert match, "activityListDisabled assignment not found in SuspenseTab.js"
    expr = match.group(1).strip()

    # The correct expression should be: !enableActivitySlices || activities.length === 0
    # Before the fix: activities.length === 0
    assert '!enableActivitySlices' in expr or 'enableActivitySlices === false' in expr, (
        f"Expression should gate on !enableActivitySlices, got: {expr}"
    )

    # Also verify the activities.length check is still there
    assert 'activities.length' in expr, (
        f"Expression should still check activities.length, got: {expr}"
    )

    # Verify the logical structure: flag disables OR no activities disables
    # Should be: !enableActivitySlices || activities.length === 0
    # (either condition being true means the list is disabled)
    expected_pattern = r'!\s*enableActivitySlices\s*\|\|\s*activities\.length\s*===\s*0'
    assert re.search(expected_pattern, expr), (
        f"Expected '!enableActivitySlices || activities.length === 0', got: {expr}"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (agent_config) — new flags must be in ALL fork files
# Source: .claude/skills/feature-flags/SKILL.md:45 @ 3ce1316b05968d2a8cffe42a110f2726f2c44c3e
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass
def test_flag_present_in_all_fork_files():
    """enableActivitySlices must be declared in every one of the 5 fork config files."""
    for path in ALL_CONFIGS:
        content = Path(path).read_text()
        assert 'enableActivitySlices' in content, (
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
        assert 'enableLogger' in content, (
            f"enableLogger flag missing from {path} — config file structure was corrupted"
        )


# [repo_tests] pass_to_pass - CI lint check
def test_repo_lint():
    """Repo's ESLint check passes (pass_to_pass)."""
    r = subprocess.run(
        ["node", "./scripts/tasks/eslint.js"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"ESLint failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


# [repo_tests] pass_to_pass - Flow typecheck
def test_repo_flow():
    """Repo's Flow typecheck passes for dom-node renderer (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "flow", "dom-node"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Flow check failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


# [repo_tests] pass_to_pass - syntax validation for feature flag files
def test_feature_flag_syntax():
    """All feature flag config files have valid JavaScript syntax (pass_to_pass)."""
    for path in ALL_CONFIGS:
        r = subprocess.run(
            ["node", "-c", path],
            capture_output=True, text=True, timeout=30, cwd=REPO,
        )
        assert r.returncode == 0, f"Syntax error in {path}:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass - SuspenseTab.js syntax validation
def test_suspense_tab_syntax():
    """SuspenseTab.js has valid JavaScript/Flow syntax (pass_to_pass)."""
    r = subprocess.run(
        ["node", "-c", SUSPENSE_TAB],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Syntax error in SuspenseTab.js:\n{r.stderr[-500:]}"
