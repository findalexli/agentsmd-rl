"""
Task: react-css-shorthand-list
Repo: facebook/react @ 12ba7d81297abac61012a36f20d4a9d22b9210d9
PR:   35636

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/react"
CSS_FILE = f"{REPO}/packages/react-dom-bindings/src/client/CSSShorthandProperty.js"


def _parse_shorthand_map():
    """Parse CSSShorthandProperty.js and return dict of shorthand -> [longhands]."""
    text = Path(CSS_FILE).read_text()
    result = {}
    # Match entries like:  propertyName: ['longhand1', 'longhand2'],
    pattern = r"(\w+):\s*\[([^\]]+)\]"
    for m in re.finditer(pattern, text):
        key = m.group(1)
        values = re.findall(r"'(\w+)'", m.group(2))
        result[key] = values
    return result


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_valid_js_syntax():
    """CSSShorthandProperty.js must parse without JS syntax errors."""
    assert Path(CSS_FILE).exists(), "CSSShorthandProperty.js not found"
    r = subprocess.run(
        ["node", "--check", CSS_FILE],
        capture_output=True, timeout=15,
    )
    assert r.returncode == 0, (
        f"Syntax error in CSSShorthandProperty.js:\n{r.stderr.decode()}"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_border_logical_properties_added():
    """borderBlock, borderInline and their color/style/width variants must be present with correct longhands."""
    mapping = _parse_shorthand_map()

    # borderBlock expands to 6 longhands
    assert "borderBlock" in mapping, "borderBlock missing from shorthandToLonghand"
    assert set(mapping["borderBlock"]) == {
        "borderBlockEndColor", "borderBlockEndStyle", "borderBlockEndWidth",
        "borderBlockStartColor", "borderBlockStartStyle", "borderBlockStartWidth",
    }, f"borderBlock longhands incorrect: {mapping['borderBlock']}"

    # borderBlockColor / borderBlockStyle / borderBlockWidth (single-axis)
    assert "borderBlockColor" in mapping, "borderBlockColor missing"
    assert set(mapping["borderBlockColor"]) == {"borderBlockEndColor", "borderBlockStartColor"}

    assert "borderBlockStyle" in mapping, "borderBlockStyle missing"
    assert set(mapping["borderBlockStyle"]) == {"borderBlockEndStyle", "borderBlockStartStyle"}

    assert "borderBlockWidth" in mapping, "borderBlockWidth missing"
    assert set(mapping["borderBlockWidth"]) == {"borderBlockEndWidth", "borderBlockStartWidth"}

    # borderInline expands to 6 longhands
    assert "borderInline" in mapping, "borderInline missing from shorthandToLonghand"
    assert set(mapping["borderInline"]) == {
        "borderInlineEndColor", "borderInlineEndStyle", "borderInlineEndWidth",
        "borderInlineStartColor", "borderInlineStartStyle", "borderInlineStartWidth",
    }, f"borderInline longhands incorrect: {mapping['borderInline']}"

    assert "borderInlineColor" in mapping, "borderInlineColor missing"
    assert set(mapping["borderInlineColor"]) == {"borderInlineEndColor", "borderInlineStartColor"}

    assert "borderInlineStyle" in mapping, "borderInlineStyle missing"
    assert "borderInlineWidth" in mapping, "borderInlineWidth missing"


# [pr_diff] fail_to_pass
def test_inset_and_block_inline_spacing_added():
    """inset, marginBlock, marginInline, paddingBlock, paddingInline, insetBlock, insetInline must be present."""
    mapping = _parse_shorthand_map()

    # inset expands to 4 physical sides
    assert "inset" in mapping, "inset missing"
    assert set(mapping["inset"]) == {"bottom", "left", "right", "top"}, \
        f"inset longhands incorrect: {mapping['inset']}"

    # insetBlock / insetInline
    assert "insetBlock" in mapping, "insetBlock missing"
    assert set(mapping["insetBlock"]) == {"insetBlockEnd", "insetBlockStart"}

    assert "insetInline" in mapping, "insetInline missing"
    assert set(mapping["insetInline"]) == {"insetInlineEnd", "insetInlineStart"}

    # margin logical shorthands
    assert "marginBlock" in mapping, "marginBlock missing"
    assert set(mapping["marginBlock"]) == {"marginBlockEnd", "marginBlockStart"}

    assert "marginInline" in mapping, "marginInline missing"
    assert set(mapping["marginInline"]) == {"marginInlineEnd", "marginInlineStart"}

    # padding logical shorthands
    assert "paddingBlock" in mapping, "paddingBlock missing"
    assert set(mapping["paddingBlock"]) == {"paddingBlockEnd", "paddingBlockStart"}

    assert "paddingInline" in mapping, "paddingInline missing"
    assert set(mapping["paddingInline"]) == {"paddingInlineEnd", "paddingInlineStart"}


# [pr_diff] fail_to_pass
def test_container_scroll_and_misc_properties_added():
    """container, containIntrinsicSize, scrollMargin, scrollPadding, fontSynthesis, offset must be present."""
    mapping = _parse_shorthand_map()

    # container
    assert "container" in mapping, "container missing"
    assert set(mapping["container"]) == {"containerName", "containerType"}

    # containIntrinsicSize
    assert "containIntrinsicSize" in mapping, "containIntrinsicSize missing"
    assert set(mapping["containIntrinsicSize"]) == {"containIntrinsicHeight", "containIntrinsicWidth"}

    # scrollMargin (4 sides)
    assert "scrollMargin" in mapping, "scrollMargin missing"
    assert set(mapping["scrollMargin"]) == {
        "scrollMarginBottom", "scrollMarginLeft", "scrollMarginRight", "scrollMarginTop"
    }

    # scrollPadding (4 sides)
    assert "scrollPadding" in mapping, "scrollPadding missing"
    assert set(mapping["scrollPadding"]) == {
        "scrollPaddingBottom", "scrollPaddingLeft", "scrollPaddingRight", "scrollPaddingTop"
    }

    # scrollMarginBlock / scrollPaddingBlock
    assert "scrollMarginBlock" in mapping, "scrollMarginBlock missing"
    assert "scrollPaddingBlock" in mapping, "scrollPaddingBlock missing"

    # fontSynthesis
    assert "fontSynthesis" in mapping, "fontSynthesis missing"
    assert set(mapping["fontSynthesis"]) == {
        "fontSynthesisPosition", "fontSynthesisSmallCaps",
        "fontSynthesisStyle", "fontSynthesisWeight",
    }

    # offset
    assert "offset" in mapping, "offset missing"
    assert "offsetAnchor" in mapping["offset"]
    assert "offsetPath" in mapping["offset"]


# [pr_diff] fail_to_pass
def test_source_comment_updated_to_firefox():
    """Source comment must reference mozilla-firefox/firefox (not old gecko-dev URL)."""
    text = Path(CSS_FILE).read_text()
    assert "mozilla-firefox/firefox" in text, \
        "Source comment not updated to mozilla-firefox/firefox URL"
    assert "firefox/blob/" in text, \
        "Expected specific firefox blob URL in comment"
    # Old gecko-dev URL should no longer be present
    assert "gecko-dev" not in text, \
        "Old gecko-dev URL still present; comment should reference mozilla-firefox/firefox"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression / anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_existing_shorthands_preserved():
    """Pre-existing shorthand properties must still be in the mapping with non-empty longhand lists."""
    mapping = _parse_shorthand_map()

    required = {
        "animation": {"animationDelay", "animationDuration", "animationName"},
        "background": {"backgroundColor", "backgroundImage"},
        "border": {"borderColor", "borderStyle", "borderWidth"},
        "flex": {"flexBasis", "flexGrow", "flexShrink"},
        "font": {"fontFamily", "fontSize", "fontStyle"},
        "margin": {"marginBottom", "marginLeft", "marginRight", "marginTop"},
        "padding": {"paddingBottom", "paddingLeft", "paddingRight", "paddingTop"},
        "transition": {"transitionDelay", "transitionDuration", "transitionProperty"},
    }

    for shorthand, expected_subset in required.items():
        assert shorthand in mapping, f"Existing shorthand '{shorthand}' was removed"
        actual = set(mapping[shorthand])
        missing = expected_subset - actual
        assert not missing, \
            f"Existing shorthand '{shorthand}' is missing longhands: {missing}"
