"""Behavioral checks for portfolio-add-clauderules-around-pdfextractors (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/portfolio")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/pdfextractors.md')
    assert '- Tests are located at `name.abuchen.portfolio.tests/src/name/abuchen/datatransfer/pdf/` within a folder for each bank, containing all connected test-exports.' in text, "expected to find: " + '- Tests are located at `name.abuchen.portfolio.tests/src/name/abuchen/datatransfer/pdf/` within a folder for each bank, containing all connected test-exports.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/pdfextractors.md')
    assert '- When implementing a new extractor or adding new parsing logic method, check `BaaderBankPDFExtractor` for reference and use the same pattern' in text, "expected to find: " + '- When implementing a new extractor or adding new parsing logic method, check `BaaderBankPDFExtractor` for reference and use the same pattern'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/pdfextractors.md')
    assert '- Add comment-blocks with `@formatter:off` and `@formatter:on` before each section-block showing the format that is handled there.' in text, "expected to find: " + '- Add comment-blocks with `@formatter:off` and `@formatter:on` before each section-block showing the format that is handled there.'[:80]

