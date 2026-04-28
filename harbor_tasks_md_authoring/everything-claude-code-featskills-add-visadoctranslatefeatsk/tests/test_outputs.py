"""Behavioral checks for everything-claude-code-featskills-add-visadoctranslatefeatsk (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/everything-claude-code")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/visa-doc-translate/README.md')
    assert 'Automatically translate visa application documents from images to professional English PDFs.' in text, "expected to find: " + 'Automatically translate visa application documents from images to professional English PDFs.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/visa-doc-translate/README.md')
    assert '- 🔄 **Automatic OCR**: Tries multiple OCR methods (macOS Vision, EasyOCR, Tesseract)' in text, "expected to find: " + '- 🔄 **Automatic OCR**: Tries multiple OCR methods (macOS Vision, EasyOCR, Tesseract)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/visa-doc-translate/README.md')
    assert '- 📄 **Bilingual PDF**: Original image + professional English translation' in text, "expected to find: " + '- 📄 **Bilingual PDF**: Original image + professional English translation'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/visa-doc-translate/SKILL.md')
    assert 'description: Translate visa application documents (images) to English and create a bilingual PDF with original and translation' in text, "expected to find: " + 'description: Translate visa application documents (images) to English and create a bilingual PDF with original and translation'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/visa-doc-translate/SKILL.md')
    assert 'When the user provides an image file path, AUTOMATICALLY execute the following steps WITHOUT asking for confirmation:' in text, "expected to find: " + 'When the user provides an image file path, AUTOMATICALLY execute the following steps WITHOUT asking for confirmation:'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/visa-doc-translate/SKILL.md')
    assert '1. **Image Conversion**: If the file is HEIC, convert it to PNG using `sips -s format png <input> --out <output>`' in text, "expected to find: " + '1. **Image Conversion**: If the file is HEIC, convert it to PNG using `sips -s format png <input> --out <output>`'[:80]

