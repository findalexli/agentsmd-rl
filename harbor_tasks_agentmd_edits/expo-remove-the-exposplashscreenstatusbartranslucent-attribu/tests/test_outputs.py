"""
Task: expo-remove-the-exposplashscreenstatusbartranslucent-attribu
Repo: expo/expo @ 9c5343ad06d7ecb11537d6c45e24086877a1fa08
PR:   43514

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import re
import subprocess
from pathlib import Path

REPO = "/workspace/expo"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _run_py(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute a Python snippet in the repo directory."""
    return subprocess.run(
        ["python3", "-c", code],
        capture_output=True, text=True, timeout=timeout, cwd=REPO,
    )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) - XML well-formedness
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified XML files must be well-formed."""
    xml_files = [
        "apps/bare-expo/android/app/src/main/res/values/strings.xml",
        "apps/expo-go/android/expoview/src/main/res/values/strings.xml",
        "apps/minimal-tester/android/app/src/main/res/values/strings.xml",
    ]
    for rel in xml_files:
        path = Path(REPO) / rel
        assert path.exists(), f"Missing: {rel}"
        import xml.etree.ElementTree as ET
        ET.parse(str(path))  # raises ParseError if malformed


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) - code changes, verified via subprocess
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_translucent_resource_removed():
    """expo_splash_screen_status_bar_translucent string must be removed from all apps."""
    r = _run_py("""
import xml.etree.ElementTree as ET
from pathlib import Path

REPO = "/workspace/expo"
xml_files = [
    "apps/bare-expo/android/app/src/main/res/values/strings.xml",
    "apps/expo-go/android/expoview/src/main/res/values/strings.xml",
    "apps/minimal-tester/android/app/src/main/res/values/strings.xml",
]
for rel in xml_files:
    tree = ET.parse(str(Path(REPO) / rel))
    for string_elem in tree.findall(".//string"):
        if string_elem.get("name") == "expo_splash_screen_status_bar_translucent":
            raise AssertionError(f"Found expo_splash_screen_status_bar_translucent in {rel}")
print("PASS")
""")
    assert r.returncode == 0, f"translucent resource still present: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_splash_screen_no_translucent_param():
    """SplashScreen.show/ensureShown must not accept statusBarTranslucent parameter."""
    r = _run_py("""
import re
from pathlib import Path

REPO = "/workspace/expo"
splash_kt = Path(REPO) / (
    "apps/expo-go/android/expoview/src/main/java/host/exp/exponent/"
    "experience/splashscreen/legacy/singletons/SplashScreen.kt"
)
content = splash_kt.read_text()

# Extract all function signatures with 'fun show' or 'fun ensureShown'
# and verify none have statusBarTranslucent parameter
sig_pattern = re.compile(
    r'fun\\s+(show|ensureShown)\\s*\\(([^)]*)\\)', re.DOTALL
)
for m in sig_pattern.finditer(content):
    params = m.group(2)
    if 'statusBarTranslucent' in params:
        raise AssertionError(
            f"Function {m.group(1)} still has statusBarTranslucent param: {params[:80]}"
        )
    if 'translucent: Boolean' in params:
        raise AssertionError(
            f"Function {m.group(1)} still has translucent: Boolean param"
        )

# Verify configureTranslucent is gone (replaced by setTranslucent)
if 'configureTranslucent' in content:
    raise AssertionError("SplashScreen.kt still calls configureTranslucent")

# Verify all show/ensureShown calls inside the file use setTranslucent
if 'SplashScreenStatusBar.setTranslucent' not in content:
    raise AssertionError("SplashScreen.kt does not call SplashScreenStatusBar.setTranslucent")

print("PASS")
""")
    assert r.returncode == 0, f"SplashScreen signature check failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_status_bar_set_translucent_simplified():
    """SplashScreenStatusBar must use setTranslucent(activity) without boolean param."""
    r = _run_py("""
import re
from pathlib import Path

REPO = "/workspace/expo"
status_bar_kt = Path(REPO) / (
    "apps/expo-go/android/expoview/src/main/java/host/exp/exponent/"
    "experience/splashscreen/legacy/singletons/SplashScreenStatusBar.kt"
)
content = status_bar_kt.read_text()

# Verify setTranslucent exists with single Activity param
sig = re.search(r'fun\\s+setTranslucent\\s*\\(\\s*activity\\s*:\\s*Activity\\s*\\)', content)
if not sig:
    raise AssertionError("SplashScreenStatusBar missing setTranslucent(activity: Activity)")

