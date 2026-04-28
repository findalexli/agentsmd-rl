"""Behavioral checks for fighthealthinsurance-add-a-claudemd-file-for (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/fighthealthinsurance")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Fight Health Insurance is a Django application that helps patients appeal health insurance denials. It combines a web interface with ML model integration to generate persuasive appeal letters. The sys' in text, "expected to find: " + 'Fight Health Insurance is a Django application that helps patients appeal health insurance denials. It combines a web interface with ML model integration to generate persuasive appeal letters. The sys'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'Django uses `django-configurations` with classes: Dev, TestSync, Test, TestActor, Prod. Set via `DJANGO_CONFIGURATION` env var.' in text, "expected to find: " + 'Django uses `django-configurations` with classes: Dev, TestSync, Test, TestActor, Prod. Set via `DJANGO_CONFIGURATION` env var.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- Webpack bundler; to rebuild, run `npm run build` from the `fighthealthinsurance/static/js/` directory' in text, "expected to find: " + '- Webpack bundler; to rebuild, run `npm run build` from the `fighthealthinsurance/static/js/` directory'[:80]

