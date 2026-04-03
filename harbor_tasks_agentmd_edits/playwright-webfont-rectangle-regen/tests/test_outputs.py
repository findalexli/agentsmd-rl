"""
Task: playwright-webfont-rectangle-regen
Repo: microsoft/playwright @ c1385dc133b5846ffdaf3eafdbb9b46a1be1575d
PR:   39092

Replace complex octicons-based webfont glyphs with simple filled rectangles
to eliminate antialiasing-sensitive screenshot test flakiness. Create a
generation script and update the README with regeneration instructions.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

REPO = "/workspace/playwright"
WEBFONT_DIR = Path(REPO) / "tests" / "assets" / "webfont"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_svg_valid_xml():
    """The iconfont.svg file must be valid XML."""
    svg_path = WEBFONT_DIR / "iconfont.svg"
    assert svg_path.exists(), "iconfont.svg not found"
    content = svg_path.read_text()
    tree = ET.fromstring(content)
    assert tree.tag == "{http://www.w3.org/2000/svg}svg" or tree.tag == "svg", \
        f"Root element should be <svg>, got {tree.tag}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_generate_font_script_runs():
    """generate_font.py must exist and produce a valid woff2 file when run."""
    script = WEBFONT_DIR / "generate_font.py"
    assert script.exists(), "generate_font.py not found"

    # Run the script — it should produce iconfont.woff2
    output_woff2 = WEBFONT_DIR / "iconfont.woff2"
    original_size = output_woff2.stat().st_size if output_woff2.exists() else 0

    r = subprocess.run(
        ["python3", str(script)],
        capture_output=True, timeout=30,
    )
    assert r.returncode == 0, \
        f"generate_font.py failed:\n{r.stdout.decode()}\n{r.stderr.decode()}"
    assert output_woff2.exists(), "generate_font.py did not produce iconfont.woff2"
    assert output_woff2.stat().st_size > 0, "Generated woff2 is empty"


# [pr_diff] fail_to_pass
def test_font_glyphs_are_rectangles():
    """SVG glyph paths must be simple rectangles, not complex bezier curves."""
    svg_path = WEBFONT_DIR / "iconfont.svg"
    content = svg_path.read_text()

    # The old complex octicons glyphs had many bezier curve commands (a, c, s, z patterns)
    # The new simplified glyphs should use only basic rectangle path commands
    assert "M531 527" not in content, \
        "SVG still contains old complex plus glyph path"
    assert "M104 350" not in content, \
        "SVG still contains old complex minus glyph path"

    # Parse the SVG and check glyph path data is simple
    tree = ET.parse(str(svg_path))
    ns = {"svg": "http://www.w3.org/2000/svg"}
    glyphs = tree.findall(".//svg:glyph", ns) or tree.findall(".//glyph")
    named_glyphs = [g for g in glyphs if g.get("glyph-name") in ("plus", "minus", "hyphen")]
    assert len(named_glyphs) >= 2, \
        f"Expected at least 2 named glyphs (plus/minus), found {len(named_glyphs)}"

    for glyph in named_glyphs:
        d = glyph.get("d", "")
        # Simple rectangle paths should be short (< 50 chars)
        # Complex octicons paths were > 200 chars
        assert len(d) < 80, \
            f"Glyph '{glyph.get('glyph-name')}' path is too complex ({len(d)} chars): {d[:60]}..."


# [pr_diff] fail_to_pass
def test_generated_font_compact():
    """The generated woff2 should be much smaller than the old octicons font."""
    woff2_path = WEBFONT_DIR / "iconfont.woff2"
    assert woff2_path.exists(), "iconfont.woff2 not found"
    size = woff2_path.stat().st_size
    # Old octicons-based font was ~2656 bytes
    # New rectangle-based font should be < 600 bytes
    assert size < 600, \
        f"Font file is {size} bytes — expected < 600 for simplified rectangle glyphs"
    assert size > 100, \
        f"Font file is {size} bytes — suspiciously small, may be corrupted"


# [pr_diff] fail_to_pass
def test_route_spec_font_size_updated():
    """route.spec.tsx must not reference the old font body.length of 2656."""
    spec_path = Path(REPO) / "tests" / "components" / "ct-react-vite" / "tests" / "route.spec.tsx"
    assert spec_path.exists(), "route.spec.tsx not found"
    content = spec_path.read_text()
    assert "2656" not in content, \
        "route.spec.tsx still references old font body.length of 2656 — must be updated"
    # The new font size should be referenced somewhere in the test expectations
    assert "toBe(" in content, "route.spec.tsx should still have body.length assertions"


# ---------------------------------------------------------------------------
# Config-edit (config_edit) — README documentation update
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass

    # Must mention the generation script
    assert "generate_font" in content, \
        "README should reference the generate_font.py script"

    # Must mention the key dependency
    assert "fonttools" in content.lower() or "fontTools" in content, \
        "README should document the fonttools dependency"

    # Must mention brotli (required for woff2 compression)
    assert "brotli" in content.lower(), \
        "README should document the brotli dependency"

    # Should describe what the font contains (rectangle/simple glyphs)
    content_lower = content.lower()
    assert "rectangle" in content_lower or "simple" in content_lower or "filled" in content_lower, \
        "README should describe the simplified glyph design (rectangles/simple shapes)"

    # Old README content should be gone
    assert "fontello" not in content_lower, \
        "README should no longer reference fontello (old generation tool)"
    assert "octicons" not in content_lower and "primer" not in content_lower, \
        "README should no longer reference octicons/primer (old icon source)"
