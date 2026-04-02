"""
Task: gradio-colorpicker-events
Repo: gradio-app/gradio @ 3f835cf9c6cdf570a107233e2a87e0dc5cd751cb
PR:   12862

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

TARGET = Path("/workspace/gradio/js/colorpicker/shared/Colorpicker.svelte")


def _read_template():
    """Read the Svelte file and return (full_content, template_only) with script stripped."""
    content = TARGET.read_text()
    # Strip <script> block to get template-only content
    template = re.sub(r"<script[^>]*>.*?</script>", "", content, flags=re.DOTALL)
    return content, template


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_svelte_structure_valid():
    """File exists and has basic Svelte structure (script + template)."""
    content = TARGET.read_text()
    assert "<script" in content, "Missing <script> tag"
    assert "</script>" in content, "Missing </script> close tag"
    # Must have at least one HTML element in template
    _, template = _read_template()
    assert re.search(r"<\w+", template), "No HTML elements in template"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_no_legacy_event_directives():
    # Regex-only because: Svelte component, cannot be imported/executed in Python
    """Template must not use Svelte 4 on:event directives (on:click, on:focus, etc.)."""
    _, template = _read_template()
    # Match on:word patterns that are event directives (not inside comments)
    # Remove HTML comments first
    no_comments = re.sub(r"<!--.*?-->", "", template, flags=re.DOTALL)
    legacy = re.findall(
        r"\bon:(click|mousedown|mouseup|mousemove|change|focus|blur|keydown|keyup|input|submit)\b",
        no_comments,
    )
    assert len(legacy) == 0, (
        f"Found {len(legacy)} legacy on: directive(s): {', '.join(f'on:{e}' for e in legacy)}"
    )


# [pr_diff] fail_to_pass
def test_dialog_button_focus_and_blur():
    # Regex-only because: Svelte component, cannot be imported/executed in Python
    """Dialog button (class=dialog-button) must have onfocus and onblur handlers
    that call the on_focus and on_blur prop callbacks."""
    content = TARGET.read_text()
    lines = content.splitlines()

    # Find the dialog-button element and collect its attribute lines until />
    btn_start = None
    for i, line in enumerate(lines):
        if "dialog-button" in line:
            btn_start = i
            break
    assert btn_start is not None, "dialog-button element not found"

    # Collect lines from button start until we find />
    btn_lines = []
    for i in range(btn_start, min(btn_start + 20, len(lines))):
        btn_lines.append(lines[i])
        if "/>" in lines[i]:
            break
    btn_block = "\n".join(btn_lines)

    assert re.search(r"\bonfocus\s*=\s*\{", btn_block), (
        "dialog-button missing onfocus handler"
    )
    assert re.search(r"\bonblur\s*=\s*\{", btn_block), (
        "dialog-button missing onblur handler"
    )
    # Verify the handlers reference the prop callbacks (anywhere in file is fine,
    # since the button is the only element with these handlers)
    assert re.search(r"\bonfocus\s*=\s*\{[^}]*on_focus", content) or \
           re.search(r"\bonfocus\s*=\s*\{on_focus\}", content), (
        "onfocus handler doesn't call on_focus prop"
    )
    assert re.search(r"\bonblur\s*=\s*\{[^}]*on_blur", content) or \
           re.search(r"\bonblur\s*=\s*\{on_blur\}", content), (
        "onblur handler doesn't call on_blur prop"
    )


# [pr_diff] fail_to_pass
def test_enter_key_triggers_submit():
    # Regex-only because: Svelte component, cannot be imported/executed in Python
    """Text input must have a keydown handler that fires on_submit when Enter is pressed."""
    content = TARGET.read_text()
    # Must have onkeydown (or onkeyup) with Enter check
    has_enter = bool(
        re.search(r"\bonkeydown\s*=\s*\{[^}]*[\"']Enter[\"']", content, re.DOTALL)
        or re.search(r"\bonkeyup\s*=\s*\{[^}]*[\"']Enter[\"']", content, re.DOTALL)
        or re.search(r"\bonkeydown\s*=\s*\{[^}]*keyCode\s*===?\s*13", content, re.DOTALL)
    )
    assert has_enter, "No Enter key handler found on text input"
    # The handler must call on_submit
    assert re.search(r"on_submit\s*\(", content), (
        "on_submit() is never called — Enter handler must trigger submit"
    )


# [pr_diff] fail_to_pass
def test_native_click_handlers():
    # Regex-only because: Svelte component, cannot be imported/executed in Python
    """Buttons and interactive elements use native onclick (not on:click)."""
    _, template = _read_template()
    no_comments = re.sub(r"<!--.*?-->", "", template, flags=re.DOTALL)
    # Must have at least 2 onclick handlers (dialog toggle + eyedropper or mode buttons)
    onclick_count = len(re.findall(r"\bonclick\s*=\s*\{", no_comments))
    assert onclick_count >= 2, (
        f"Expected >=2 onclick handlers, found {onclick_count}"
    )


# [pr_diff] fail_to_pass
def test_svelte_window_native_handlers():
    # Regex-only because: Svelte component, cannot be imported/executed in Python
    """<svelte:window> must use native onmousemove/onmouseup (not on:mousemove)."""
    content = TARGET.read_text()
    window_match = re.search(r"<svelte:window\s+([^/]*?)/>", content, re.DOTALL)
    assert window_match, "No <svelte:window> element found"
    window_attrs = window_match.group(1)
    assert "onmousemove" in window_attrs or "onmousemove" in content.split("<svelte:window")[1].split("/>")[0], (
        "svelte:window missing onmousemove"
    )
    assert "onmouseup" in window_attrs or "onmouseup" in content.split("<svelte:window")[1].split("/>")[0], (
        "svelte:window missing onmouseup"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub():
    """Component is a real implementation, not a stub."""
    content = TARGET.read_text()
    lines = [l for l in content.splitlines() if l.strip()]
    assert len(lines) > 100, f"Only {len(lines)} non-empty lines — looks like a stub"
    assert content.count("<button") >= 2, "Missing button elements"
    assert "<input" in content, "Missing input element"
    assert "dialog" in content.lower(), "Missing dialog logic"
    assert "color" in content.lower(), "Missing color-related code"