# Verify configureTranslucent is gone
if 'configureTranslucent' in content:
    raise AssertionError("SplashScreenStatusBar still has configureTranslucent")

# Verify no translucent: Boolean param anywhere in the object
if 'translucent: Boolean' in content:
    raise AssertionError("SplashScreenStatusBar still accepts translucent boolean")

# Verify the insets listener is always applied (no conditional branching)
# The old code had 
# The new code should NOT have setOnApplyWindowInsetsListener(null)
if 'setOnApplyWindowInsetsListener(null)' in content:
    raise AssertionError("SplashScreenStatusBar still has null listener fallback")

print("PASS")
""")
    assert r.returncode == 0, f"SplashScreenStatusBar check failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_experience_utils_set_translucent_no_boolean():
    """ExperienceActivityUtils.setTranslucent must take only activity, no boolean."""
    r = _run_py("""
import re
from pathlib import Path

REPO = "/workspace/expo"
utils_kt = Path(REPO) / (
    "apps/expo-go/android/expoview/src/main/java/host/exp/exponent/"
    "utils/ExperienceActivityUtils.kt"
)
content = utils_kt.read_text()

# Verify setTranslucent signature takes only activity
sig = re.search(r'fun\\s+setTranslucent\\(\\s*activity\\s*:\\s*Activity\\s*\\)', content)
if not sig:
    raise AssertionError("ExperienceActivityUtils missing setTranslucent(activity: Activity)")

# Verify old signature with boolean is gone
if 'translucent: Boolean' in content:
    raise AssertionError("ExperienceActivityUtils.setTranslucent still accepts translucent boolean")

# Verify call site in updateStatusBar uses setTranslucent(activity) without boolean
# The old code was: setTranslucent(statusBarTranslucent, activity)
# The new code should be: setTranslucent(activity)
call_pattern = re.compile(r'setTranslucent\\s*\\(([^)]*)\\)', re.MULTILINE)
for m in call_pattern.finditer(content):
    args = [a.strip() for a in m.group(1).split(',') if a.strip()]
    if len(args) > 1:
        raise AssertionError(
            f"setTranslucent called with multiple args: {m.group(0)}"
        )

# Verify the statusBarTranslucent local variable is removed
if 'val statusBarTranslucent' in content:
    raise AssertionError("statusBarTranslucent variable still exists in ExperienceActivityUtils")

print("PASS")
""")
    assert r.returncode == 0, f"ExperienceActivityUtils check failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_get_status_bar_translucent_removed():
    """getStatusBarTranslucent helper must be removed from lifecycle listener."""
    r = _run_py("""
from pathlib import Path

REPO = "/workspace/expo"
listener_kt = Path(REPO) / (
    "apps/expo-go/android/expoview/src/main/java/host/exp/exponent/"
    "experience/splashscreen/legacy/SplashScreenReactActivityLifecycleListener.kt"
)
content = listener_kt.read_text()

if 'getStatusBarTranslucent' in content:
    raise AssertionError("getStatusBarTranslucent still present")

# Verify ensureShown calls no longer pass statusBarTranslucent arg
# Old: ensureShown(activity, resizeMode, ReactRootView::class.java, getStatusBarTranslucent(activity))
# New: ensureShown(activity, resizeMode, ReactRootView::class.java)
import re
ensure_calls = re.findall(r'ensureShown\\s*\\([^)]+\\)', content, re.DOTALL)
for call in ensure_calls:
    args = [a.strip() for a in call.split(',') if a.strip()]
    if len(args) > 3:
        raise AssertionError(f"ensureShown called with >3 args: {call[:80]}")

print("PASS")
""")
    assert r.returncode == 0, f"getStatusBarTranslucent check failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_experience_activity_splash_screen_call():
    """ExperienceActivity must call SplashScreen.show without the translucent boolean arg."""
    r = _run_py("""
import re
from pathlib import Path

REPO = "/workspace/expo"
activity_kt = Path(REPO) / (
    "apps/expo-go/android/expoview/src/main/java/host/exp/exponent/"
    "experience/ExperienceActivity.kt"
)
content = activity_kt.read_text()

