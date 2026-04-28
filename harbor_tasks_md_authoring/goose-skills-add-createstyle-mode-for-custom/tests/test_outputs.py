"""Behavioral checks for goose-skills-add-createstyle-mode-for-custom (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/goose-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/composites/goose-graphics/SKILL.md')
    assert '- **Create custom style** — `/goose-graphics --create-style --ref <image>` runs only the style extraction workflow from `styles/extract-style.md`. Analyzes the reference image, maps fonts to Google Fo' in text, "expected to find: " + '- **Create custom style** — `/goose-graphics --create-style --ref <image>` runs only the style extraction workflow from `styles/extract-style.md`. Analyzes the reference image, maps fonts to Google Fo'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/composites/goose-graphics/SKILL.md')
    assert 'The user may also say: **"I have a reference image"** — in that case, read `styles/extract-style.md` and follow its workflow to derive a custom style in slim format from the provided image. The extrac' in text, "expected to find: " + 'The user may also say: **"I have a reference image"** — in that case, read `styles/extract-style.md` and follow its workflow to derive a custom style in slim format from the provided image. The extrac'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/composites/goose-graphics/SKILL.md')
    assert '4. **`--create-style` present** → read `styles/extract-style.md` and follow its workflow. Skip §6 (Discover Intent), §7 (Select Style preset list), §8-§12. The extract-style workflow handles everythin' in text, "expected to find: " + '4. **`--create-style` present** → read `styles/extract-style.md` and follow its workflow. Skip §6 (Discover Intent), §7 (Select Style preset list), §8-§12. The extract-style workflow handles everythin'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/composites/goose-graphics/styles/extract-style.md')
    assert 'The output MUST be in the slim preset format (Palette → Typography → Layout → Do/Don\'t → CSS snippets). Do NOT generate the verbose 9-section DESIGN.md format with sections like "Visual Theme & Atmosp' in text, "expected to find: " + 'The output MUST be in the slim preset format (Palette → Typography → Layout → Do/Don\'t → CSS snippets). Do NOT generate the verbose 9-section DESIGN.md format with sections like "Visual Theme & Atmosp'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/composites/goose-graphics/styles/extract-style.md')
    assert 'The user provides a reference image — a screenshot, design mockup, mood board, website capture, or any visual reference — and wants to capture its design language as a reusable style preset. The outpu' in text, "expected to find: " + 'The user provides a reference image — a screenshot, design mockup, mood board, website capture, or any visual reference — and wants to capture its design language as a reusable style preset. The outpu'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/composites/goose-graphics/styles/extract-style.md')
    assert "A `:root` variables block defining all CSS custom properties, followed by 4-5 self-contained component patterns as inline-styled HTML blocks. Each component must use the style's colors, fonts, and spa" in text, "expected to find: " + "A `:root` variables block defining all CSS custom properties, followed by 4-5 self-contained component patterns as inline-styled HTML blocks. Each component must use the style's colors, fonts, and spa"[:80]

