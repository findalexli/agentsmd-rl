"""Behavioral checks for mnelab-add-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/mnelab")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Every PR must include an entry in the `[UNRELEASED]` section of [CHANGELOG.md](CHANGELOG.md). Add it under the appropriate subsection (`### ✨ Added`, `### 🔧 Fixed`, `### 🌀 Changed`, or `### 🗑️ Removed' in text, "expected to find: " + 'Every PR must include an entry in the `[UNRELEASED]` section of [CHANGELOG.md](CHANGELOG.md). Add it under the appropriate subsection (`### ✨ Added`, `### 🔧 Fixed`, `### 🌀 Changed`, or `### 🗑️ Removed'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Docstrings follow [NumPy style](https://numpydoc.readthedocs.io/en/latest/format.html), but use standard Markdown syntax instead of reStructuredText. In particular, inline code uses single backticks' in text, "expected to find: " + '- Docstrings follow [NumPy style](https://numpydoc.readthedocs.io/en/latest/format.html), but use standard Markdown syntax instead of reStructuredText. In particular, inline code uses single backticks'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Add support for XYZ ([#123](https://github.com/cbrnr/mnelab/pull/123) by [Your Name](https://github.com/yourname))' in text, "expected to find: " + '- Add support for XYZ ([#123](https://github.com/cbrnr/mnelab/pull/123) by [Your Name](https://github.com/yourname))'[:80]

