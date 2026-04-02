"""
Task: react-enable-fragment-refs-flags
Repo: facebook/react @ a74302c02d220e3663fcad5836cb90607fc2d006
PR:   36026

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/react"

MAIN_FLAGS       = Path(f"{REPO}/packages/shared/ReactFeatureFlags.js")
NATIVE_OSS_FLAGS = Path(f"{REPO}/packages/shared/forks/ReactFeatureFlags.native-oss.js")
TEST_RENDERER    = Path(f"{REPO}/packages/shared/forks/ReactFeatureFlags.test-renderer.js")
TEST_WWW         = Path(f"{REPO}/packages/shared/forks/ReactFeatureFlags.test-renderer.www.js")


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — file existence / syntax
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_required_files_exist():
    """All 4 feature flag files must be present and have export const syntax."""
    for f in [MAIN_FLAGS, NATIVE_OSS_FLAGS, TEST_RENDERER, TEST_WWW]:
        assert f.exists(), f"Required file missing: {f}"
        assert "export const" in f.read_text(), f"File missing export syntax: {f}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core flag value changes
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_main_instance_handles_enabled():
    """enableFragmentRefsInstanceHandles must be true in ReactFeatureFlags.js (was false)."""
    content = MAIN_FLAGS.read_text()
    assert "enableFragmentRefsInstanceHandles: boolean = true;" in content, \
        "enableFragmentRefsInstanceHandles should be true in ReactFeatureFlags.js"
    assert "enableFragmentRefsInstanceHandles: boolean = false;" not in content, \
        "enableFragmentRefsInstanceHandles still false in ReactFeatureFlags.js"


# [pr_diff] fail_to_pass
def test_native_oss_instance_handles_enabled():
    """enableFragmentRefsInstanceHandles must be true in ReactFeatureFlags.native-oss.js (was false)."""
    content = NATIVE_OSS_FLAGS.read_text()
    assert "enableFragmentRefsInstanceHandles: boolean = true;" in content, \
        "enableFragmentRefsInstanceHandles should be true in native-oss.js"
    assert "enableFragmentRefsInstanceHandles: boolean = false;" not in content, \
        "enableFragmentRefsInstanceHandles still false in native-oss.js"


# [pr_diff] fail_to_pass
def test_native_oss_text_nodes_enabled():
    """enableFragmentRefsTextNodes must be true in ReactFeatureFlags.native-oss.js (was false)."""
    content = NATIVE_OSS_FLAGS.read_text()
    assert "enableFragmentRefsTextNodes: boolean = true;" in content, \
        "enableFragmentRefsTextNodes should be true in native-oss.js"
    assert "enableFragmentRefsTextNodes: boolean = false;" not in content, \
        "enableFragmentRefsTextNodes still false in native-oss.js"


# [pr_diff] fail_to_pass
def test_test_renderer_instance_handles_enabled():
    """enableFragmentRefsInstanceHandles must be true in ReactFeatureFlags.test-renderer.js (was false)."""
    content = TEST_RENDERER.read_text()
    assert "enableFragmentRefsInstanceHandles: boolean = true;" in content, \
        "enableFragmentRefsInstanceHandles should be true in test-renderer.js"
    assert "enableFragmentRefsInstanceHandles: boolean = false;" not in content, \
        "enableFragmentRefsInstanceHandles still false in test-renderer.js"


# [pr_diff] fail_to_pass
def test_www_all_fragment_flags_enabled():
    """All 4 fragment ref flags must be true in ReactFeatureFlags.test-renderer.www.js (all were false)."""
    content = TEST_WWW.read_text()
    for flag_true in [
        "enableFragmentRefs: boolean = true;",
        "enableFragmentRefsScrollIntoView: boolean = true;",
        "enableFragmentRefsInstanceHandles: boolean = true;",
        "enableFragmentRefsTextNodes: boolean = true;",
    ]:
        assert flag_true in content, \
            f"{flag_true.split(':')[0]} should be true in test-renderer.www.js"
    for flag_false in [
        "enableFragmentRefs: boolean = false;",
        "enableFragmentRefsScrollIntoView: boolean = false;",
        "enableFragmentRefsInstanceHandles: boolean = false;",
        "enableFragmentRefsTextNodes: boolean = false;",
    ]:
        assert flag_false not in content, \
            f"{flag_false.split(':')[0]} still false in test-renderer.www.js"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — structural consistency
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_no_duplicate_flag_definitions():
    """Each fragment ref flag must be defined at most once per file."""
    flags = [
        "enableFragmentRefs",
        "enableFragmentRefsScrollIntoView",
        "enableFragmentRefsInstanceHandles",
        "enableFragmentRefsTextNodes",
    ]
    for f in [MAIN_FLAGS, NATIVE_OSS_FLAGS, TEST_RENDERER, TEST_WWW]:
        content = f.read_text()
        for flag in flags:
            count = content.count(f"{flag}:")
            assert count <= 1, f"{flag} defined {count} times in {f.name}"


# [static] pass_to_pass
def test_flag_values_are_boolean_literals():
    """Fragment ref flags must use boolean literal syntax (true/false/__VARIANT__), not expressions."""
    pattern = re.compile(r"enableFragmentRefs\w*\s*:\s*boolean\s*=\s*(.+?);")
    for f in [MAIN_FLAGS, NATIVE_OSS_FLAGS, TEST_RENDERER, TEST_WWW]:
        content = f.read_text()
        for match in pattern.finditer(content):
            value = match.group(1).strip()
            assert value in ("true", "false", "__VARIANT__"), \
                f"Non-literal flag value in {f.name}: {match.group(0)}"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from .claude/skills/feature-flags/SKILL.md
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — .claude/skills/feature-flags/SKILL.md:15 @ a74302c02d220e3663fcad5836cb90607fc2d006
def test_instance_handles_in_all_forks():
    """enableFragmentRefsInstanceHandles enabled in ALL fork files (SKILL.md: 'Add to ALL fork files')."""
    for f in [MAIN_FLAGS, NATIVE_OSS_FLAGS, TEST_RENDERER, TEST_WWW]:
        content = f.read_text()
        assert "enableFragmentRefsInstanceHandles: boolean = true;" in content, \
            f"enableFragmentRefsInstanceHandles not enabled in {f.name} — must propagate to all forks"
