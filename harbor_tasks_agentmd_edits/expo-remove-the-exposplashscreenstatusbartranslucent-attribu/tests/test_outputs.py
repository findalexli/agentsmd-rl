"""
Task: expo-remove-the-exposplashscreenstatusbartranslucent-attribu
Repo: expo/expo @ 9c5343ad06d7ecb11537d6c45e24086877a1fa08
PR:   43514

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/expo"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — XML well-formedness
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified XML files must be well-formed."""
    import xml.etree.ElementTree as ET

    xml_files = [
        "apps/bare-expo/android/app/src/main/res/values/strings.xml",
        "apps/expo-go/android/expoview/src/main/res/values/strings.xml",
        "apps/minimal-tester/android/app/src/main/res/values/strings.xml",
    ]
    for rel in xml_files:
        path = Path(REPO) / rel
        assert path.exists(), f"Missing: {rel}"
        ET.parse(str(path))  # raises ParseError if malformed


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — code changes
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_translucent_resource_removed():
    """expo_splash_screen_status_bar_translucent string must be removed from all apps."""
    xml_files = [
        "apps/bare-expo/android/app/src/main/res/values/strings.xml",
        "apps/expo-go/android/expoview/src/main/res/values/strings.xml",
        "apps/minimal-tester/android/app/src/main/res/values/strings.xml",
    ]
    for rel in xml_files:
        content = (Path(REPO) / rel).read_text()
        assert "expo_splash_screen_status_bar_translucent" not in content, (
            f"{rel} still contains expo_splash_screen_status_bar_translucent"
        )


# [pr_diff] fail_to_pass
def test_splash_screen_no_translucent_param():
    """SplashScreen.kt show/ensureShown must not accept statusBarTranslucent parameter."""
    splash_kt = (
        Path(REPO)
        / "apps/expo-go/android/expoview/src/main/java/host/exp/exponent"
        / "experience/splashscreen/legacy/singletons/SplashScreen.kt"
    )
    content = splash_kt.read_text()
    # The parameter declaration should be gone
    assert "statusBarTranslucent: Boolean" not in content, (
        "SplashScreen.kt still declares statusBarTranslucent parameter"
    )
    # The old configureTranslucent call should be replaced with setTranslucent
    assert "configureTranslucent" not in content, (
        "SplashScreen.kt still calls configureTranslucent instead of setTranslucent"
    )


# [pr_diff] fail_to_pass
def test_status_bar_set_translucent_simplified():
    """SplashScreenStatusBar must use setTranslucent(activity) without boolean param."""
    status_bar_kt = (
        Path(REPO)
        / "apps/expo-go/android/expoview/src/main/java/host/exp/exponent"
        / "experience/splashscreen/legacy/singletons/SplashScreenStatusBar.kt"
    )
    content = status_bar_kt.read_text()
    # Must have setTranslucent with single activity param
    assert re.search(r"fun\s+setTranslucent\s*\(\s*activity\s*:\s*Activity\s*\)", content), (
        "SplashScreenStatusBar should have setTranslucent(activity: Activity)"
    )
    # Must NOT have old configureTranslucent with translucent boolean
    assert "configureTranslucent" not in content, (
        "SplashScreenStatusBar still has configureTranslucent"
    )
    assert "translucent: Boolean" not in content, (
        "SplashScreenStatusBar still accepts translucent boolean"
    )


# [pr_diff] fail_to_pass
def test_experience_utils_set_translucent_no_boolean():
    """ExperienceActivityUtils.setTranslucent must take only activity, no boolean."""
    utils_kt = (
        Path(REPO)
        / "apps/expo-go/android/expoview/src/main/java/host/exp/exponent"
        / "utils/ExperienceActivityUtils.kt"
    )
    content = utils_kt.read_text()
    # Should have setTranslucent(activity: Activity) without boolean
    assert re.search(r"fun\s+setTranslucent\s*\(\s*activity\s*:\s*Activity\s*\)", content), (
        "ExperienceActivityUtils should have setTranslucent(activity: Activity)"
    )
    # Should NOT have translucent: Boolean param
    assert "translucent: Boolean" not in content, (
        "ExperienceActivityUtils.setTranslucent still accepts translucent boolean"
    )


# [pr_diff] fail_to_pass
def test_get_status_bar_translucent_removed():
    """getStatusBarTranslucent helper must be removed from lifecycle listener."""
    listener_kt = (
        Path(REPO)
        / "apps/expo-go/android/expoview/src/main/java/host/exp/exponent"
        / "experience/splashscreen/legacy/SplashScreenReactActivityLifecycleListener.kt"
    )
    content = listener_kt.read_text()
    assert "getStatusBarTranslucent" not in content, (
        "SplashScreenReactActivityLifecycleListener still has getStatusBarTranslucent"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (config_edit) — README documentation update
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_status_bar_still_applies_insets():
    """SplashScreenStatusBar.setTranslucent must still apply window insets (not be empty)."""
    status_bar_kt = (
        Path(REPO)
        / "apps/expo-go/android/expoview/src/main/java/host/exp/exponent"
        / "experience/splashscreen/legacy/singletons/SplashScreenStatusBar.kt"
    )
    content = status_bar_kt.read_text()
    # Must still contain the insets logic
    assert "setOnApplyWindowInsetsListener" in content, (
        "SplashScreenStatusBar.setTranslucent is missing insets listener"
    )
    assert "replaceSystemWindowInsets" in content, (
        "SplashScreenStatusBar.setTranslucent is missing replaceSystemWindowInsets"
    )
    assert "requestApplyInsets" in content, (
        "SplashScreenStatusBar.setTranslucent is missing requestApplyInsets"
    )
