"""
Task: gradio-dropdown-slowdown-destructure
Repo: gradio-app/gradio @ e5ba4fa992c0ac389c6af2d143c9ad4c33eea360
PR:   12944

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

Note: All tests use regex on Svelte source because Svelte components cannot
be imported or executed from Python. This is the equivalent of AST checks
for a non-Python, non-compilable-from-Python language.
"""

import re
from pathlib import Path

TARGET = Path("/workspace/gradio/js/dropdown/shared/Dropdown.svelte")


def _read_target():
    assert TARGET.exists(), f"{TARGET} not found"
    return TARGET.read_text()


def _script_section(content: str) -> str:
    """Extract the <script> block from a Svelte component."""
    m = re.search(r"<script[^>]*>(.*?)</script>", content, re.DOTALL)
    assert m, "No <script> tag found in Dropdown.svelte"
    return m.group(1)


def _template_section(content: str) -> str:
    """Extract everything outside <script> tags (the template markup)."""
    return re.sub(r"<script[^>]*>.*?</script>", "", content, flags=re.DOTALL)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_no_array_destructure_from_derived():
    """The buggy pattern `let [input_text, selected_index] = $derived.by(...)`
    must be removed — it causes O(N) re-derivations per dropdown option."""
    content = _read_target()

    buggy = re.search(
        r"let\s*\[.*?input_text.*?,.*?selected_index.*?\]\s*=\s*\$derived",
        content,
        re.DOTALL,
    )
    assert not buggy, (
        "Array destructuring from $derived.by for input_text/selected_index still present"
    )


# [pr_diff] fail_to_pass
def test_input_text_reactive_variable():
    """input_text must be a standalone reactive variable ($state or $derived),
    not array-destructured from a combined derivation."""
    script = _script_section(_read_target())

    # Accept: let input_text = $state(...) or let input_text: <type> = $state(...)
    # Also accept $derived if someone chose a different valid approach
    assert re.search(
        r"let\s+input_text\s*(?::\s*\S+\s*)?=\s*\$(?:state|derived)", script
    ), "input_text must be declared as its own $state or $derived variable"


# [pr_diff] fail_to_pass
def test_selected_index_reactive_variable():
    """selected_index must be a standalone reactive variable ($state or $derived),
    not array-destructured from a combined derivation."""
    script = _script_section(_read_target())

    assert re.search(
        r"let\s+selected_index\s*(?::\s*[^=]+)?=\s*\$(?:state|derived)", script
    ), "selected_index must be declared as its own $state or $derived variable"


# [pr_diff] fail_to_pass
def test_variables_update_on_value_change():
    """input_text and selected_index must reactively track changes to the
    value prop via $effect or $derived — not just be static initial values."""
    script = _script_section(_read_target())

    # Pattern A: $effect that assigns input_text based on value
    has_effect = bool(
        re.search(
            r"\$effect\s*\(\s*\(\s*\)\s*=>\s*\{[^}]*input_text\s*=",
            script,
            re.DOTALL,
        )
    )
    # Pattern B: input_text = $derived(...value...) or $derived.by(...)
    has_derived = bool(
        re.search(
            r"input_text\s*=\s*\$derived(?:\.by)?\s*\(",
            script,
        )
    )
    assert has_effect or has_derived, (
        "No reactive logic updates input_text/selected_index when value changes"
    )


# [pr_diff] fail_to_pass
def test_template_no_inline_selected_indices():
    """Template must not compute selected_indices inline as
    `selected_index === null ? [] : [selected_index]` — this creates
    a new array reference on every access, amplifying reactive cascades."""
    template = _template_section(_read_target())

    inline = re.search(
        r"selected_index\s*===\s*null\s*\?\s*\[\]\s*:\s*\[selected_index\]",
        template,
    )
    assert not inline, (
        "Template still has inline selected_indices ternary computation"
    )


# [pr_diff] fail_to_pass
def test_selected_indices_derived():
    """selected_indices must be a pre-computed $derived variable so the template
    uses a stable reference instead of creating a new array on every access."""
    script = _script_section(_read_target())

    assert re.search(
        r"let\s+selected_indices\s*=\s*\$derived", script
    ), "selected_indices not declared as a $derived variable"


# [pr_diff] fail_to_pass
def test_template_uses_selected_indices():
    """Template must reference the pre-computed selected_indices variable
    (as a prop shorthand {selected_indices} or explicit prop assignment)."""
    template = _template_section(_read_target())

    uses_shorthand = bool(re.search(r"\{selected_indices\}", template))
    uses_prop = bool(re.search(r"selected_indices\s*=\s*\{", template))
    assert uses_shorthand or uses_prop, (
        "Template doesn't reference the selected_indices variable"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub():
    """Dropdown.svelte must retain substantial implementation logic —
    the fix should only change reactive variable declarations, not gut the file."""
    content = _read_target()

    line_count = content.count("\n")
    assert line_count > 100, f"File too short ({line_count} lines) — likely stubbed"

    # Must still have core dropdown functionality
    assert "handle_option_selected" in content, "Missing handle_option_selected function"
    assert "DropdownOptions" in content or "dropdown" in content.lower(), (
        "Missing dropdown component references"
    )

    reactive_refs = len(re.findall(r"\$(state|derived|effect|props)", content))
    assert reactive_refs >= 3, f"Too few reactive declarations ({reactive_refs})"
