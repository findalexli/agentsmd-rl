"""Behavioral checks for ente-mobphotos-add-claudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/ente")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('mobile/apps/photos/CLAUDE.md')
    assert "Ente is focused on privacy, transparency and trust. It's a fully open-source, end-to-end encrypted platform for storing data in the cloud. When contributing, always prioritize:" in text, "expected to find: " + "Ente is focused on privacy, transparency and trust. It's a fully open-source, end-to-end encrypted platform for storing data in the cloud. When contributing, always prioritize:"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('mobile/apps/photos/CLAUDE.md')
    assert '- **Photos-specific plugins** (`./plugins/`): Custom Flutter plugins specific to Photos app for separation and testability' in text, "expected to find: " + '- **Photos-specific plugins** (`./plugins/`): Custom Flutter plugins specific to Photos app for separation and testability'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('mobile/apps/photos/CLAUDE.md')
    assert '- When adding functionality, check both `../../packages/` for shared code and `./plugins/` for Photos-specific plugins' in text, "expected to find: " + '- When adding functionality, check both `../../packages/` for shared code and `./plugins/` for Photos-specific plugins'[:80]

