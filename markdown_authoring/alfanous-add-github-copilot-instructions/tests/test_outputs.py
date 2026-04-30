"""Behavioral checks for alfanous-add-github-copilot-instructions (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/alfanous")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert "Alfanous is a search engine API for the Holy Qur'an that provides simple and advanced search capabilities. The project is written in Python and uses Whoosh for indexing and search functionality." in text, "expected to find: " + "Alfanous is a search engine API for the Holy Qur'an that provides simple and advanced search capabilities. The project is written in Python and uses Whoosh for indexing and search functionality."[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert "# perl -p -w -e 's|alfanous.release|$(VERSION)|g;s|alfanous.version|$(VERSION)|g;' src/alfanous/resources/information.json.in > src/alfanous/resources/information.json" in text, "expected to find: " + "# perl -p -w -e 's|alfanous.release|$(VERSION)|g;s|alfanous.version|$(VERSION)|g;' src/alfanous/resources/information.json.in > src/alfanous/resources/information.json"[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- Test files should match the module they test (e.g., `test_engines.py` for `engines.py`)' in text, "expected to find: " + '- Test files should match the module they test (e.g., `test_engines.py` for `engines.py`)'[:80]

