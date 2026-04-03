"""
Task: expo-exporouter-use-kvc-to-provide
Repo: expo/expo @ a6d7308929a768de78b5c39b79f71572e6865bca
PR:   43620

Replace direct type casts to RNSBottomTabs* classes with KVC-based
RNScreensTabCompat utility for react-native-screens 4.23/4.24 compat,
and update CLAUDE.md to document Swift testing conventions.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/expo"
PKG = Path(REPO) / "packages" / "expo-router"
IOS = PKG / "ios"
LINK_PREVIEW = IOS / "LinkPreview"
NAV_FILE = LINK_PREVIEW / "LinkPreviewNativeNavigation.swift"
COMPAT_FILE = LINK_PREVIEW / "RNScreensTabCompat.swift"
CLAUDE_MD = PKG / "CLAUDE.md"
PODSPEC = IOS / "ExpoRouter.podspec"
TESTS_DIR = IOS / "Tests"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / structure checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified Swift files exist and are non-empty."""
    assert NAV_FILE.exists(), f"Missing {NAV_FILE}"
    assert NAV_FILE.stat().st_size > 100, "LinkPreviewNativeNavigation.swift is too small"
    assert CLAUDE_MD.exists(), f"Missing {CLAUDE_MD}"
    assert CLAUDE_MD.stat().st_size > 100, "CLAUDE.md is too small"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests for KVC compat layer
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_compat_file_exists_with_kvc_api():
    """RNScreensTabCompat.swift must exist with KVC-based tab detection API."""
    assert COMPAT_FILE.exists(), (
        f"Expected new file at {COMPAT_FILE.relative_to(REPO)}"
    )
    content = COMPAT_FILE.read_text()
    # Must define the enum/struct with the compat API
    assert "RNScreensTabCompat" in content, (
        "File must define RNScreensTabCompat type"
    )
    # Must use responds(to:) or KVC for dynamic dispatch — the whole point
    assert "responds(to:" in content or "value(forKey:" in content, (
        "RNScreensTabCompat must use responds(to:) or value(forKey:) for KVC"
    )


# [pr_diff] fail_to_pass
def test_compat_has_istabscreen():
    """RNScreensTabCompat must expose isTabScreen for type-check without casting."""
    content = COMPAT_FILE.read_text()
    assert "isTabScreen" in content, (
        "RNScreensTabCompat must provide isTabScreen method"
    )


# [pr_diff] fail_to_pass
def test_compat_has_tabkey():
    """RNScreensTabCompat must expose tabKey accessor for KVC property access."""
    content = COMPAT_FILE.read_text()
    assert "tabKey" in content, (
        "RNScreensTabCompat must provide tabKey accessor"
    )


# [pr_diff] fail_to_pass
def test_compat_has_tabbarcontroller_methods():
    """RNScreensTabCompat must expose tabBarController helpers for both screen and host."""
    content = COMPAT_FILE.read_text()
    assert "tabBarController" in content, (
        "RNScreensTabCompat must provide tabBarController helper(s)"
    )
    # Should handle both tab screen and tab host cases
    assert "fromTabScreen" in content or "fromTabHost" in content, (
        "Must distinguish tab screen vs tab host for tabBarController access"
    )


# [pr_diff] fail_to_pass
def test_navigation_uses_compat_not_direct_cast():
    """LinkPreviewNativeNavigation must use RNScreensTabCompat, not direct casts."""
    content = NAV_FILE.read_text()
    assert "RNScreensTabCompat" in content, (
        "LinkPreviewNativeNavigation must reference RNScreensTabCompat"
    )
    # The old direct casts to RNSBottomTabsScreenComponentView should be removed
    direct_cast_pattern = r'as\?\s+RNSBottomTabsScreenComponentView'
    matches = re.findall(direct_cast_pattern, content)
    assert len(matches) == 0, (
        f"Found {len(matches)} direct cast(s) to RNSBottomTabsScreenComponentView — "
        "these should be replaced with RNScreensTabCompat calls"
    )


# [pr_diff] fail_to_pass


# ---------------------------------------------------------------------------
# Fail-to-pass (config_edit) — CLAUDE.md must document Swift testing
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# ---------------------------------------------------------------------------
# Fail-to-pass — podspec and test file structure (new in this PR)
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_podspec_has_test_spec():
    """ExpoRouter.podspec must have a test_spec for Tests."""
    content = PODSPEC.read_text()
    assert "test_spec" in content, (
        "ExpoRouter.podspec should declare a test_spec"
    )
    assert "Tests" in content, (
        "ExpoRouter.podspec test_spec should reference Tests directory"
    )


# [pr_diff] fail_to_pass
def test_swift_test_file_exists():
    """Native Swift test file must exist in ios/Tests/."""
    test_files = list(TESTS_DIR.glob("*.swift")) if TESTS_DIR.exists() else []
    assert len(test_files) > 0, (
        f"Expected at least one Swift test file in {TESTS_DIR.relative_to(REPO)}"
    )
    # The test file should test the compat layer
    found_compat_test = False
    for tf in test_files:
        if "RNScreensTabCompat" in tf.read_text():
            found_compat_test = True
            break
    assert found_compat_test, (
        "At least one test file must test RNScreensTabCompat"
    )


# [pr_diff] fail_to_pass
def test_swift_test_uses_swift_testing():
    """Swift test file should use Swift Testing framework, not XCTest."""
    test_files = list(TESTS_DIR.glob("*.swift")) if TESTS_DIR.exists() else []
    assert len(test_files) > 0, "No test files found"
    # At least one test file should import Testing
    found = any("import Testing" in tf.read_text() for tf in test_files)
    assert found, (
        "Swift test files should use 'import Testing' (Swift Testing framework)"
    )
