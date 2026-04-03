"""
Task: maui-shell-query-clear-config-cleanup
Repo: dotnet/maui @ f73f0f7dabecaa2af50231522313e609ff78dcb7
PR:   33451

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/maui"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified C# files must exist and contain valid class/method structure."""
    nav_mgr = Path(REPO) / "src/Controls/src/Core/Shell/ShellNavigationManager.cs"
    assert nav_mgr.exists(), "ShellNavigationManager.cs must exist"
    content = nav_mgr.read_text()
    assert "class ShellNavigationManager" in content, "Must contain ShellNavigationManager class"
    assert "ApplyQueryAttributes" in content, "Must contain ApplyQueryAttributes method"
    assert content.count("{") > 10, "File appears corrupted (too few braces)"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests for the code fix
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_shellcontent_path_guards_empty_popping():
    """ShellContent code path must skip ApplyQueryAttributes when mergedData is empty and popping."""
    nav_mgr = Path(REPO) / "src/Controls/src/Core/Shell/ShellNavigationManager.cs"
    content = nav_mgr.read_text()

    method_start = content.find("public static void ApplyQueryAttributes(Element element")
    assert method_start != -1, "ApplyQueryAttributes method must exist"
    method_body = content[method_start:]

    # Find the ShellContent branch
    sc_idx = method_body.find("is ShellContent")
    assert sc_idx != -1, "Must have ShellContent branch in ApplyQueryAttributes"

    # Extract text between ShellContent branch and the isLastItem branch
    islastitem_idx = method_body.find("isLastItem", sc_idx + 50)
    assert islastitem_idx != -1, "Must have isLastItem branch"
    shellcontent_section = method_body[sc_idx:islastitem_idx]

    # The ApplyQueryAttributes call must be conditional on mergedData being non-empty
    # or not popping. Accept various equivalent guard formulations:
    #   if (mergedData.Count > 0 || !isPopping)       — positive guard
    #   if (mergedData.Count == 0 && isPopping) return — early return
    #   if (isPopping && mergedData.Count == 0) ...    — skip variant
    has_guard = bool(re.search(
        r'mergedData\.Count\s*>\s*0.*[|!].*isPopping|'
        r'!isPopping.*mergedData\.Count|'
        r'mergedData\.Count\s*==\s*0.*isPopping|'
        r'isPopping.*mergedData\.Count\s*==\s*0',
        shellcontent_section,
        re.DOTALL,
    ))
    assert has_guard, (
        "ShellContent branch must guard ApplyQueryAttributes call with "
        "a check combining mergedData.Count and isPopping"
    )


# [pr_diff] fail_to_pass
def test_lastitem_path_guards_empty_popping():
    """isLastItem code path must skip setting query attributes when mergedData is empty and popping."""
    nav_mgr = Path(REPO) / "src/Controls/src/Core/Shell/ShellNavigationManager.cs"
    content = nav_mgr.read_text()

    method_start = content.find("public static void ApplyQueryAttributes(Element element")
    assert method_start != -1
    method_body = content[method_start:]

    islastitem_idx = method_body.find("else if (isLastItem)")
    if islastitem_idx == -1:
        islastitem_idx = method_body.find("isLastItem")
    assert islastitem_idx != -1, "Must have isLastItem branch"

    # Extract the isLastItem block up to MergeData local function
    mergedata_func_idx = method_body.find("ShellRouteParameters MergeData", islastitem_idx)
    if mergedata_func_idx == -1:
        mergedata_func_idx = len(method_body)
    lastitem_section = method_body[islastitem_idx:mergedata_func_idx]

    # SetValue must be conditional on mergedData count or isPopping
    has_guard = bool(re.search(
        r'mergedData\.Count\s*>\s*0.*[|!].*isPopping|'
        r'!isPopping.*mergedData\.Count|'
        r'mergedData\.Count\s*==\s*0.*isPopping|'
        r'isPopping.*mergedData\.Count\s*==\s*0',
        lastitem_section,
        re.DOTALL,
    ))
    assert has_guard, (
        "isLastItem branch must guard SetValue with "
        "a check combining mergedData.Count and isPopping"
    )


# [pr_diff] fail_to_pass

    method_start = content.find("public static void ApplyQueryAttributes(Element element")
    method_body = content[method_start:]

    sc_idx = method_body.find("is ShellContent")
    assert sc_idx != -1
    islastitem_idx = method_body.find("isLastItem", sc_idx + 50)
    shellcontent_section = method_body[sc_idx:islastitem_idx]

    # The isPopping guard for SetValue must also check mergedData count
    # Before fix: `if (isPopping) { element.SetValue(...) }` — no count check
    # After fix: `if (isPopping && mergedData.Count > 0)` or equivalent
    # Also accept: early return when count == 0 && isPopping before the SetValue
    setvalue_line_match = re.search(
        r'if\s*\(isPopping\s*&&\s*mergedData\.Count\s*>\s*0|'
        r'if\s*\(mergedData\.Count\s*>\s*0\s*&&\s*isPopping|'
        r'mergedData\.Count\s*==\s*0\s*&&\s*isPopping|'
        r'isPopping\s*&&\s*mergedData\.Count\s*==\s*0',
        shellcontent_section,
    )
    assert setvalue_line_match is not None, (
        "SetValue for QueryAttributesProperty in ShellContent branch must require "
        "a check combining isPopping and mergedData.Count"
    )


# ---------------------------------------------------------------------------
# Config file update tests (config_edit) — agent must update these files
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass

    assert "### Opening PRs" not in content, (
        "copilot-instructions.md should not have an 'Opening PRs' section "
        "requiring the NOTE block"
    )
    assert "Are you waiting for the changes in this PR to be merged?" not in content, (
        "copilot-instructions.md should not contain the NOTE block text"
    )


# [config_edit] fail_to_pass

    assert "Are you waiting for the changes in this PR to be merged?" not in content, (
        "pr-finalize SKILL.md should not contain the NOTE block text"
    )
    assert "Start with the required NOTE block" not in content, (
        "pr-finalize SKILL.md should not require starting with a NOTE block"
    )


# [config_edit] fail_to_pass

    assert "Are you waiting for the changes in this PR to be merged?" not in content, (
        "complete-example.md should not contain the NOTE block text"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass — regressions / structural integrity
# ---------------------------------------------------------------------------

# [static] pass_to_pass


# [static] pass_to_pass


# [static] pass_to_pass
def test_nav_manager_method_signature_intact():
    """ApplyQueryAttributes method signature must remain unchanged."""
    nav_mgr = Path(REPO) / "src/Controls/src/Core/Shell/ShellNavigationManager.cs"
    content = nav_mgr.read_text()
    assert "public static void ApplyQueryAttributes(Element element, ShellRouteParameters query, bool isLastItem, bool isPopping)" in content, (
        "ApplyQueryAttributes method signature must not be changed"
    )
