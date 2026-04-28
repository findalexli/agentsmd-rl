"""Behavioral checks for couchers-merge-cursorrules-into-claudemd-and (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/couchers")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursorrules')
    assert '.cursorrules' in text, "expected to find: " + '.cursorrules'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- For dates and times on the web frontend, never use `Date.toLocaleDateString()` or `Intl.DateTimeFormat` directly - use the helpers in `app/web/utils/date.ts` (`localizeDateTime`, `localizeDateTimeRa' in text, "expected to find: " + '- For dates and times on the web frontend, never use `Date.toLocaleDateString()` or `Intl.DateTimeFormat` directly - use the helpers in `app/web/utils/date.ts` (`localizeDateTime`, `localizeDateTimeRa'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- Query elements by label (`getByLabelText`) for accessibility. When there\'s ambiguity (e.g., both a label and aria-label), use the `selector` option: `getByLabelText(label, { selector: "textarea" })`' in text, "expected to find: " + '- Query elements by label (`getByLabelText`) for accessibility. When there\'s ambiguity (e.g., both a label and aria-label), use the `selector` option: `getByLabelText(label, { selector: "textarea" })`'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- Use the `<Trans>` component for text with embedded components (like links). Make sure components in the translation JSON match the `components` prop exactly' in text, "expected to find: " + '- Use the `<Trans>` component for text with embedded components (like links). Make sure components in the translation JSON match the `components` prop exactly'[:80]

