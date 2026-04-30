"""Behavioral checks for cli-docslarkdrive-add-missing-import-command (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/cli")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lark-drive/references/lark-drive-import.md')
    assert 'lark-cli drive +import --file ./report.docx --type docx' in text, "expected to find: " + 'lark-cli drive +import --file ./report.docx --type docx'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lark-drive/references/lark-drive-import.md')
    assert 'lark-cli drive +import --file ./legacy.xls --type sheet' in text, "expected to find: " + 'lark-cli drive +import --file ./legacy.xls --type sheet'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/lark-drive/references/lark-drive-import.md')
    assert 'lark-cli drive +import --file ./legacy.doc --type docx' in text, "expected to find: " + 'lark-cli drive +import --file ./legacy.doc --type docx'[:80]

