"""
Task: maui-android-fix-collectionview-selection-crash
Repo: dotnet/maui @ ecd6428d324e395ca07f8d375600c0fc93d0dd3c
PR:   34275

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/maui"

ADAPTER_PATH = (
    Path(REPO)
    / "src/Controls/src/Core/Handlers/Items/Android/Adapters"
    / "SelectableItemsViewAdapter.cs"
)
COPILOT_PATH = Path(REPO) / ".github" / "copilot-instructions.md"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

def test_syntax_check():
    """Modified C# files have balanced braces (basic syntax sanity)."""
    for fpath in [ADAPTER_PATH]:
        content = fpath.read_text()
        opens = content.count("{")
        closes = content.count("}")
        assert opens == closes, (
            f"{fpath.name}: unbalanced braces ({opens} open vs {closes} close)"
        )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests for the code fix
# ---------------------------------------------------------------------------

def test_header_footer_guard_in_onbindviewholder():
    """OnBindViewHolder must check IsHeader/IsFooter before selection tracking.

    The base code blindly adds all SelectableViewHolders (including header
    and footer) to _currentViewHolders. When MarkPlatformSelection later
    calls GetItem() on a header position, the internal AdjustIndexForHeader
    returns -1, causing ArgumentOutOfRangeException via ElementAt(-1).

    The fix must detect header/footer positions and skip them.
    """
    content = ADAPTER_PATH.read_text()

    # Extract the OnBindViewHolder method body
    method_match = re.search(
        r"public\s+override\s+void\s+OnBindViewHolder\b.*?\{(.*?)^\t\t\}",
        content,
        re.DOTALL | re.MULTILINE,
    )
    assert method_match, "OnBindViewHolder method not found"
    method_body = method_match.group(1)

    # Must check for header positions
    assert re.search(r"IsHeader\s*\(\s*position\s*\)", method_body), (
        "OnBindViewHolder must check IsHeader(position)"
    )
    # Must check for footer positions
    assert re.search(r"IsFooter\s*\(\s*position\s*\)", method_body), (
        "OnBindViewHolder must check IsFooter(position)"
    )


def test_guard_before_click_handler():
    """If the guard only skips _currentViewHolders.Add but still subscribes the
    click handler, the crash would still occur via SelectableClicked -> GetItem.
    The guard must early-return before the Clicked += line.
    """
    content = ADAPTER_PATH.read_text()

    method_match = re.search(
        r"public\s+override\s+void\s+OnBindViewHolder\b.*?\{(.*?)^\t\t\}",
        content,
        re.DOTALL | re.MULTILINE,
    )
    assert method_match, "OnBindViewHolder method not found"
    method_body = method_match.group(1)

    # Find the position of the header/footer check
    header_check = re.search(r"IsHeader\s*\(", method_body)
    assert header_check, "IsHeader check not found in OnBindViewHolder"

    # Find return statement after the header check (within ~10 lines)
    after_check = method_body[header_check.start():]
    return_match = re.search(r"\breturn\b", after_check)
    assert return_match, "No return after IsHeader/IsFooter check"

    # Find the click subscription
    click_sub = re.search(r"\.Clicked\s*\+=", method_body)
    assert click_sub, "Clicked += subscription not found"

    # The header/footer guard + return must appear BEFORE the click subscription
    guard_end = header_check.start() + return_match.end()
    assert guard_end < click_sub.start(), (
        "Header/footer guard must appear before Clicked += subscription"
    )


