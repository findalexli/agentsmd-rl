"""Behavioral checks for claude-skills-refactor-skills-reference-bin-executables (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/claude-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/design-assets/skills/image-processing/SKILL.md')
    assert "**Generate a custom script when**: the operation needs logic `img-process` doesn't cover (compositing multiple images, watermarks, complex text layouts, conditional processing)." in text, "expected to find: " + "**Generate a custom script when**: the operation needs logic `img-process` doesn't cover (compositing multiple images, watermarks, complex text layouts, conditional processing)."[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/design-assets/skills/image-processing/SKILL.md')
    assert '**Use `img-process` when**: the operation is standard (resize, convert, trim, thumbnail, optimise, OG card, batch). This is faster and avoids generating a script each time.' in text, "expected to find: " + '**Use `img-process` when**: the operation is standard (resize, convert, trim, thumbnail, optimise, OG card, batch). This is faster and avoids generating a script each time.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/design-assets/skills/image-processing/SKILL.md')
    assert "Use `img-process` (shipped in `bin/`) for common operations. For complex or custom workflows, generate a Pillow script adapted to the user's environment." in text, "expected to find: " + "Use `img-process` (shipped in `bin/`) for common operations. For complex or custom workflows, generate a Pillow script adapted to the user's environment."[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/frontend/skills/product-showcase/SKILL.md')
    assert '**c. "How It Works" flow** — the main workflow in sequence. Run `capture-screenshots` multiple times with `--prefix workflow-step` as you navigate through the flow steps.' in text, "expected to find: " + '**c. "How It Works" flow** — the main workflow in sequence. Run `capture-screenshots` multiple times with `--prefix workflow-step` as you navigate through the flow steps.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/frontend/skills/product-showcase/SKILL.md')
    assert 'Use `capture-screenshots` (shipped in `bin/`) to capture the app. This is faster and more consistent than generating Playwright scripts each time.' in text, "expected to find: " + 'Use `capture-screenshots` (shipped in `bin/`) to capture the app. This is faster and more consistent than generating Playwright scripts each time.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/frontend/skills/product-showcase/SKILL.md')
    assert '**b. Features** — each major section. Use `--pages` with all nav paths. Capture 6-10 key screens that tell the product story.' in text, "expected to find: " + '**b. Features** — each major section. Use `--pages` with all nav paths. Capture 6-10 key screens that tell the product story.'[:80]

