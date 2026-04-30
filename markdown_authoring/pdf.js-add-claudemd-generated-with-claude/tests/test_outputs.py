"""Behavioral checks for pdf.js-add-claudemd-generated-with-claude (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/pdf.js")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "PDF.js is a Portable Document Format (PDF) viewer built with JavaScript, HTML5 Canvas, and CSS. It's a Mozilla project that provides a general-purpose, web standards-based platform for parsing and ren" in text, "expected to find: " + "PDF.js is a Portable Document Format (PDF) viewer built with JavaScript, HTML5 Canvas, and CSS. It's a Mozilla project that provides a general-purpose, web standards-based platform for parsing and ren"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Then open http://localhost:8888/web/viewer.html to view the PDF viewer. Test PDFs are available at http://localhost:8888/test/pdfs/?frame' in text, "expected to find: " + 'Then open http://localhost:8888/web/viewer.html to view the PDF viewer. Test PDFs are available at http://localhost:8888/test/pdfs/?frame'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Font handling**: CFF, TrueType, Type1 font parsing and conversion (`font.js`, `fonts.js`, `cff_*.js`, `type1_*.js`)' in text, "expected to find: " + '- **Font handling**: CFF, TrueType, Type1 font parsing and conversion (`font.js`, `fonts.js`, `cff_*.js`, `type1_*.js`)'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'CLAUDE.md' in text, "expected to find: " + 'CLAUDE.md'[:80]