def test_guard_before_viewholders_add():
    """Even without the click handler, adding headers to _currentViewHolders
    causes MarkPlatformSelection to call GetItem on header positions.
    The guard must return before _currentViewHolders.Add as well.
    """
    content = ADAPTER_PATH.read_text()

    method_match = re.search(
        r"public\s+override\s+void\s+OnBindViewHolder\b.*?\{(.*?)^\t\t\}",
        content,
        re.DOTALL | re.MULTILINE,
    )
    assert method_match, "OnBindViewHolder method not found"
    method_body = method_match.group(1)

    header_check = re.search(r"IsHeader\s*\(", method_body)
    assert header_check, "IsHeader check not found"
    after_check = method_body[header_check.start():]
    return_match = re.search(r"\breturn\b", after_check)
    assert return_match, "No return after header/footer check"

    viewholder_add = re.search(r"_currentViewHolders\.Add\b", method_body)
    assert viewholder_add, "_currentViewHolders.Add not found"

    guard_end = header_check.start() + return_match.end()
    assert guard_end < viewholder_add.start(), (
        "Header/footer guard must appear before _currentViewHolders.Add"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (config_edit) — copilot-instructions.md update tests
# ---------------------------------------------------------------------------

def test_copilot_nullable_enable_documented():
    """PublicAPI.Unshipped.txt files require #nullable enable on the first line.
    If it gets moved (e.g., by sorting), the Roslyn analyzer emits RS0017 errors.
    The instructions must document this critical requirement.
    """
    content = COPILOT_PATH.read_text()

    assert "#nullable enable" in content, (
        "copilot-instructions.md must mention '#nullable enable'"
    )
    # Must reference PublicAPI files specifically
    assert "PublicAPI" in content or "publicapi" in content.lower(), (
        "copilot-instructions.md must reference PublicAPI files"
    )
    # Must mention it needs to be on line 1 / first line
    assert re.search(r"(line\s*1|first\s*line)", content, re.IGNORECASE), (
        "copilot-instructions.md must state #nullable enable goes on line 1 / first line"
    )


def test_copilot_bom_warning():
    """BOM bytes (0xEF 0xBB 0xBF) sort after ASCII under LC_ALL=C, which
    pushes #nullable enable to the bottom. The instructions must warn about this.
    """
    content = COPILOT_PATH.read_text()

    # Must warn about sort
    assert re.search(r"(never|don.t|do\s+not)\s+sort", content, re.IGNORECASE), (
        "copilot-instructions.md must warn against sorting PublicAPI files"
    )
    # Must mention BOM as the reason
    assert "BOM" in content or "0xEF" in content.lower() or "\xef\xbb\xbf" in content, (
        "copilot-instructions.md must mention BOM bytes as the reason"
    )


def test_copilot_merge_conflict_script():
    """The script should handle merge conflict resolution for PublicAPI.Unshipped.txt
    files while preserving the #nullable enable header line.
    """
    content = COPILOT_PATH.read_text()

    # Must include a bash script (code block with merge conflict handling)
    assert "```bash" in content or "```sh" in content, (
        "copilot-instructions.md should include a bash script example"
    )
    # Must reference merge conflict markers or diff-filter
    assert "conflict" in content.lower() or "diff-filter" in content.lower(), (
        "copilot-instructions.md script should handle merge conflicts"
    )
    # Must mention preserving/extracting the header
    assert re.search(r"(preserv|header|head\s+-1)", content, re.IGNORECASE), (
        "copilot-instructions.md script must preserve the header line"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub / regression
# ---------------------------------------------------------------------------

def test_existing_selection_logic_intact():
    """The rest of OnBindViewHolder's selection logic must remain intact.

    The fix only adds a guard — existing click handler subscription,
    _currentViewHolders tracking, and IsSelected marking must remain.
    """
    content = ADAPTER_PATH.read_text()

    method_match = re.search(
        r"public\s+override\s+void\s+OnBindViewHolder\b.*?\{(.*?)^\t\t\}",
        content,
        re.DOTALL | re.MULTILINE,
    )
    assert method_match, "OnBindViewHolder method not found"
    method_body = method_match.group(1)

    assert "SelectableClicked" in method_body, (
        "Clicked handler subscription must remain"
    )
    assert "_currentViewHolders.Add" in method_body, (
        "_currentViewHolders.Add must remain for normal items"
    )
    assert "IsSelected" in method_body, (
        "IsSelected marking must remain for normal items"
    )


def test_copilot_existing_publicapi_section_intact():
    """The existing PublicAPI.Unshipped.txt guidance must remain intact.

    The new #nullable enable warning supplements existing guidance — it must
    not replace the original four bullet points about PublicAPI management.
    """
    content = COPILOT_PATH.read_text()

    assert "Never disable analyzers" in content or "never disable" in content.lower(), (
        "Original 'Never disable analyzers' guidance must remain"
    )
    assert "dotnet format analyzers" in content, (
        "Original 'dotnet format analyzers' guidance must remain"
    )
