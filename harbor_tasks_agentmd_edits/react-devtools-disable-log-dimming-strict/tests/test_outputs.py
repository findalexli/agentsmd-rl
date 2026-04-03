"""
Task: react-devtools-disable-log-dimming-strict
Repo: facebook/react @ ba5b843692519a226347aecfb789d90fcb24b4bc
PR:   35207

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/react"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — code behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_hook_settings_type_has_dimming_field():
    """DevToolsHookSettings type includes disableSecondConsoleLogDimmingInStrictMode."""
    types_file = Path(REPO) / "packages/react-devtools-shared/src/backend/types.js"
    content = types_file.read_text()
    assert "disableSecondConsoleLogDimmingInStrictMode" in content, (
        "DevToolsHookSettings should include disableSecondConsoleLogDimmingInStrictMode field"
    )


# [pr_diff] fail_to_pass
def test_hook_checks_dimming_setting():
    """installHook() in hook.js checks disableSecondConsoleLogDimmingInStrictMode before dimming."""
    hook_file = Path(REPO) / "packages/react-devtools-shared/src/hook.js"
    content = hook_file.read_text()
    # The setting must be referenced in hook.js to control dimming behavior
    occurrences = content.count("disableSecondConsoleLogDimmingInStrictMode")
    assert occurrences >= 2, (
        f"hook.js should reference disableSecondConsoleLogDimmingInStrictMode "
        f"at least twice (default + check), found {occurrences}"
    )


# [pr_diff] fail_to_pass
def test_hook_default_settings_include_dimming():
    """Default settings object in hook.js includes disableSecondConsoleLogDimmingInStrictMode: false."""
    hook_file = Path(REPO) / "packages/react-devtools-shared/src/hook.js"
    content = hook_file.read_text()
    # Find the default settings block and verify the new field is present
    # The default settings are defined near the end of installHook
    match = re.search(
        r"disableSecondConsoleLogDimmingInStrictMode\s*:\s*false",
        content,
    )
    assert match, (
        "Default settings should include disableSecondConsoleLogDimmingInStrictMode: false"
    )


# [pr_diff] fail_to_pass
def test_debugging_settings_ui_has_dimming_control():
    """DebuggingSettings component includes state and UI for the dimming setting."""
    settings_file = (
        Path(REPO)
        / "packages/react-devtools-shared/src/devtools/views/Settings/DebuggingSettings.js"
    )
    content = settings_file.read_text()
    assert "disableSecondConsoleLogDimmingInStrictMode" in content, (
        "DebuggingSettings should include disableSecondConsoleLogDimmingInStrictMode"
    )
    # Should have a useState call for this setting
    assert re.search(
        r"useState\(.*disableSecondConsoleLogDimmingInStrictMode",
        content,
        re.DOTALL,
    ) or "setDisableSecondConsoleLogDimmingInStrictMode" in content, (
        "DebuggingSettings should have state management for the dimming setting"
    )


# [pr_diff] fail_to_pass
def test_hook_settings_injector_validates_dimming():
    """hookSettingsInjector validates disableSecondConsoleLogDimmingInStrictMode type."""
    injector_file = (
        Path(REPO)
        / "packages/react-devtools-extensions/src/contentScripts/hookSettingsInjector.js"
    )
    content = injector_file.read_text()
    assert "disableSecondConsoleLogDimmingInStrictMode" in content, (
        "hookSettingsInjector should validate the disableSecondConsoleLogDimmingInStrictMode setting"
    )


# [pr_diff] fail_to_pass
def test_inline_backend_passes_dimming_setting():
    """react-devtools-inline backend.js passes disableSecondConsoleLogDimmingInStrictMode through."""
    backend_file = Path(REPO) / "packages/react-devtools-inline/src/backend.js"
    content = backend_file.read_text()
    assert "disableSecondConsoleLogDimmingInStrictMode" in content, (
        "inline backend.js should pass disableSecondConsoleLogDimmingInStrictMode to the window"
    )
    # Should set the __REACT_DEVTOOLS_ global for it
    assert "__REACT_DEVTOOLS_DISABLE_SECOND_CONSOLE_LOG_DIMMING_IN_STRICT_MODE__" in content, (
        "inline backend.js should set the window global for disable dimming"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (config_edit) — README documentation tests
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass
