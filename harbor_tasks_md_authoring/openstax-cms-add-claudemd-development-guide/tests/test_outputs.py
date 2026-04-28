"""Behavioral checks for openstax-cms-add-claudemd-development-guide (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/openstax-cms")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert "**Solution**: This is expected in local development. The error occurs because production uses SES for email, but local development doesn't need it. Your `local.py` file should already handle this, but" in text, "expected to find: " + "**Solution**: This is expected in local development. The error occurs because production uses SES for email, but local development doesn't need it. Your `local.py` file should already handle this, but"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'OpenStax CMS is a content management system built with **Wagtail CMS** on top of **Django Framework**. It manages content for openstax.org including books, pages, news, and various marketing pages.' in text, "expected to find: " + 'OpenStax CMS is a content management system built with **Wagtail CMS** on top of **Django Framework**. It manages content for openstax.org including books, pages, news, and various marketing pages.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '3. **Create local settings file** (REQUIRED before migrations) (cp openstax/settings/local.py.example openstax/settings.local.py)' in text, "expected to find: " + '3. **Create local settings file** (REQUIRED before migrations) (cp openstax/settings/local.py.example openstax/settings.local.py)'[:80]

