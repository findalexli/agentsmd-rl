"""
Task: gradio-dropdown-scroll-detach
Repo: gradio-app/gradio @ 7fb33fc3b80b421817c1d1ddea19c8858a9f2924
PR:   #12994

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/gradio"
FILE = Path(REPO) / "js/dropdown/shared/DropdownOptions.svelte"
POSITIONING_VARS = ["distance_from_top", "distance_from_bottom", "input_height"]


def _read_script_block():
    """Extract the <script> content and full source from the Svelte file."""
    src = FILE.read_text()
    match = re.search(r"<script[^>]*>([\s\S]*?)</script>", src)
    assert match, "Could not find <script> block in DropdownOptions.svelte"
    return match.group(1), src


def _extract_block(text: str, max_chars: int = 3000) -> str:
    """Extract the first balanced { ... } block from *text*."""
    depth = 0
    buf = []
    started = False
    for ch in text[:max_chars]:
        if ch == "{":
            depth += 1
            started = True
        if ch == "}":
            depth -= 1
        if started:
            buf.append(ch)
        if started and depth == 0:
            break
    return "".join(buf)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_positioning_vars_use_state():
    """All 3 positioning variables must be declared with $state() so Svelte 5
    reactivity tracks mutations made by scroll_listener / calculate_window_distance."""
    script, _ = _read_script_block()
    for var in POSITIONING_VARS:
        pat = re.compile(rf"let\s+{var}\b[^;\n]*=\s*\$state\s*[(<]")
        assert pat.search(script), (
            f"{var} is not declared with $state() — scroll position won't be reactive"
        )


# [pr_diff] fail_to_pass
def test_no_bare_positioning_declarations():
    """The old buggy pattern — bare `let <var>: number;` with no initialiser —
    must be absent for all 3 positioning variables."""
    script, _ = _read_script_block()
    for var in POSITIONING_VARS:
        buggy = re.compile(rf"let\s+{var}\s*:\s*\w+\s*;")
        assert not buggy.search(script), (
            f"{var} still has a bare 'let {var}: <type>;' declaration (not reactive)"
        )


# ---------------------------------------------------------------------------
# Pass-to-pass — regression + anti-stub
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_input_width_still_reactive():
    """input_width was already $state before the fix and must remain so."""
    script, _ = _read_script_block()
    assert re.search(r"let\s+input_width\b[^;\n]*=\s*\$state", script), (
        "input_width lost its $state reactivity"
    )


# [pr_diff] pass_to_pass
def test_effect_reads_positioning_vars():
    """$effect (or $effect.pre) block must reference at least one positioning
    variable so CSS properties update when the reactive values change."""
    script, _ = _read_script_block()
    effect_match = re.search(r"\$effect(?:\.pre)?\s*\(", script)
    assert effect_match, "$effect block not found"
    body = _extract_block(script[effect_match.start():])
    refs = sum(1 for v in POSITIONING_VARS if v in body)
    assert refs >= 1, (
        "$effect does not reference any positioning variables — "
        "CSS won't update on scroll"
    )


# [pr_diff] pass_to_pass
def test_template_structure_intact():
    """Dropdown template must render a <ul> list with CSS positioning and a
    show_options visibility guard."""
    _, src = _read_script_block()
    after_script = src[src.index("</script>") + 9:]
    assert re.search(r"<ul\b", after_script), "Missing <ul> list element in template"
    assert (
        re.search(r"style[=:].*top|top\s*:", after_script)
    ), "Missing top/bottom positioning in template styles"
    assert "show_options" in src, "Missing show_options visibility guard"


# [static] pass_to_pass
def test_not_stubbed():
    """File must have substantial content — not a gutted replacement."""
    script, src = _read_script_block()
    lines = len(src.strip().splitlines())
    funcs = len(re.findall(r"function\s+\w+", script))
    assert lines > 50, f"Only {lines} lines — file appears stubbed"
    assert funcs >= 2, f"Only {funcs} functions — file appears stubbed"
