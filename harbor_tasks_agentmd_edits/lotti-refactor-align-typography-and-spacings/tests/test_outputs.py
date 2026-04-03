"""
Task: lotti-refactor-align-typography-and-spacings
Repo: matthiasn/lotti @ e782947f64cde48b0bd77cc38d258eee41e22b16
PR:   2855

Refactor: replace hardcoded spacing/typography values with design-system tokens,
localize AM/PM labels, and update the design-system README.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/lotti"
DS = f"{REPO}/lib/features/design_system"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified Dart files exist and contain expected widget definitions."""
    files = {
        f"{DS}/components/calendar_pickers/design_system_time_calendar_picker.dart": "_MonthCalendarCard",
        f"{DS}/components/navigation/design_system_navigation_tab_bar.dart": "DesignSystemNavigationTabBar",
        f"{DS}/components/task_filters/design_system_task_filter_sheet.dart": "DesignSystemTaskFilterSheet",
        f"{DS}/components/task_list_items/design_system_task_list_item.dart": "_taskMetadataSpans",
        f"{DS}/components/time_pickers/design_system_time_picker.dart": "_DesignSystemTimePickerState",
        f"{DS}/components/toasts/design_system_toast.dart": "DesignSystemToast",
    }
    for path, expected_symbol in files.items():
        content = Path(path).read_text()
        assert expected_symbol in content, f"{Path(path).name} missing {expected_symbol}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — code behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_calendar_picker_uses_token_typography():
    """Calendar picker must use design-token typography, not Theme.of(context).textTheme."""
    content = Path(
        f"{DS}/components/calendar_pickers/design_system_time_calendar_picker.dart"
    ).read_text()
    # After the fix, typography comes from tokens not Theme.of(context).textTheme
    assert "typography.styles" in content, \
        "Calendar picker should use design-token typography styles"
    # Should not use Theme.of(context).textTheme for the main text styles
    # (weekday labels, month header, day buttons)
    theme_text_style_count = len(re.findall(
        r"Theme\.of\(context\)\.textTheme\.\w+\?\.copyWith", content
    ))
    assert theme_text_style_count == 0, \
        f"Calendar picker still has {theme_text_style_count} Theme.of(context).textTheme " \
        f"usages that should use design tokens"


# [pr_diff] fail_to_pass
def test_time_picker_localized_meridiem():
    """Time picker must use MaterialLocalizations for AM/PM, not hardcoded strings."""
    content = Path(
        f"{DS}/components/time_pickers/design_system_time_picker.dart"
    ).read_text()
    assert "anteMeridiemAbbreviation" in content, \
        "Time picker should use MaterialLocalizations.anteMeridiemAbbreviation"
    assert "postMeridiemAbbreviation" in content, \
        "Time picker should use MaterialLocalizations.postMeridiemAbbreviation"


# [pr_diff] fail_to_pass
def test_navigation_tab_bar_uses_token_typography():
    """Navigation tab bar must use token-based typography, not Theme.of(context).textTheme."""
    content = Path(
        f"{DS}/components/navigation/design_system_navigation_tab_bar.dart"
    ).read_text()
    assert "typography.styles" in content, \
        "Navigation tab bar should use design-token typography"
    # Should not use Theme.of(context).textTheme for label styling
    theme_refs = len(re.findall(
        r"Theme\.of\(context\)\.textTheme\.\w+\?\.copyWith", content
    ))
    assert theme_refs == 0, \
        f"Navigation tab bar still has {theme_refs} Theme.of(context).textTheme usages"


# [pr_diff] fail_to_pass
def test_task_filter_uses_token_spacing():
    """Task filter sheet must use token-based spacing instead of hardcoded const values."""
    content = Path(
        f"{DS}/components/task_filters/design_system_task_filter_sheet.dart"
    ).read_text()
    # After fix, should use spacing.step references extensively
    step_refs = len(re.findall(r"spacing\.step\d+", content))
    assert step_refs >= 10, \
        f"Task filter should use token spacing extensively (found {step_refs}, expected >= 10)"
    # The old hardcoded const paddings should be replaced
    # Check that Theme.of(context).textTheme is not used for counter text
    assert "typography.styles" in content, \
        "Task filter should use token typography for text styles"


# [pr_diff] fail_to_pass


# [pr_diff] fail_to_pass


# ---------------------------------------------------------------------------
# Fail-to-pass (config_edit) — config/documentation update tests
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass — lib/features/design_system/README.md


# [config_edit] fail_to_pass — lib/features/design_system/README.md
