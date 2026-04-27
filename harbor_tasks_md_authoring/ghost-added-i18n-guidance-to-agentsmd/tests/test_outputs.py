"""Behavioral checks for ghost-added-i18n-guidance-to-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/ghost")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '`yarn translate` is run as part of `yarn workspace @tryghost/i18n test`. In CI, it fails if translation keys or `context.json` are out of date (`failOnUpdate: process.env.CI`). Always run `yarn transl' in text, "expected to find: " + '`yarn translate` is run as part of `yarn workspace @tryghost/i18n test`. In CI, it fails if translation keys or `context.json` are out of date (`failOnUpdate: process.env.CI`). Always run `yarn transl'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '1. **Never split sentences across multiple `t()` calls.** Translators cannot reorder words across separate keys. Instead, use `@doist/react-interpolate` to embed React elements (links, bold, etc.) wit' in text, "expected to find: " + '1. **Never split sentences across multiple `t()` calls.** Translators cannot reorder words across separate keys. Instead, use `@doist/react-interpolate` to embed React elements (links, bold, etc.) wit'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '2. **Always provide context descriptions.** When adding a new key, add a description in `context.json` explaining where the string appears and what it does. CI will reject empty descriptions.' in text, "expected to find: " + '2. **Always provide context descriptions.** When adding a new key, add a description in `context.json` explaining where the string appears and what it does. CI will reject empty descriptions.'[:80]

