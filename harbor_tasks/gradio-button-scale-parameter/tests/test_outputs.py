"""
Task: gradio-button-scale-parameter
Repo: gradio-app/gradio @ a0fff5cb0e4cc0f8cc3fff7b5fbe18a031c7cc27
PR:   12911

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

Regex-based because: Svelte components cannot be imported/executed from Python
without the full Node.js + pnpm toolchain (not installed in test environment).
"""

import re
from pathlib import Path

TARGET = Path("/workspace/gradio/js/button/Index.svelte")


def _read_clean():
    """Read the file and strip comments."""
    content = TARGET.read_text()
    content = re.sub(r"//.*?$", "", content, flags=re.MULTILINE)
    content = re.sub(r"/\*.*?\*/", "", content, flags=re.DOTALL)
    return content


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_svelte_parses():
    """Index.svelte exists and has basic Svelte structure."""
    content = TARGET.read_text()
    assert "<script" in content, "Missing <script> tag"
    assert "<Button" in content, "Missing <Button> component usage"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_scale_reads_from_shared():
    """Button's scale prop is bound to gradio.shared.scale, not gradio.props.scale."""
    content = _read_clean()

    # Find all <Button ...> tags and extract scale={...} bindings
    button_tags = re.findall(r"<Button\s+([^>]*)/??>", content, re.DOTALL)
    assert button_tags, "No <Button> tag found in template"

    scale_values = []
    for tag in button_tags:
        m = re.search(r"scale\s*=\s*\{([^}]+)\}", tag)
        if m:
            scale_values.append(m.group(1).strip())

    assert scale_values, "No scale={...} binding found on <Button>"

    for val in scale_values:
        assert "gradio.props.scale" not in val, (
            f"Bug not fixed: scale still reads from gradio.props.scale (got: {val})"
        )
        # Must reference gradio.shared (the correct source for shared props)
        assert "gradio.shared" in val, (
            f"scale should read from gradio.shared, got: {val}"
        )


# [pr_diff] fail_to_pass
def test_scale_not_in_button_props():
    """scale field removed from ButtonProps type definition (it's a shared prop)."""
    content = _read_clean()

    # Find the props type block — either interface ButtonProps { ... }
    # or a destructuring type annotation: let { ... }: { ... }
    interface_m = re.search(
        r"(?:interface|type)\s+ButtonProps\s*[={]\s*\{([^}]*)\}", content, re.DOTALL
    )
    destruct_m = re.search(
        r"let\s*\{[^}]*\}\s*:\s*\{([^}]+)\}", content, re.DOTALL
    )

    props_block = None
    if interface_m:
        props_block = interface_m.group(1)
    elif destruct_m:
        props_block = destruct_m.group(1)

    if props_block is not None:
        # scale should NOT appear as a typed property
        assert not re.search(r"\bscale\s*:", props_block), (
            "scale is still declared in ButtonProps — it should be removed "
            "because scale is a shared prop"
        )
    else:
        # If no recognizable props block, ensure scale isn't typed anywhere as a prop
        assert not re.search(r"\bscale\s*:\s*number\b", content), (
            "scale is still typed as number somewhere in the file"
        )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_other_props_intact():
    """Other ButtonProps fields (value, variant, size, link, icon) still present."""
    content = _read_clean()
    # These props must still appear in the file (as type annotations or bindings)
    for prop in ["value", "variant", "size", "link", "icon"]:
        assert re.search(rf"\b{prop}\b", content), (
            f"Expected prop '{prop}' missing — agent may have over-deleted"
        )


# [static] pass_to_pass
def test_not_stub():
    """File has meaningful Svelte component (not emptied or stubbed)."""
    content = TARGET.read_text()
    assert len(content) >= 200, "File too small — likely stubbed"

    script_m = re.search(r"<script[^>]*>(.*?)</script>", content, re.DOTALL)
    assert script_m, "No <script> section found"
    assert len(script_m.group(1).strip()) >= 50, "Script section too small"

    assert "gradio" in content, "No gradio reference — file was likely replaced"
