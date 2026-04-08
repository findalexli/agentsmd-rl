"""
Task: gradio-colorpicker-events
Repo: gradio-app/gradio @ 3f835cf9c6cdf570a107233e2a87e0dc5cd751cb
PR:   12862

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import subprocess

REPO = "/workspace/gradio"
TARGET = f"{REPO}/js/colorpicker/shared/Colorpicker.svelte"


def _analyze_svelte() -> dict:
    """Run subprocess to parse the Svelte component and return structured analysis."""
    r = subprocess.run(
        ["python3", "-c", _PARSE_SCRIPT],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    if r.returncode != 0:
        raise RuntimeError(f"Parse error: {r.stderr}")
    return json.loads(r.stdout.strip())


_PARSE_SCRIPT = r"""
import re, json

content = open("/workspace/gradio/js/colorpicker/shared/Colorpicker.svelte").read()
lines = content.splitlines()

# Strip script blocks to isolate template
template = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL)
no_comments = re.sub(r'<!--.*?-->', '', template, flags=re.DOTALL)

# Legacy Svelte 4 on: directives in template
legacy = re.findall(
    r'\bon:(click|mousedown|mouseup|mousemove|change|focus|blur|keydown|keyup|input|submit)\b',
    no_comments,
)

# Native Svelte 5 onclick handler count
onclick_count = len(re.findall(r'\bonclick\s*=\s*\{', no_comments))

# Extract dialog-button element block
btn_block = ""
for i, line in enumerate(lines):
    if "dialog-button" in line:
        for j in range(i, min(i + 15, len(lines))):
            btn_block += lines[j] + "\n"
            if "/>" in lines[j]:
                break
        break

# Extract text input element block
input_block = ""
for i, line in enumerate(lines):
    if '<input' in line and 'type="text"' in line:
        for j in range(i, min(i + 15, len(lines))):
            input_block += lines[j] + "\n"
            if "/>" in lines[j]:
                break
        break

# Extract svelte:window section
window_section = ""
if "<svelte:window" in content:
    window_section = content.split("<svelte:window")[1].split("/>")[0]

result = {
    # Structure (p2p)
    "has_script": "<script" in content and "</script>" in content,
    "has_html": bool(re.search(r'<\w+', template)),
    "line_count": len([l for l in lines if l.strip()]),
    "button_count": content.count("<button"),
    "has_input": "<input" in content,
    "has_dialog": "dialog" in content.lower(),
    "has_color": "color" in content.lower(),
    # f2p: legacy events
    "legacy_events": legacy,
    # f2p: dialog button focus/blur
    "btn_has_onfocus": bool(re.search(r'onfocus\s*=\s*\{', btn_block)),
    "btn_has_onblur": bool(re.search(r'onblur\s*=\s*\{', btn_block)),
    "btn_onfocus_is_on_focus": bool(re.search(r'onfocus\s*=\s*\{on_focus\}', btn_block)),
    "btn_onblur_is_on_blur": bool(re.search(r'onblur\s*=\s*\{on_blur\}', btn_block)),
    # f2p: enter key submit
    "input_has_onkeydown": bool(re.search(r'onkeydown\s*=\s*\{', input_block)),
    "input_checks_enter": "Enter" in input_block,
    "input_calls_submit": bool(re.search(r'on_submit\s*\(\)', input_block)),
    # f2p: native click
    "onclick_count": onclick_count,
    # f2p: svelte:window
    "window_has_onmousemove": "onmousemove" in window_section,
    "window_has_onmouseup": "onmouseup" in window_section,
}

print(json.dumps(result))
"""


# ---------------------------------------------------------------------------
# Pass-to-pass (static)
# ---------------------------------------------------------------------------


def test_svelte_structure_valid():
    """File exists and has basic Svelte structure (script + template)."""
    data = _analyze_svelte()
    assert data["has_script"], "Missing <script> tag"
    assert data["has_html"], "No HTML elements in template"


def test_not_stub():
    """Component is a real implementation, not a stub."""
    data = _analyze_svelte()
    assert data["line_count"] > 100, f"Only {data['line_count']} non-empty lines"
    assert data["button_count"] >= 2, "Missing button elements"
    assert data["has_input"], "Missing input element"
    assert data["has_dialog"], "Missing dialog logic"
    assert data["has_color"], "Missing color-related code"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff)
# ---------------------------------------------------------------------------


def test_no_legacy_event_directives():
    """Template must not use Svelte 4 on:event directives."""
    data = _analyze_svelte()
    legacy = data["legacy_events"]
    assert len(legacy) == 0, (
        f"Found {len(legacy)} legacy on: directive(s): "
        + ", ".join(f"on:{e}" for e in legacy)
    )


def test_dialog_button_focus_and_blur():
    """Dialog button must have onfocus/onblur handlers calling on_focus/on_blur props."""
    data = _analyze_svelte()
    assert data["btn_has_onfocus"], "dialog-button missing onfocus handler"
    assert data["btn_has_onblur"], "dialog-button missing onblur handler"
    assert data["btn_onfocus_is_on_focus"], "onfocus does not call on_focus prop"
    assert data["btn_onblur_is_on_blur"], "onblur does not call on_blur prop"


def test_enter_key_triggers_submit():
    """Text input must fire on_submit when Enter is pressed."""
    data = _analyze_svelte()
    assert data["input_has_onkeydown"], "Text input missing onkeydown handler"
    assert data["input_checks_enter"], "onkeydown does not check for Enter key"
    assert data["input_calls_submit"], "onkeydown does not call on_submit()"


def test_native_click_handlers():
    """Buttons use native onclick instead of on:click."""
    data = _analyze_svelte()
    assert data["onclick_count"] >= 2, (
        f"Expected >=2 onclick, found {data['onclick_count']}"
    )


def test_svelte_window_native_handlers():
    """svelte:window uses native onmousemove/onmouseup."""
    data = _analyze_svelte()
    assert data["window_has_onmousemove"], "svelte:window missing onmousemove"
    assert data["window_has_onmouseup"], "svelte:window missing onmouseup"