# Find SplashScreen.show calls
show_calls = re.findall(r'SplashScreen\\.show\\s*\\([^)]+\\)', content, re.DOTALL)
for call in show_calls:
    # The old code had: SplashScreen.show(this, managedAppSplashScreenViewController!!, true)
    # The new code: SplashScreen.show(this, managedAppSplashScreenViewController!!)
    if 'true' in call.split(',')[-1].strip().lower():
        raise AssertionError(
            f"SplashScreen.show still passes translucent boolean: {call[:100]}"
        )

print("PASS")
""")
    assert r.returncode == 0, f"ExperienceActivity call site check failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (static) - anti-stub
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
    assert "setOnApplyWindowInsetsListener" in content, (
        "SplashScreenStatusBar.setTranslucent is missing insets listener"
    )
    assert "replaceSystemWindowInsets" in content, (
        "SplashScreenStatusBar.setTranslucent is missing replaceSystemWindowInsets"
    )
    assert "requestApplyInsets" in content, (
        "SplashScreenStatusBar.setTranslucent is missing requestApplyInsets"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) - file validation
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_kotlin_files_valid():
    """Modified Kotlin files must have valid syntax (balanced braces/parens, package declarations)."""
    kotlin_files = [
        "apps/expo-go/android/expoview/src/main/java/host/exp/exponent/experience/splashscreen/legacy/singletons/SplashScreen.kt",
        "apps/expo-go/android/expoview/src/main/java/host/exp/exponent/experience/splashscreen/legacy/singletons/SplashScreenStatusBar.kt",
        "apps/expo-go/android/expoview/src/main/java/host/exp/exponent/utils/ExperienceActivityUtils.kt",
        "apps/expo-go/android/expoview/src/main/java/host/exp/exponent/experience/splashscreen/legacy/SplashScreenReactActivityLifecycleListener.kt",
        "apps/expo-go/android/expoview/src/main/java/host/exp/exponent/experience/ExperienceActivity.kt",
    ]
    for rel in kotlin_files:
        path = Path(REPO) / rel
        assert path.exists(), f"Missing: {rel}"
        content = path.read_text()
        # Basic syntax validation
        assert "package " in content, f"{rel}: missing package declaration"
        # Check braces are balanced (basic check)
        open_braces = content.count("{")
        close_braces = content.count("}")
        assert open_braces == close_braces, f"{rel}: unbalanced braces ({open_braces} vs {close_braces})"
        # Check parentheses are roughly balanced
        open_parens = content.count("(")
        close_parens = content.count(")")
        assert open_parens == close_parens, f"{rel}: unbalanced parentheses ({open_parens} vs {close_parens})"


# [static] pass_to_pass
def test_splash_screen_kt_structure():
    """SplashScreen.kt must have required object structure."""
    splash_kt = Path(REPO) / (
        "apps/expo-go/android/expoview/src/main/java/host/exp/exponent/"
        "experience/splashscreen/legacy/singletons/SplashScreen.kt"
    )
    content = splash_kt.read_text()
    # Check for required structure
    assert "object SplashScreen" in content, "Missing SplashScreen object declaration"
    assert "fun show(" in content, "Missing show function"
    assert "fun ensureShown(" in content, "Missing ensureShown function"
    assert "SingletonModule" in content, "Missing SingletonModule interface"


# [static] pass_to_pass
def test_splash_screen_status_bar_kt_structure():
    """SplashScreenStatusBar.kt must have required object structure."""
    status_bar_kt = Path(REPO) / (
        "apps/expo-go/android/expoview/src/main/java/host/exp/exponent/"
        "experience/splashscreen/legacy/singletons/SplashScreenStatusBar.kt"
    )
    content = status_bar_kt.read_text()
    # Check for required structure
    assert "object SplashScreenStatusBar" in content, "Missing SplashScreenStatusBar object declaration"
    assert "import android.app.Activity" in content, "Missing Activity import"
    assert "import androidx.core.view.ViewCompat" in content, "Missing ViewCompat import"


# [static] pass_to_pass
def test_experience_activity_utils_structure():
    """ExperienceActivityUtils.kt must have setTranslucent function."""
    utils_kt = Path(REPO) / (
        "apps/expo-go/android/expoview/src/main/java/host/exp/exponent/"
        "utils/ExperienceActivityUtils.kt"
    )
    content = utils_kt.read_text()
    # Check for required structure
    assert "object ExperienceActivityUtils" in content, "Missing ExperienceActivityUtils object declaration"
    assert "fun setTranslucent(" in content, "Missing setTranslucent function"
    assert "@UiThread" in content, "Missing @UiThread annotation"
