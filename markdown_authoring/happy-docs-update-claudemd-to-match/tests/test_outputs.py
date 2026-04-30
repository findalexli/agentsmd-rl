"""Behavioral checks for happy-docs-update-claudemd-to-match (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/happy")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '3. **Add to ALL languages** - When adding new strings, you MUST add them to all language files in `sources/text/translations/` (currently: `en`, `ru`, `pl`, `es`, `ca`, `it`, `pt`, `ja`, `zh-Hans`)' in text, "expected to find: " + '3. **Add to ALL languages** - When adding new strings, you MUST add them to all language files in `sources/text/translations/` (currently: `en`, `ru`, `pl`, `es`, `ca`, `it`, `pt`, `ja`, `zh-Hans`)'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '6. **Platform-Specific Code**: Separate implementations for web vs native when needed' in text, "expected to find: " + '6. **Platform-Specific Code**: Separate implementations for web vs native when needed'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **libsodium** (via `@more-tech/react-native-libsodium`) for end-to-end encryption' in text, "expected to find: " + '- **libsodium** (via `@more-tech/react-native-libsodium`) for end-to-end encryption'[:80]

