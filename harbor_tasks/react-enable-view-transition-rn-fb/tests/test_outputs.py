"""
Task: react-enable-view-transition-rn-fb
Repo: facebook/react @ b4546cd0d4db2b913d8e7503bee86e1844073b2e
PR:   36106

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/react"
FLAG_NATIVE_FB = f"{REPO}/packages/shared/forks/ReactFeatureFlags.native-fb.js"
FLAG_TEST_RN   = f"{REPO}/packages/shared/forks/ReactFeatureFlags.test-renderer.native-fb.js"
FLAG_TEST_WWW  = f"{REPO}/packages/shared/forks/ReactFeatureFlags.test-renderer.www.js"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core flag changes
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_enable_view_transition_native_fb():
    """enableViewTransition is set to true in ReactFeatureFlags.native-fb.js."""
    content = Path(FLAG_NATIVE_FB).read_text()
    m = re.search(r'export const enableViewTransition\b.*?=\s*(\S+?)\s*;', content)
    assert m is not None, "enableViewTransition declaration not found in native-fb.js"
    actual = m.group(1)
    assert actual == "true", (
        f"enableViewTransition should be 'true' in native-fb.js, found: '{actual}'"
    )


# [pr_diff] fail_to_pass
def test_enable_view_transition_test_renderer_native_fb():
    """enableViewTransition is set to true in ReactFeatureFlags.test-renderer.native-fb.js."""
    content = Path(FLAG_TEST_RN).read_text()
    m = re.search(r'export const enableViewTransition\b.*?=\s*(\S+?)\s*;', content)
    assert m is not None, "enableViewTransition declaration not found in test-renderer.native-fb.js"
    actual = m.group(1)
    assert actual == "true", (
        f"enableViewTransition should be 'true' in test-renderer.native-fb.js, found: '{actual}'"
    )


# [pr_diff] fail_to_pass
def test_enable_view_transition_test_renderer_www():
    """enableViewTransition is set to true in ReactFeatureFlags.test-renderer.www.js."""
    content = Path(FLAG_TEST_WWW).read_text()
    m = re.search(r'export const enableViewTransition\b.*?=\s*(\S+?)\s*;', content)
    assert m is not None, "enableViewTransition declaration not found in test-renderer.www.js"
    actual = m.group(1)
    assert actual == "true", (
        f"enableViewTransition should be 'true' in test-renderer.www.js, found: '{actual}'"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub: no collateral flag changes
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_no_unintended_flag_changes():
    """Other flags remain at their base-commit values — only enableViewTransition was changed."""
    # These flags were all false at the base commit and must stay false.
    flags_must_stay_false = [
        "enableGestureTransition",
        "enableSuspenseyImages",
        "enableYieldingBeforePassive",
        "enableThrottledScheduling",
    ]
    for filepath in [FLAG_NATIVE_FB, FLAG_TEST_RN, FLAG_TEST_WWW]:
        content = Path(filepath).read_text()
        for flag in flags_must_stay_false:
            m = re.search(
                rf'export const {flag}(?::\s*\w+)?\s*=\s*(\S+?)\s*;', content
            )
            if m:
                actual = m.group(1)
                assert actual == "false", (
                    f"{flag} should remain 'false' in {Path(filepath).name}, "
                    f"found: '{actual}' — only enableViewTransition should be changed"
                )


# ---------------------------------------------------------------------------
# Agent-config derived (agent_config) — .claude/skills/feature-flags/SKILL.md
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — .claude/skills/feature-flags/SKILL.md:78 @ b4546cd0d4db2b913d8e7503bee86e1844073b2e
def test_all_fork_files_have_view_transition_enabled():
    """All three fork files must have enableViewTransition enabled (not just one).

    Rule: 'Missing fork files — New flags must be added to ALL fork files, not just the main one'
    Source: .claude/skills/feature-flags/SKILL.md line 78
    """
    # AST-only because: JavaScript files, not Python; using regex text check.
    files = {
        "native-fb.js": FLAG_NATIVE_FB,
        "test-renderer.native-fb.js": FLAG_TEST_RN,
        "test-renderer.www.js": FLAG_TEST_WWW,
    }
    missing = []
    for name, filepath in files.items():
        content = Path(filepath).read_text()
        m = re.search(r'export const enableViewTransition\b.*?=\s*(\S+?)\s*;', content)
        if m is None or m.group(1) != "true":
            found = m.group(1) if m else "not found"
            missing.append(f"{name}: {found}")

    assert not missing, (
        "enableViewTransition must be 'true' in ALL fork files. "
        "Still false/missing in: " + ", ".join(missing)
    )
